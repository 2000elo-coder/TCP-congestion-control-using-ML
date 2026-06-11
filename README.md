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

Or expressed in standard mathematical formulations:

$$\text{RTT}_{\text{norm}} = \text{clip}\left(\frac{\text{RTT}}{250.0}, 0, 1\right)$$

$$\text{ssthresh}_{\text{norm}} = \text{clip}\left(\frac{\text{ssthresh}}{60.0}, 0, 1\right)$$

$$\text{retrans\_rate} = \text{clip}\left(\frac{\text{bytes\_retrans}}{\text{bytes\_sent} + 1}, 0, 1\right)$$

$$\text{delivery\_rate} = \text{clip}\left(\frac{\text{delivered}}{\text{segs\_out} + 1}, 0, 1\right)$$

$$\text{cwnd}_{\text{norm}} = \text{clip}\left(\frac{\text{cwnd} - \text{cwnd}_{\text{min}}}{\text{cwnd}_{\text{max}} - \text{cwnd}_{\text{min}}}, 0, 1\right)$$

### 7.5 Reward Function

The reward function is the most important design decision — it defines what 'good' behaviour means for the agent. It is a weighted sum of four components:

```
reward = 2.0 × tracking_reward
       + 0.3 × throughput_bonus
       - 0.5 × loss_penalty
       - rtt_penalty
```

Or written explicitly as:

$$R_t = 2.0 \cdot R_{\text{track}} + 0.3 \cdot \text{cwnd}_{\text{norm}} - 0.5 \cdot \text{Loss}_{\text{penalty}} - \text{RTT}_{\text{penalty}}$$

Where:

* **Tracking Component ($R_{\text{track}}$):** Forces the policy network to track historical baseline window updates closely to optimize behavioral alignment:
  $$R_{\text{track}} = 1.0 - \frac{|\text{cwnd}_{\text{RL}} - \text{cwnd}_{\text{real}}|}{\text{cwnd}_{\text{max}} - \text{cwnd}_{\text{min}}}$$
* **Loss Penalty:** Discourages transmission rate allocations that trigger queuing drops and segment retransmissions:
  $$\text{Loss}_{\text{penalty}} = \text{clip}\left(\frac{\text{bytes\_retrans}}{\text{bytes\_sent} + 1}, 0, 1\right)$$
* **RTT Penalty:** Mildly penalizes latency increases, preventing self-congestion bufferbloat:
  $$\text{RTT}_{\text{penalty}} = 0.2 \cdot \text{clip}\left(\frac{\text{RTT}}{250.0}, 0, 1\right)$$

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

---

## 8. NS-3 Simulation Script Design (`tcp-rl-sim.cc`)

The custom simulation script located in `scratch/tcp-rl-sim.cc` defines the network topology, schedules packet injection, and manages real-time tracing metrics. It allows evaluating your RL agent or baseline algorithms under multiple competitive parameters.

### 8.1 Key Features

- **Multi-Sender Topology Support:** Allows running single-sender flows or configuring up to 8 parallel senders ($N \in [1, 8]$) sharing a common bottleneck. This is used to test the fairness and performance of your model against other protocols.
- **Staggered Flow Initiation:** Starts sender flows sequentially (`0.1 + i * 0.05` seconds) to avoid massive packet collisions during initial TCP synchronization handshakes.
- **Dynamic Queue Sizing:** Queue disc limits on bottleneck devices are computed using propagation delays:
  
  $$qSize = \text{max}\left(10, \frac{\text{bandwidth} \times 10^6}{8} \times \frac{2 \times \text{delay}}{1000} \div \text{MSS}\right)$$

### 8.2 Safe Connection Helper (Direct Socket Tracing)

In NS-3.42, dynamic wildcard paths (such as `SocketList/*`) do not resolve before the simulation runs because sockets are allocated on demand. Attempting to connect wildcards in `main()` causes a fatal trace attachment error. 

The simulation script resolves this by connecting to a specific target socket (`SocketList/0`) 0.5 seconds after execution begins:

```cpp
static void ConnectSenderTraces (uint32_t nodeIdx, uint32_t senderIdx)
{
    std::string base = "/NodeList/" + std::to_string (nodeIdx) +
                       "/$ns3::TcpL4Protocol/SocketList/0/";

    Config::ConnectWithoutContext (
        base + "CongestionWindow",
        MakeBoundCallback (&CwndChange, senderIdx));
    Config::ConnectWithoutContext (
        base + "SlowStartThreshold",
        MakeBoundCallback (&SsthreshChange, senderIdx));
    Config::ConnectWithoutContext (
        base + "RTT",
        MakeBoundCallback (&RttChange, senderIdx));
    Config::ConnectWithoutContext (
        base + "Tx",
        MakeBoundCallback (&TxTrace, senderIdx));
    Config::ConnectWithoutContext (
        base + "Rx",
        MakeBoundCallback (&RxTrace, senderIdx));
}
```

