# TCP Congestion Control Using ML

**NS-3 Setup, Installation & RL Model Guide**

> VirtualBox + Ubuntu 24.04 LTS + NS-3.42 + PPO Agent

---

## 1. VirtualBox Installation

### 1.1 System Requirements

- Windows 10 or Windows 11 (64-bit)
- Minimum 8 GB RAM (16 GB recommended)
- Minimum 50 GB free disk space
- CPU with virtualization support (Intel VT-x or AMD-V)
- Virtualization must be enabled in BIOS/UEFI settings

### 1.2 Download and Install VirtualBox

1. Open your browser and go to: https://www.virtualbox.org/wiki/Downloads
2. Click "Windows hosts" to download the VirtualBox installer (.exe file)
3. Run the downloaded installer as Administrator
4. Click Next through all installation steps and accept default settings
5. Click Install and wait for the installation to complete
6. Click Finish to launch VirtualBox

### 1.3 Configure VirtualBox Settings

7. Open VirtualBox and go to **File > Preferences > General**
8. Set the Default Machine Folder to a drive with sufficient space (e.g., `D:\VMs`)
9. Click OK to save settings

---

## 2. Ubuntu 24.04 LTS Installation

### 2.1 Download Ubuntu ISO

10. Go to https://ubuntu.com/download/desktop
11. Download Ubuntu 24.04 LTS (.iso file, approximately 5 GB)
12. Save the ISO file to a known location on your Windows PC

### 2.2 Create a New Virtual Machine

13. Open VirtualBox and click the "New" button
14. Enter Name: `Ubuntu NS3`, set Type to `Linux`, Version to `Ubuntu (64-bit)`
15. Set Base Memory to **6144 MB (6 GB)** — recommended for NS-3 builds
16. Set Processors to **2 CPUs** if your machine has 4 or more cores
17. Create a Virtual Hard Disk with at least **40 GB** storage
18. Click Finish to create the VM

### 2.3 Configure VM Settings

19. Select your VM and click **Settings**
20. Go to **System > Processor** and check Enable PAE/NX
21. Go to **Display > Screen** and set Video Memory to 128 MB
22. Go to **Network > Adapter 1** and ensure it is set to NAT
23. Go to **Storage > Empty optical drive**, click the disc icon, and select your Ubuntu ISO
24. Click OK to save all settings

### 2.4 Install Ubuntu

25. Click Start to boot the VM from the Ubuntu ISO
26. Select "Try or Install Ubuntu" from the boot menu
27. Click "Install Ubuntu" on the welcome screen
28. Select keyboard layout and click Next
29. Choose "Normal Installation" and check both download options
30. Select "Erase disk and install Ubuntu" (safe inside VM)
31. Set your username, computer name, and password
32. Click Install and wait for installation to complete (10–20 minutes)
33. Click Restart Now and press Enter when prompted to remove the ISO

---

## 3. NS-3 Setup and Installation

### 3.1 System Update

Open a terminal (`Ctrl + Alt + T`) and run:

```bash
sudo apt update && sudo apt upgrade -y
```

### 3.2 Create Swap Space

NS-3 build requires significant memory. Create a 4 GB swap file to prevent build failures:

