
# TCP Congestion Control Using Machine Learning

## NS-3 Setup, Installation & RL Model Guide
**Environment:** VirtualBox + Ubuntu 24.04 LTS + NS-3.42 + PPO Agent

---

## 📌 1. VirtualBox Installation

### System Requirements
- Windows 10 / 11 (64-bit)
- 8 GB RAM (16 GB recommended)
- 50 GB disk space
- CPU virtualization enabled

### Install
Download: https://www.virtualbox.org/wiki/Downloads  
Install with default settings.

---

## 🐧 2. Ubuntu 24.04 Installation

### Steps
- Download ISO: https://ubuntu.com/download/desktop
- Create VM:
  - Name: Ubuntu NS3
  - RAM: 6GB
  - CPU: 2 cores
  - Disk: 40GB
- Enable PAE/NX, set video memory to 128MB
- Install Ubuntu (Normal Installation)

---

## ⚙️ 3. NS-3 Installation

### Update System
```bash
sudo apt update && sudo apt upgrade -y

sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

sudo apt install -y build-essential autoconf automake python3 python3-dev python3-pip
sudo apt install -y cmake ninja-build git libboost-all-dev libssl-dev
sudo apt install -y libsqlite3-dev libxml2-dev libgsl-dev
sudo apt install -y qtbase5-dev qt5-qmake qtbase5-dev-tools
sudo apt install -y openmpi-bin libopenmpi-dev
sudo apt install -y gir1.2-goocanvas-2.0 python3-gi python3-pygraphviz
sudo apt install -y wireshark tcpdump


wget http://www.nsnam.org/releases/ns-allinone-3.42.tar.bz2
tar -xjvf ns-allinone-3.42.tar.bz2
cd ns-allinone-3.42/ns-3.42


./ns3 configure --enable-examples --enable-tests
./ns3 build -- -j1

./ns3 run hello-simulator

ns-3.42/
├── scratch/
├── src/internet/model/
├── examples/tcp/
├── build/
├── ns3
└── CMakeLists.txt


./ns3 run tcp-bulk-send

gedit scratch/my-tcp-sim.cc
./ns3 build
./ns3 run my-tcp-sim


pip install stable-baselines3 gymnasium pandas numpy matplotlib

tcp-dataset/
├── bbr/
├── cubic/
└── yeah/

state = [
    rtt / 250.0,
    ssthresh / 60.0,
    bytes_retrans / (bytes_sent + 1),
    delivered / (segs_out + 1),
    (cwnd - cwnd_min) / (cwnd_max - cwnd_min)
]

reward = 2.0 * tracking_reward \
       + 0.3 * throughput_bonus \
       - 0.5 * loss_penalty \
       - 0.2 * rtt_penalty

python model.py

from stable_baselines3 import PPO

model = PPO.load("tcp_rl_agent")
action, _ = model.predict(obs)