---

## 9. Real-Time Python Inference Bridge (`rl_bridge.py`)

Because NS-3 (C++) cannot natively execute Python neural-network packages, `rl_bridge.py` coordinates state-space data and predictions via file-based Inter-Process Communication (IPC):

```
NS-3 Simulation (C++)                                 Python Bridge (rl_bridge.py)
 ┌────────────────────────┐                             ┌────────────────────────┐
 │ PeriodicTrace() fires  │                             │ rl_bridge.py loops and │
 │ every 1 second         │                             │ polls for state file   │
 └───────────┬────────────┘                             └───────────┬────────────┘
             │                                                      │
             │ 1. Writes stats to                                   │
             │    /tmp/rl_state.txt                                 │
             ▼                                                      │
    [ /tmp/rl_state.txt ]                                           │
             │                                                      │
             │ 2. Parses and normalizes the                         │
             └─────────────────────────────────────────────────────►│ features into observation
                                                                    │ vector
                                                                    │
                                                                    │ 3. Runs inference:
                                                                    │    model.predict(obs)
                                                                    │
                                                                    │ 4. Scales and writes cwnd
                                                                    │    to /tmp/rl_action.txt
                                                                    ▼
                                                           [ /tmp/rl_action.txt ]
                                                                    │
             │ 5. Reads decision from                               │
             │    /tmp/rl_action.txt                                │
             ◄──────────────────────────────────────────────────────┘
             │
             ▼
 ┌────────────────────────┐
 │ Overrides cwnd of      │
 │ active TCP socket      │
 └────────────────────────┘
```

The script cleans up trailing `/tmp` files on boot, decodes raw metrics, applies normalization clipping matching `model.py`, and implements a 3-second timeout window upon detecting `/tmp/rl_done.txt` to ensure trailing packets finish logging cleanly.

---

## 10. Running the Co-Simulation Workflow

### 10.1 Environment Execution Steps

Move all required script assets to your local NS-3 root folder:

```bash
# Copy C++ simulation script to NS-3 scratch folder
cp tcp-rl-sim.cc ~/Downloads/ns-allinone-3.42/ns-3.42/scratch/

# Copy the trained model and Python bridge to the NS-3 root directory
cp tcp_rl_agent.zip ~/Downloads/ns-allinone-3.42/ns-3.42/
cp rl_bridge.py ~/Downloads/ns-allinone-3.42/ns-3.42/
```

Navigate to your NS-3 directory and build the binaries:

```bash
cd ~/Downloads/ns-allinone-3.42/ns-3.42
./ns3 build
```

### 10.2 Running Baseline Modes (RL Disabled)

Verify baseline network performance across multiple configurations (e.g., competing senders, bandwidth limits, one-way delays, and packet loss rates):

```bash
# 3 flows running Cubic over a 10 Mbps bottleneck link (40ms propagation delay)
./ns3 run "tcp-rl-sim --algo=cubic --senders=3 --bandwidth=10 --delay=40 --loss=0.001 --rl=false"
```

Expected output showing successful baseline traffic sharing:
```
=== TCP-RL-SIM (multi-sender) ===
Sender 0  : cubic  (ns3::TcpCubic)
Senders 1+: cubic  (ns3::TcpCubic)  x2
Bottleneck: 10 Mbps  40 ms  loss=0.001
Duration  : 60 s
-------------------------------------------------
Throughput Summary
  Sender 0 [baseline]  3.20 Mbps  (33.31% of total)
  Sender 1 [competitor]  3.48 Mbps  (36.23% of total)
  Sender 2 [competitor]  2.93 Mbps  (30.46% of total)
```

### 10.3 Running Co-Simulation Mode (RL Enabled)

To execute the closed-loop co-simulation, run the Python inference bridge in one terminal, then start the NS-3 simulation in a separate terminal:

**Terminal 1 (Start Python Bridge):**
```bash
cd ~/Downloads/ns-allinone-3.42/ns-3.42
python3 rl_bridge.py --model tcp_rl_agent --cwnd_min 2 --cwnd_max 500 --verbose
```

**Terminal 2 (Start NS-3 with RL enabled):**
```bash
cd ~/Downloads/ns-allinone-3.42/ns-3.42
./ns3 run "tcp-rl-sim --algo=cubic --duration=60 --rl=true"
```