```bash
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

Verify swap is active:

```bash
free -h
```

> Swap should show `4.0Gi`.

### 3.3 Install Required Libraries

Install each dependency one by one:

```bash
sudo apt install -y build-essential autoconf automake python3 python3-dev python3-pip
sudo apt install -y cmake ninja-build git libboost-all-dev libssl-dev
sudo apt install -y libsqlite3-dev libxml2-dev libgsl-dev
sudo apt install -y qtbase5-dev qt5-qmake qtbase5-dev-tools
sudo apt install -y openmpi-bin libopenmpi-dev
sudo apt install -y gir1.2-goocanvas-2.0 python3-gi python3-pygraphviz
sudo apt install -y wireshark tcpdump
```

> **Note:** The package `python3-gi-cairo` may not be available on Ubuntu 24.04. This is safe to skip — it only affects optional graphical animation features and does not impact simulations.

### 3.4 Download NS-3.42

Download the NS-3.42 archive from your browser:

```
http://www.nsnam.org/releases/ns-allinone-3.42.tar.bz2
```

Save the file to your Ubuntu Downloads folder. Verify the file size is approximately 44–46 MB:

```bash
ls -lh ~/Downloads/ns-allinone-3.42.tar.bz2
```

### 3.5 Extract NS-3

```bash
tar -xjvf ~/Downloads/ns-allinone-3.42.tar.bz2 -C ~/Downloads/
cd ~/Downloads/ns-allinone-3.42/ns-3.42
```

Confirm you are in the right folder:

```bash
ls
```

> You should see a file called `ns3` in the list.

### 3.6 Configure NS-3

```bash
./ns3 configure --enable-examples --enable-tests
```

> **Expected output:** `'Configuring done'` and `'Generating done'` at the end confirms successful configuration. Takes approximately 2–5 minutes.

### 3.7 Build NS-3

```bash
./ns3 build -- -j1
```

> **Important:** The `-j1` flag limits the build to one parallel job to prevent out-of-memory crashes on systems with limited RAM. This build takes approximately **40–60 minutes**. Do NOT close the terminal or shut down the VM during this process.

### 3.8 Verify Installation

Run the hello simulator to confirm NS-3 is working:

```bash
./ns3 run hello-simulator
```

**Expected output:**

```
Hello Simulator
```

NS-3 is successfully installed and ready to use.

---

## 4. Troubleshooting Common Issues

| Problem | Cause | Fix |
|---|---|---|
| Build killed during compilation | RAM and swap exhausted | Increase swap to 8 GB, close all other apps before building |
| SSL error during wget download | Outdated certificates or restricted network | Download manually on Windows and transfer via Shared Folder |
| tar extraction error: not recoverable | Corrupted or incomplete download | Delete file, re-download, verify size is ~44–46 MB |
| Unknown option error during configure | Typo in command | Re-type command carefully, use `--enable-examples` |
| Swap showing 0B after reboot | Swap not made permanent | Run the `echo '/swapfile...' fstab` command again |
| python3-gi-cairo not found | Package renamed in Ubuntu 24.04 | Skip it — not required for simulations |

---

## 5. Important Folder Structure

```
~/Downloads/ns-allinone-3.42/ns-3.42/
├── scratch/             <- Place your custom simulation scripts here
├── src/internet/model/  <- NS-3 TCP source code
├── examples/tcp/        <- Built-in TCP example scripts
├── build/               <- Compiled build output
├── ns3                  <- NS-3 build tool (run commands from here)
└── CMakeLists.txt       <- Build configuration
```

---

## 6. Running Your First TCP Simulation

Navigate to the NS-3 folder:

```bash
cd ~/Downloads/ns-allinone-3.42/ns-3.42
```

Run a built-in TCP example:

```bash
./ns3 run tcp-bulk-send
```

Write your own simulation script:

```bash
gedit scratch/my-tcp-sim.cc
```

Build and run your script:

```bash
./ns3 build
./ns3 run my-tcp-sim
```

---

## 7. RL Model — TCP Congestion Control Agent

This section describes how to build, train, and evaluate a Reinforcement Learning agent that learns to control TCP's congestion window (cwnd) by studying real network traces collected from NS-3 simulations. The agent is trained using **PPO (Proximal Policy Optimization)** and evaluated against all 17 baseline TCP algorithms.

### 7.1 Overview

The RL agent replaces the fixed cwnd update rules of classical TCP algorithms (CUBIC, BBR, Vegas, etc.) with a neural network policy that observes the current network state and outputs an optimal cwnd value. Because it is trained on traces from all 17 algorithms simultaneously, it learns a generalised policy that adapts to a wide range of network conditions.

| Component | Description |
|---|---|
| State (input) | 5 normalised features: RTT, ssthresh, loss rate, delivery rate, current cwnd |
| Action (output) | New cwnd value — one continuous number |
| Algorithm | PPO (Proximal Policy Optimization) via Stable-Baselines3 |
| Neural network | MLP with 2 hidden layers of 256 neurons each |
| Training data | 17 algorithm folders × up to 50 CSV files = up to 850 traces |
| Training steps | 1,000,000 environment steps (~20–40 minutes on CPU) |

### 7.2 Install Python Dependencies

Install the required Python libraries in your environment (Windows or Ubuntu):

```bash
pip install stable-baselines3 gymnasium pandas numpy matplotlib
```

### 7.3 Dataset Structure

The dataset must be organised as one folder per algorithm, with each folder containing numbered `.log` CSV files:

```
tcp-dataset/
├── bbr/
│   ├── bbr1.log
│   ├── bbr2.log
│   └── ... (up to bbr50.log)
├── cubic/
│   ├── cubic1.log
│   └── ...
└── yeah/
    └── ...
