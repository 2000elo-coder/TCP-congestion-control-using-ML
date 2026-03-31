import os
import numpy as np
import pandas as pd
import gymnasium as gym
from gymnasium import spaces
from stable_baselines3 import PPO
from stable_baselines3.common.env_checker import check_env
from stable_baselines3.common.vec_env import DummyVecEnv
import matplotlib.pyplot as plt


# ── 1. LOAD DATASET ──────────────────────────────────────────────────
def load_dataset(data_dir):
    algo_names = [
        "bbr","bic","cdg","cubic","dctcp","highspeed","htcp","hybla",
        "illinois","lp","nv","reno","scalable","vegas","veno","westwood","yeah"
    ]

    traces = {}
    total  = 0

    for name in algo_names:
        algo_folder = os.path.join(data_dir, name)
        if not os.path.isdir(algo_folder):
            print(f"  Folder not found, skipping: {algo_folder}")
            continue

        algo_traces = []
        for i in range(1, 51):
            path = os.path.join(algo_folder, f"{name}{i}.log")
            if not os.path.exists(path):
                path = os.path.join(algo_folder, f"{name}{i}.log.csv")
            if not os.path.exists(path):
                continue

            try:
                df = pd.read_csv(path, sep=";")
                df.columns = df.columns.str.strip()
                df = df.dropna(axis=1, how="all")
                df.columns = df.columns.str.strip()

                for col in ["bytes_retrans", "bytes_sent", "bytes_acked",
                            "segs_out", "delivered", "ssthresh", "rtt", "cwnd"]:
                    if col not in df.columns:
                        df[col] = 0

                df = df.dropna(subset=["cwnd", "rtt"])
                df = df.reset_index(drop=True)

                if len(df) < 10:
                    continue

                algo_traces.append(df)

            except Exception as e:
                print(f"  Could not read {path}: {e}")
                continue

        if algo_traces:
            traces[name] = algo_traces
            total += len(algo_traces)
            print(f"  {name:12s}: {len(algo_traces)} files loaded")
        else:
            print(f"  {name:12s}: no files found")

    print(f"\nTotal traces loaded: {total} across {len(traces)} algorithms\n")
    return traces


# COMPUTE GLOBAL CWND STATS FOR NORMALIZATION 
def compute_cwnd_stats(traces):
    all_cwnds = []
    for algo_traces in traces.values():
        for df in algo_traces:
            all_cwnds.extend(df["cwnd"].tolist())
    arr = np.array(all_cwnds)
    return float(arr.mean()), float(arr.std() + 1e-6), float(arr.min()), float(arr.max())