---

## 11. Real-Time Execution Logs & Performance Analysis

### 11.1 Live IPC Communication Trace
When Terminal 2 connects, the active TCP socket's metrics are output directly to the Python bridge, which calculates and applies the target congestion window:

```
Loading model from tcp_rl_agent.zip ...
Model loaded.  cwnd range: [2.0, 500.0]
Bridge ready — waiting for NS-3 simulation to start...

  step     0 | rtt=273.00ms  cwnd_real=469.0  rl_cwnd=179.3
  step     1 | rtt=281.00ms  cwnd_real=142.0  rl_cwnd=227.0
  step     2 | rtt=288.00ms  cwnd_real=167.0  rl_cwnd=223.3
  step     3 | rtt=220.00ms  cwnd_real=187.0  rl_cwnd=193.0
  step     4 | rtt=237.00ms  cwnd_real=200.0  rl_cwnd=206.6
  step     5 | rtt=247.00ms  cwnd_real=206.0  rl_cwnd=214.8
```

The RL agent maps continuous actions directly to congestion window decisions, adapting to network state changes rather than collapsing to the minimum congestion window bounds.

### 11.2 Visual Performance Evaluation (`cwnd_comparison.png`)

```
Mean cwnd: RL agent vs real algorithm
 35 ├─
 30 ├─       ■   ■                   ■   ■
 25 ├─       │   │   ■   ■   ■   ■   │   │
 20 ├─   ■   │   │   │   │   │   │   │   │
 15 ├─   │   │   │   │   │   │   │   │   │
 10 ├─   │   │   │   │   │   │   │   │   │
  5 ├─   │   │   │   │   │   │   │   │   │
  0 └───┴───┴───┴───┴───┴───┴───┴───┴───┴───┴───
        bbr     bic    cubic   htcp    reno    vegas
        
        [■] Real algorithm   [■] RL agent
```

This chart confirms the generalization capabilities of the single neural network policy. The RL agent correctly scales its window sizes up or down depending on the active environment trace:
- **High-capacity protocols (such as Illinois, Scalable, and Bic):** The agent correctly allocates large window sizes ($\ge 30$).
- **Conservative protocols (such as Vegas, BBR, and CDG):** The agent reduces its transmission rate, preventing congestion collapse while maintaining link stability.

---

## 12. Detailed Troubleshooting of Co-Simulation Challenges

Developing and deploying an inter-process co-simulation framework presented several challenges, which were resolved through targeted fixes:

### 12.1 Out of Memory (OOM) Compiler Termination
- **Problem:** During compilation, the C++ compiler (`cc1plus`) was terminated with a `Killed` signal. 
- **Cause:** The Virtual Machine exhausted its physical memory footprint while attempting parallel compilation tasks.
- **Resolution:** Allocated a persistent 4.0 GiB swap space (`/swapfile`) and restricted parallel execution by passing the `-j1` build flag:
  ```bash
  ./ns3 build -- -j1
  ```

### 12.2 Double Queue Disc Allocation Error
- **Problem:** Running the simulation resulted in a crash stating: `"Cannot install a root queue disc on a device already having one."`
- **Cause:** NS-3's `PointToPointHelper` automatically installs a default `PfifoFastQueueDisc` on every device it creates. Installing a second queue disc on top of it causes a fatal error.
- **Resolution:** Explicitly uninstalled the default queue disc before attaching custom queue boundaries:
  ```cpp
  TrafficControlHelper tchUninstall;
  tchUninstall.Uninstall(rrDevs);
  ```

### 12.3 Wildcard Socket Tracing Connection Failure
- **Problem:** The simulation threw a fatal abort: `"Could not connect callback to /NodeList/0/$ns3::TcpL4Protocol/SocketList/*/CongestionWindow"`
- **Cause:** Dynamic wildcard paths (using `*`) do not resolve in the `Config` system prior to active socket creation, causing the simulation to abort immediately.
- **Resolution:** Scheduled trace registration 0.5 seconds after simulation boot, targeting the explicit socket path (`SocketList/0`) after connection establishment:
  ```cpp
  Simulator::Schedule(Seconds(0.5), &ConnectSenderTraces);
  ```

### 12.4 Missing Trace Sources in NS-3.42
- **Problem:** Execution aborted with errors regarding missing trace paths such as `BytesRetransmitted`.
- **Cause:** `BytesRetransmitted` is not a standard trace source in NS-3.42, causing a configuration failure.
- **Resolution:** Switched to tracing standard event sources like `Tx` and `Rx` using `TraceConnectWithoutContext`, and bypassed potential trace path mismatches using safe callback wrappers.