```

Each `.log` file is a semicolon-separated CSV with the following key columns:

| Column | Meaning |
|---|---|
| cwnd | Congestion window — the key metric the agent learns to control |
| rtt | Round-trip time in milliseconds |
| ssthresh | Slow-start threshold — boundary between slow-start and congestion avoidance |
| bytes_sent | Cumulative bytes sent since connection opened |
| bytes_retrans | Cumulative bytes retransmitted (loss indicator) |
| bytes_acked | Cumulative bytes acknowledged (actual goodput) |
| delivered | Segments confirmed delivered to receiver |
| segs_out | Segments sent (used with delivered to compute delivery rate) |

### 7.4 How the Environment Works

The custom Gymnasium environment (`TCPCongestionEnv`) wraps the CSV dataset so PPO can train on it like any standard RL environment:

- `reset()` — picks a random algorithm and a random run file, returns the first row as the initial state
- `step(action)` — takes the agent's cwnd decision, computes reward from the current CSV row, advances to the next row
- One episode = one full CSV file (3600 rows)
- Each training episode uses a different algorithm and run file, so the agent generalises across all network conditions

The observation vector fed to the neural network at each step:

```python
state = [
    rtt / 250.0,                              # RTT normalised to [0,1]
    ssthresh / 60.0,                          # ssthresh normalised
    bytes_retrans / (bytes_sent + 1),         # loss rate 0 to 1
    delivered / (segs_out + 1),               # delivery rate 0 to 1
    (cwnd - cwnd_min) / (cwnd_max - cwnd_min) # agent's last cwnd normalised
]
```

### 7.5 Reward Function

The reward function is the most important design decision — it defines what 'good' behaviour means for the agent. It is a weighted sum of four components:

```
reward = 2.0 × tracking_reward
       + 0.3 × throughput_bonus
       - 0.5 × loss_penalty
       - rtt_penalty
```

| Component | Weight | Purpose |
|---|---|---|
| Tracking reward | 2.0 | `1 - |rl_cwnd - real_cwnd| / range`. Dominant signal — forces agent to match real algorithm behaviour |
| Throughput bonus | +0.3 | Rewards higher cwnd when real algo also uses high cwnd. Prevents the agent collapsing to cwnd_min |
| Loss penalty | -0.5 | Penalises retransmissions. High `bytes_retrans / bytes_sent` = network is congested |
| RTT penalty | -0.2 | Mild penalty for high latency. Kept low so it does not push the agent to always choose tiny cwnd |

> **Why tracking reward is dominant:** In the previous version, the agent collapsed to cwnd=2 (the minimum) because RTT and loss penalties were easiest to minimise by doing nothing. The 2.0 tracking weight ensures the agent must actively match real cwnd values to earn a good reward.

### 7.6 Training the Agent

Place all 17 algorithm folders in a single directory, then update the `DATA_DIR` path in `model.py` and run:

```bash
python model.py
```

You will see training progress printed every 2048 steps:

```
------------------------------------------
| rollout/         |                     |
|   ep_len_mean    | 3.6e+03             |
|   ep_rew_mean    | 1.25e+03            |  <- watch this increase
| train/           |                     |
|   explained_var  | 0.45                |  <- should approach 1.0
|   entropy_loss   | -1.43               |  <- measures exploration
------------------------------------------
```

| Metric | What to look for |
|---|---|
| ep_rew_mean | Average reward per episode. Should increase over training. If flat, tune reward weights. |
| explained_variance | How well the value network predicts rewards. Near 1.0 = well-trained critic. |
| entropy_loss | Measures exploration. If it drops too fast, raise `ent_coef` to 0.1. |
| clip_fraction | Fraction of updates hitting the PPO clip. Should stay below 0.2. |

### 7.7 Output Files

After training completes, the following files are saved to your project folder:

| File | Contents |
|---|---|
| `tcp_rl_agent.zip` | Trained PPO model — load this to make predictions without retraining |
| `rl_vs_baselines.png` | Grid of cwnd traces: real algorithm (blue) vs RL agent (orange dashed), one panel per algorithm |
| `reward_comparison.png` | Bar chart of average reward per algorithm environment |
| `cwnd_comparison.png` | Side-by-side mean cwnd bars: real vs RL agent for all 17 algorithms |

### 7.8 Evaluating the Trained Agent

To load and evaluate a previously trained agent without retraining:

```python
from stable_baselines3 import PPO
import numpy as np