# 3. ENVIRONMENT 
class TCPCongestionEnv(gym.Env):
    """
    State:  [rtt_norm, ssthresh_norm, retrans_rate, delivery_rate, cwnd_norm]
    Action: [-1, 1] mapped to [cwnd_min, cwnd_max]  (SB3 recommended range)
    Reward: heavily penalises deviation from real cwnd + throughput bonus
    """

    def __init__(self, traces, cwnd_min, cwnd_max):
        super().__init__()
        self.traces   = traces
        self.algo_list = list(traces.keys())
        self.cwnd_min  = cwnd_min
        self.cwnd_max  = cwnd_max

        
        self.action_space = spaces.Box(
            low=-1.0, high=1.0, shape=(1,), dtype=np.float32
        )
        self.observation_space = spaces.Box(
            low=0.0, high=1.0, shape=(5,), dtype=np.float32
        )

        self.df           = None
        self.step_idx     = 0
        self.current_cwnd = cwnd_min
        self.current_algo = None

    def _scale_action(self, action):
        # map [-1, 1] → [cwnd_min, cwnd_max]
        return (float(action[0]) + 1.0) / 2.0 * (self.cwnd_max - self.cwnd_min) + self.cwnd_min

    def _get_obs(self, row):
        rtt      = float(np.clip(row["rtt"]      / 250.0, 0, 1))
        ssthresh = float(np.clip(row["ssthresh"] / 60.0,  0, 1))
        retrans  = float(np.clip(
            row["bytes_retrans"] / (row["bytes_sent"] + 1), 0, 1))
        delivery = float(np.clip(
            row["delivered"] / (row["segs_out"] + 1), 0, 1))
        cwnd_n   = float(np.clip(
            (self.current_cwnd - self.cwnd_min) / (self.cwnd_max - self.cwnd_min), 0, 1))
        return np.array([rtt, ssthresh, retrans, delivery, cwnd_n], dtype=np.float32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.current_algo = np.random.choice(self.algo_list)
        algo_traces       = self.traces[self.current_algo]
        self.df           = algo_traces[np.random.randint(len(algo_traces))]
        self.step_idx     = 0
        self.current_cwnd = float(self.df.iloc[0]["cwnd"])
        return self._get_obs(self.df.iloc[0]), {}

    def step(self, action):
        new_cwnd  = self._scale_action(action)
        row       = self.df.iloc[self.step_idx]
        real_cwnd = float(row["cwnd"])

        # Reward components

        # 1. Tracking reward: how close is agent cwnd to real cwnd?
        #    This is the PRIMARY signal — forces agent to learn real behaviour
        cwnd_range   = self.cwnd_max - self.cwnd_min
        tracking_err = abs(new_cwnd - real_cwnd) / cwnd_range   # 0=perfect, 1=worst (More experiments needed)
        tracking_reward = 1.0 - tracking_err                     # 0 to 1

        # 2. Throughput bonus: reward higher cwnd when real algo also uses it
        #    (agent learns: big cwnd is good when the network supports it)
        cwnd_norm    = (real_cwnd - self.cwnd_min) / cwnd_range
        throughput_bonus = 0.3 * cwnd_norm

        # 3. Loss penalty: punish retransmissions
        loss_penalty = float(np.clip(
            row["bytes_retrans"] / (row["bytes_sent"] + 1), 0, 1))

        # 4. RTT penalty: mild — high RTT is bad but not as bad as loss
        rtt_penalty = 0.2 * float(np.clip(row["rtt"] / 250.0, 0, 1))

        reward = (
              2.0 * tracking_reward    # strong: track real cwnd closely
            + throughput_bonus         # mild:   prefer higher cwnd when appropriate
            - 0.5 * loss_penalty       # mild:   avoid retransmissions
            - rtt_penalty              # mild:   avoid high RTT
        )

        self.current_cwnd  = new_cwnd
        self.step_idx     += 1
        done = self.step_idx >= len(self.df) - 1

        next_idx = -1 if done else self.step_idx
        obs = self._get_obs(self.df.iloc[next_idx])

        return obs, float(reward), done, False, {
            "algo":      self.current_algo,
            "real_cwnd": real_cwnd,
            "rl_cwnd":   new_cwnd,
        }


# 4. TRAIN The NN
def train(traces, cwnd_min, cwnd_max, total_timesteps=1_000_000):
    env = TCPCongestionEnv(traces, cwnd_min, cwnd_max)
    check_env(env, warn=True)

    model = PPO(
        "MlpPolicy",
        env,
        verbose=1,
        learning_rate=3e-4,
        n_steps=2048,
        batch_size=64,
        n_epochs=10,
        gamma=0.99,
        ent_coef=0.05,          # higher the entropy == more is the  exploration ???
        clip_range=0.2,
        policy_kwargs=dict(net_arch=[256, 256]),   
    )

    model.learn(total_timesteps=total_timesteps)
    model.save("tcp_rl_agent")
    print("\nModel saved → tcp_rl_agent.zip")
    return model


# 5. EVALUATE
def evaluate(model, traces, cwnd_min, cwnd_max):
    print("\nEvaluating agent against all algorithms...\n")
    results = {}

    for algo, algo_traces in traces.items():
        all_rewards    = []
        all_real_cwnds = []
        all_rl_cwnds   = []

        for df in algo_traces:
            current_cwnd = float(df.iloc[0]["cwnd"])
            obs = np.array([
                np.clip(df.iloc[0]["rtt"]      / 250.0, 0, 1),
                np.clip(df.iloc[0]["ssthresh"] / 60.0,  0, 1),
                0.0,
                1.0,
                np.clip((current_cwnd - cwnd_min) / (cwnd_max - cwnd_min), 0, 1),
            ], dtype=np.float32)

            rewards, real_cwnds, rl_cwnds = [], [], []

            for i in range(len(df) - 1):
                action, _ = model.predict(obs, deterministic=True)
                # scale [-1,1] → [cwnd_min, cwnd_max]
                new_cwnd  = (float(action[0]) + 1.0) / 2.0 * (cwnd_max - cwnd_min) + cwnd_min
                row       = df.iloc[i]
                real_cwnd = float(row["cwnd"])

                cwnd_range   = cwnd_max - cwnd_min
                tracking_err = abs(new_cwnd - real_cwnd) / cwnd_range
                tracking_r   = 1.0 - tracking_err
                cwnd_norm    = (real_cwnd - cwnd_min) / cwnd_range
                loss_penalty = float(np.clip(
                    row["bytes_retrans"] / (row["bytes_sent"] + 1), 0, 1))
                rtt_penalty  = 0.2 * float(np.clip(row["rtt"] / 250.0, 0, 1))

                r = 2.0*tracking_r + 0.3*cwnd_norm - 0.5*loss_penalty - rtt_penalty
                rewards.append(r)
                real_cwnds.append(real_cwnd)
                rl_cwnds.append(new_cwnd)

                next_row = df.iloc[i + 1]
                obs = np.array([
                    np.clip(next_row["rtt"]      / 250.0, 0, 1),
                    np.clip(next_row["ssthresh"] / 60.0,  0, 1),
                    np.clip(next_row["bytes_retrans"] / (next_row["bytes_sent"] + 1), 0, 1),
                    np.clip(next_row["delivered"]     / (next_row["segs_out"]   + 1), 0, 1),
                    np.clip((new_cwnd - cwnd_min) / (cwnd_max - cwnd_min), 0, 1),
                ], dtype=np.float32)
                current_cwnd = new_cwnd

            all_rewards.append(np.mean(rewards))
            all_real_cwnds.extend(real_cwnds)
            all_rl_cwnds.extend(rl_cwnds)

        results[algo] = {
            "avg_reward":  float(np.mean(all_rewards)),
            "runs":        len(algo_traces),
            "real_cwnds":  np.array(all_real_cwnds),
            "rl_cwnds":    np.array(all_rl_cwnds),
        }

    return results


# 6. PRINTING SUMMARY AND RESULTs
def print_summary(results):
    print("── Per-algorithm results ────────────────────────────────────")
    print(f"  {'algo':12s}  {'reward':>8s}  {'real_cwnd':>10s}  {'rl_cwnd':>8s}  {'diff':>6s}  runs")
    print("  " + "-"*62)
    for algo, r in sorted(results.items(), key=lambda x: -x[1]["avg_reward"]):
        real_mean = float(np.mean(r["real_cwnds"]))
        rl_mean   = float(np.mean(r["rl_cwnds"]))
        diff      = rl_mean - real_mean
        print(
            f"  {algo:12s}  {r['avg_reward']:>8.4f}  "
            f"{real_mean:>10.2f}  {rl_mean:>8.2f}  "
            f"{diff:>+6.2f}  {r['runs']}"
        )


# 7. PLOTTING the results
def plot_results(results):
    algos = list(results.keys())

    #  cwnd traces 
    cols = 3
    rows = (len(algos) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(18, rows * 4))
    axes = axes.flatten()

    for i, algo in enumerate(algos):
        r  = results[algo]
        ax = axes[i]
        n  = min(3600, len(r["real_cwnds"]))

        ax.plot(range(n), r["real_cwnds"][:n],
                color="#378ADD", lw=1.2, label=f"Real ({algo})")
        ax.plot(range(n), r["rl_cwnds"][:n],
                color="#D85A30", lw=1.2, linestyle="--", label="RL agent")
        ax.set_title(f"{algo}  |  reward: {r['avg_reward']:.3f}", fontsize=9)
        ax.set_xlabel("Step", fontsize=8)
        ax.set_ylabel("cwnd", fontsize=8)
        ax.legend(fontsize=7)

    for j in range(i + 1, len(axes)):
        axes[j].set_visible(False)

    plt.suptitle("RL Agent cwnd vs Real cwnd — all algorithms", fontsize=13)
    plt.tight_layout()
    plt.savefig("rl_vs_baselines.png", dpi=150, bbox_inches="tight")
    print("Saved → rl_vs_baselines.png")

    #  reward bar chart 
    fig2, ax2 = plt.subplots(figsize=(14, 5))
    rewards = [results[a]["avg_reward"] for a in algos]
    colors  = ["#1D9E75" if r == max(rewards) else "#378ADD" for r in rewards]
    ax2.bar(algos, rewards, color=colors, edgecolor="none")
    ax2.axhline(max(rewards), color="#D85A30", linestyle="--", lw=1,
                label=f"Best: {max(rewards):.3f}")
    ax2.set_title("Average reward per algorithm")
    ax2.set_ylabel("Avg reward")
    ax2.legend()
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.savefig("reward_comparison.png", dpi=150)
    print("Saved → reward_comparison.png")

    #  mean cwnd comparison 
    fig3, ax3 = plt.subplots(figsize=(14, 5))
    real_means = [float(np.mean(results[a]["real_cwnds"])) for a in algos]
    rl_means   = [float(np.mean(results[a]["rl_cwnds"]))   for a in algos]
    x = np.arange(len(algos))
    w = 0.35
    ax3.bar(x - w/2, real_means, w, label="Real algorithm",
            color="#378ADD", edgecolor="none")
    ax3.bar(x + w/2, rl_means,   w, label="RL agent",
            color="#D85A30", edgecolor="none")
    ax3.set_xticks(x)
    ax3.set_xticklabels(algos, rotation=45, ha="right")
    ax3.set_ylabel("Mean cwnd")
    ax3.set_title("Mean cwnd: RL agent vs real algorithm")
    ax3.legend()
    plt.tight_layout()
    plt.savefig("cwnd_comparison.png", dpi=150)
    print("Saved → cwnd_comparison.png")

    plt.show()


# 8. MAIN 
if __name__ == "__main__":

    DATA_DIR = r"C:\Users\Rajat sharma\Desktop\major\dataset\10894768\tcp-dataset"

    print("Loading dataset...")
    traces = load_dataset(DATA_DIR)

    print("Computing cwnd range across all traces...")
    _, _, cwnd_min, cwnd_max = compute_cwnd_stats(traces)
    cwnd_min = max(2.0, cwnd_min)
    print(f"  cwnd range: {cwnd_min:.1f} → {cwnd_max:.1f}\n")

    print("Training agent...")
    model = train(traces, cwnd_min, cwnd_max, total_timesteps=1_000_000)

    print("Evaluating...")
    results = evaluate(model, traces, cwnd_min, cwnd_max)

    print_summary(results)
    plot_results(results)