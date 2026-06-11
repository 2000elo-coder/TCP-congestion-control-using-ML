#!/usr/bin/env python3
"""
rl_bridge.py  —  Real-time inference bridge between NS-3 and your PPO agent
=============================================================================

PURPOSE:
    NS-3 (C++) cannot directly call Python.  This script runs as a
    separate process and talks to the simulation via two tiny text files:

        /tmp/rl_state.txt   ← NS-3 writes current network state here
        /tmp/rl_action.txt  ← this script writes the RL cwnd decision here
        /tmp/rl_done.txt    ← NS-3 writes "done" when simulation finishes

HOW TO RUN:
    # Terminal 1 — start the bridge FIRST, wait for "Bridge ready" message
    python3 rl_bridge.py --model tcp_rl_agent --cwnd_min 2 --cwnd_max 3000

    # Terminal 2 — then start NS-3
    ./ns3 run "tcp-rl-sim --algo=cubic --rl=true --duration=60"

ARGUMENTS:
    --model     Path to tcp_rl_agent.zip (without .zip extension)
    --cwnd_min  Same cwnd_min used during training  (default: 2)
    --cwnd_max  Same cwnd_max used during training  (default: 3000)
    --verbose   Print each state→action pair for debugging

EXPECTED STATE FILE FORMAT (semicolon-separated, one line):
    rtt_ms ; ssthresh ; bytes_sent ; bytes_retrans ; delivered ; segs_out ; current_cwnd
"""

import argparse
import os
import sys
import time
import numpy as np

# ── Parse arguments ──────────────────────────────────────────────────────────
parser = argparse.ArgumentParser ()
parser.add_argument ("--model",    default="tcp_rl_agent",
                     help="Path to model zip (without .zip)")
parser.add_argument ("--cwnd_min", type=float, default=2.0)
parser.add_argument ("--cwnd_max", type=float, default=3000.0)
parser.add_argument ("--verbose",  action="store_true")
args = parser.parse_args ()

STATE_FILE  = "/tmp/rl_state.txt"
ACTION_FILE = "/tmp/rl_action.txt"
DONE_FILE   = "/tmp/rl_done.txt"

# ── Load the trained PPO model ───────────────────────────────────────────────
try:
    from stable_baselines3 import PPO
except ImportError:
    sys.exit ("ERROR: stable-baselines3 not installed.\n"
              "       Run: pip install stable-baselines3")

model_path = args.model if args.model.endswith (".zip") else args.model + ".zip"
if not os.path.exists (model_path):
    sys.exit (f"ERROR: Model file not found: {model_path}\n"
              f"       Make sure tcp_rl_agent.zip is in the same folder.")

print (f"Loading model from {model_path} ...")
model = PPO.load (args.model)
print (f"Model loaded.  cwnd range: [{args.cwnd_min:.1f}, {args.cwnd_max:.1f}]")

cwnd_min = args.cwnd_min
cwnd_max = args.cwnd_max
cwnd_range = cwnd_max - cwnd_min

# ── Clean up leftover IPC files ───────────────────────────────────────────────
for f in [STATE_FILE, ACTION_FILE, DONE_FILE]:
    try: os.remove (f)
    except FileNotFoundError: pass

print ("Bridge ready — waiting for NS-3 simulation to start...\n")

# ── Main polling loop ─────────────────────────────────────────────────────────
# Exit only when DONE_FILE exists AND no new state has arrived for 3 seconds.
# This prevents premature exit when NS-3 writes done before all IPC steps finish.
step = 0
done_seen       = False
last_state_time = time.time ()

while True:
    if os.path.exists (DONE_FILE):
        done_seen = True

    # Give 3 extra seconds after done signal for any remaining state files
    if done_seen and (time.time () - last_state_time) > 3.0:
        print (f"\nSimulation finished after {step} steps.  Bridge exiting.")
        break

    # Wait for NS-3 to write a state file
    if not os.path.exists (STATE_FILE):
        time.sleep (0.005)
        continue

    last_state_time = time.time ()

    # Read the state
    try:
        with open (STATE_FILE, "r") as f:
            line = f.read ().strip ()
        os.remove (STATE_FILE)   # consume — prevents re-reading same state

        parts = line.split (";")
        if len (parts) < 7:
            continue

        rtt_ms        = float (parts[0])
        ssthresh      = float (parts[1])
        bytes_sent    = float (parts[2])
        bytes_retrans = float (parts[3])
        delivered     = float (parts[4])
        segs_out      = float (parts[5])
        current_cwnd  = float (parts[6])

    except Exception as e:
        print (f"  [step {step}] State read error: {e}")
        continue

    # Build the 5-feature observation vector (same normalisation as training)
    rtt_norm      = float (np.clip (rtt_ms / 250.0,                          0, 1))
    ssthresh_norm = float (np.clip (ssthresh / 60.0,                         0, 1))
    retrans_rate  = float (np.clip (bytes_retrans / (bytes_sent + 1),        0, 1))
    delivery_rate = float (np.clip (delivered     / (segs_out + 1),          0, 1))
    cwnd_norm     = float (np.clip ((current_cwnd - cwnd_min) / cwnd_range,  0, 1))

    obs = np.array ([rtt_norm, ssthresh_norm, retrans_rate,
                     delivery_rate, cwnd_norm], dtype=np.float32)

    # Run inference
    action, _ = model.predict (obs, deterministic=True)

    # Scale [-1, 1] → [cwnd_min, cwnd_max]  (same as training _scale_action)
    rl_cwnd = (float (action[0]) + 1.0) / 2.0 * cwnd_range + cwnd_min
    rl_cwnd = max (cwnd_min, min (cwnd_max, rl_cwnd))

    if args.verbose:
        print (f"  step {step:5d} | rtt={rtt_ms:7.2f}ms  "
               f"cwnd_real={current_cwnd:6.1f}  rl_cwnd={rl_cwnd:6.1f}")

    # Write the decision for NS-3
    with open (ACTION_FILE, "w") as f:
        f.write (f"{rl_cwnd:.4f}\n")

    step += 1

print ("Bridge done.")