model = PPO.load('tcp_rl_agent')

# build state vector from a CSV row
obs = np.array([rtt/250, ssthresh/60, retrans_rate,
                delivery_rate, cwnd_norm], dtype=np.float32)

action, _ = model.predict(obs, deterministic=True)
predicted_cwnd = (float(action[0]) + 1.0) / 2.0 * (cwnd_max - cwnd_min) + cwnd_min
```

### 7.9 Key Python Libraries

| Library | Purpose |
|---|---|
| `gymnasium` | Standard RL environment interface. Defines `reset()` and `step()` contract between environment and training algorithm. |
| `gymnasium.spaces` | Defines the shape and valid range of observations (Box 0–1, shape 5) and actions (Box -1 to 1, shape 1). |
| `stable_baselines3.PPO` | The PPO training algorithm. Runs the environment, collects experience, and updates the neural network weights. |
| `check_env` | Validates the custom environment before training. Catches shape mismatches and missing return values early. |
| `DummyVecEnv` | Vectorised environment wrapper used internally by SB3. Enables collecting experience from multiple env copies. |
| `pandas` | Loads and processes the CSV trace files. |
| `numpy` | Numerical operations — normalisation, clipping, metrics computation. |
| `matplotlib` | Generates the comparison plots saved as PNG files. |

### 7.10 Hyperparameter Reference

| Parameter | Value | Effect if Changed |
|---|---|---|
| learning_rate | 3e-4 | Lower = slower but more stable. Higher = faster but may diverge. |
| n_steps | 2048 | Steps collected before each update. Higher = more stable gradient estimates. |
| batch_size | 64 | Mini-batch size for gradient updates. Higher = smoother updates. |
| n_epochs | 10 | How many times each batch is reused. Higher = more sample efficiency. |
| gamma | 0.99 | Discount factor. Near 1.0 = values long-term rewards. Lower = short-sighted. |
| ent_coef | 0.05 | Exploration bonus. Raise to 0.1 if agent stops exploring (entropy drops fast). |
| net_arch | [256, 256] | Neural network hidden layers. Increase to [512, 512] for more capacity. |
| total_timesteps | 1,000,000 | Total training steps. Increase to 2M for better convergence. |

### 7.11 Common Issues and Fixes

| Problem | Cause | Fix |
|---|---|---|
| Agent outputs constant cwnd | Reward function lets agent exploit RTT/loss penalties with cwnd=min | Ensure `tracking_reward` weight is at least 2.0 |
| `KeyError: bytes_retrans` | CDG or other algorithm missing this column in CSV | Add missing column fill with 0 in `load_dataset` |
| `FileNotFoundError` on CSV | Filename pattern mismatch (`.log` vs `.log.csv`) | Code tries both — check actual filenames in folder |
| `ep_rew_mean` not increasing | Learning rate too high or reward too sparse | Lower `learning_rate` to `1e-4`, increase `ent_coef` |
| `explained_variance` stays near 0 | Value network not learning — too little data per update | Increase `n_steps` to 4096 |
| Training crashes mid-run | RAM exhaustion on large dataset | Close other applications, reduce `total_timesteps` |
