# TCP Congestion Control Using ML

---

## NS-3 Setup and Installation Guide
### VirtualBox + Ubuntu 24.04 LTS + NS-3.42

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
2. Click **"Windows hosts"** to download the VirtualBox installer (.exe file)
3. Run the downloaded installer as Administrator
4. Click Next through all installation steps and accept default settings
5. Click Install and wait for the installation to complete
6. Click Finish to launch VirtualBox

### 1.3 Configure VirtualBox Settings
1. Open VirtualBox and go to **File > Preferences > General**
2. Set the Default Machine Folder to a drive with sufficient space (e.g., D:\VMs)
3. Click OK to save settings

---

## 2. Ubuntu 24.04 LTS Installation

### 2.1 Download Ubuntu ISO
1. Go to https://ubuntu.com/download/desktop
2. Download **Ubuntu 24.04 LTS** (.iso file, approximately 5 GB)
3. Save the ISO file to a known location on your Windows PC

### 2.2 Create a New Virtual Machine
1. Open VirtualBox and click the **"New"** button
2. Enter Name: `Ubuntu NS3`, set Type to `Linux`, Version to `Ubuntu (64-bit)`
3. Set Base Memory to **6144 MB (6 GB)** — recommended for NS-3 builds
4. Set Processors to **2 CPUs** if your machine has 4 or more cores
5. Create a Virtual Hard Disk with at least **40 GB** storage
6. Click Finish to create the VM

### 2.3 Configure VM Settings
1. Select your VM and click **Settings**
2. Go to **System > Processor** and check Enable PAE/NX
3. Go to **Display > Screen** and set Video Memory to **128 MB**
4. Go to **Network > Adapter 1** and ensure it is set to **NAT**
5. Go to **Storage > Empty** optical drive, click the disc icon, and select your Ubuntu ISO
6. Click OK to save all settings

### 2.4 Install Ubuntu
1. Click **Start** to boot the VM from the Ubuntu ISO
2. Select **"Try or Install Ubuntu"** from the boot menu
3. Click **"Install Ubuntu"** on the welcome screen
4. Select keyboard layout and click Next
5. Choose **"Normal Installation"** and check both download options
6. Select **"Erase disk and install Ubuntu"** (safe inside VM)
7. Set your username, computer name, and password
8. Click Install and wait for installation to complete (10–20 minutes)
9. Click **Restart Now** and press Enter when prompted to remove the ISO

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
Swap should show **4.0Gi**.

### 3.3 Install Required Libraries
Install each dependency one by one:
```bash
sudo apt install -y build-essential
sudo apt install -y autoconf
sudo apt install -y automake
sudo apt install -y python3
sudo apt install -y python3-dev
sudo apt install -y python3-pip
sudo apt install -y cmake
sudo apt install -y ninja-build
sudo apt install -y git
sudo apt install -y libboost-all-dev
sudo apt install -y libssl-dev
sudo apt install -y libsqlite3-dev
sudo apt install -y libxml2-dev
sudo apt install -y libgsl-dev
sudo apt install -y qtbase5-dev
sudo apt install -y qt5-qmake
sudo apt install -y qtbase5-dev-tools
sudo apt install -y openmpi-bin
sudo apt install -y libopenmpi-dev
sudo apt install -y gir1.2-goocanvas-2.0
sudo apt install -y python3-gi
sudo apt install -y python3-pygraphviz
sudo apt install -y wireshark
sudo apt install -y tcpdump
```

> **Note:** The package `python3-gi-cairo` may not be available on Ubuntu 24.04.
> This is safe to skip — it only affects optional graphical animation features
> and does not impact simulations.

### 3.4 Download NS-3.42
Download the NS-3.42 archive manually from your browser:
```
http://www.nsnam.org/releases/ns-allinone-3.42.tar.bz2
```
Save the file to your Ubuntu **Downloads** folder.

Verify the file size is approximately **44–46 MB**:
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
You should see a file called `ns3` in the list.

### 3.6 Configure NS-3
```bash
./ns3 configure --enable-examples --enable-tests
```

> **Expected output:** `Configuring done` and `Generating done` at the end
> confirms successful configuration. Takes approximately 2–5 minutes.

### 3.7 Build NS-3
```bash
./ns3 build -- -j1
```

> **Important:** The `-j1` flag limits the build to one parallel job to prevent
> out-of-memory crashes on systems with limited RAM. This build takes
> approximately **40–60 minutes**. Do NOT close the terminal or shut down
> the VM during this process.

### 3.8 Verify Installation
Run the hello simulator to confirm NS-3 is working:
```bash
./ns3 run hello-simulator
```

**Expected output:**
```
Hello Simulator
```
NS-3 is successfully installed and ready to use! ✅

---

## 4. Troubleshooting Common Issues

| Problem | Cause | Fix |
|---|---|---|
| Build killed during compilation | RAM and swap exhausted | Increase swap to 8 GB, close all other apps before building |
| SSL error during wget download | Outdated certificates or restricted network | Download manually on Windows and transfer via Shared Folder |
| tar extraction error: not recoverable | Corrupted or incomplete download | Delete file, re-download, verify size is ~44–46 MB |
| Unknown option error during configure | Typo in command (e.g. `--enalbe`) | Re-type command carefully, use `--enable-examples` |
| Swap showing 0B after reboot | Swap not made permanent | Run the `echo '/swapfile...'` fstab command again |
| `python3-gi-cairo` not found | Package renamed in Ubuntu 24.04 | Skip it — not required for simulations |

---

## 5. Important Folder Structure

```
~/Downloads/ns-allinone-3.42/ns-3.42/
├── scratch/              ← Place your custom simulation scripts here
├── src/internet/model/   ← NS-3 TCP source code
├── examples/tcp/         ← Built-in TCP example scripts
├── build/                ← Compiled build output
├── ns3                   ← NS-3 build tool (run commands from here)
└── CMakeLists.txt        ← Build configuration
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

*NS-3 Installation Guide | Ubuntu 24.04 LTS | VirtualBox | NS-3.42*
