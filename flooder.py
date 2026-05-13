#!/usr/bin/env python3

import subprocess
import random
import time
import os

# ==================================
# CONFIG
# ==================================

INTERFACE = "wlan0"
SSID = "YOUR_WIFI"
PASSWORD = "YOUR_PASSWORD"

ITERATIONS = 25
WAIT_TIME = 5

# ==================================
# DEVICE DATABASE
# ==================================

DEVICES = {
    "Samsung-A10": [
        "38:2D:E8",
        "A8:9C:ED",
        "64:BC:0C"
    ],
    "iPhone-13": [
        "F0:18:98",
        "AC:BC:32"
    ],
    "Xiaomi-Redmi": [
        "64:09:80",
        "50:8F:4C"
    ],
    "Motorola-G": [
        "9C:4F:DA",
        "00:1A:11"
    ]
}

# ==================================
# COMMAND RUNNER
# ==================================

def run(cmd):
    print(f"\n[+] {cmd}")

    result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    if result.stdout:
        print(result.stdout.strip())

    if result.stderr:
        print(result.stderr.strip())

    return result.returncode

# ==================================
# MAC GENERATOR
# ==================================

def generate_mac(prefix):
    suffix = [random.randint(0, 255) for _ in range(3)]
    return prefix + ":" + ":".join(f"{x:02X}" for x in suffix)

# ==================================
# WIFI FUNCTIONS
# ==================================

def disconnect():
    run(f"nmcli dev disconnect {INTERFACE}")

def connect():

    # Delete old temp connection
    run(f'nmcli connection delete fakewifi 2>/dev/null')

    cmd = (
        f'nmcli connection add '
        f'type wifi '
        f'ifname {INTERFACE} '
        f'con-name fakewifi '
        f'ssid "{SSID}"'
    )

    run(cmd)

    run(
        f'nmcli connection modify fakewifi '
        f'wifi-sec.key-mgmt wpa-psk'
    )

    run(
        f'nmcli connection modify fakewifi '
        f'wifi-sec.psk "{PASSWORD}"'
    )

    run('nmcli connection up fakewifi')

def set_mac(mac):
    run(f"ip link set {INTERFACE} down")
    run(f"macchanger -m {mac} {INTERFACE}")
    run(f"ip link set {INTERFACE} up")

def set_hostname(name):
    run(f"hostnamectl set-hostname {name}")

# ==================================
# MAIN
# ==================================

if os.geteuid() != 0:
    print("Run as root.")
    exit()

print("\n=== Fake Device Simulator ===\n")

for i in range(ITERATIONS):

    print("\n" + "=" * 60)
    print(f"DEVICE {i+1}/{ITERATIONS}")

    # Random device type
    device = random.choice(list(DEVICES.keys()))
    prefix = random.choice(DEVICES[device])

    mac = generate_mac(prefix)

    hostname = f"{device}-{random.randint(1000,9999)}"

    print(f"[Device ] {device}")
    print(f"[MAC    ] {mac}")
    print(f"[Host   ] {hostname}")

    # Disconnect previous
    disconnect()

    # Set fake identity
    set_hostname(hostname)
    set_mac(mac)

    # Wait interface recovery
    time.sleep(2)

    # Connect
    print("\n[+] Connecting...")
    connect()

    # Stay connected
    print(f"[+] Waiting {WAIT_TIME}s")
    time.sleep(WAIT_TIME)

    # Disconnect
    print("[+] Disconnecting...")
    disconnect()

    time.sleep(2)

print("\nFinished.")
