#!/usr/bin/env python3

import subprocess
import random
import time
import os
from datetime import datetime

# =========================================================
# CONFIG
# =========================================================

INTERFACE = "wlan0"

SSID = "YOUR_WIFI"
PASSWORD = "YOUR_PASSWORD"

ITERATIONS = 15
WAIT_TIME = 5

PING_TARGET = "8.8.8.8"

# =========================================================
# DEVICE DATABASE
# =========================================================

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

# =========================================================
# COLORS
# =========================================================

RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
CYAN = "\033[96m"
WHITE = "\033[97m"
RESET = "\033[0m"

# =========================================================
# UTILITIES
# =========================================================

def banner():
    print(f"""{CYAN}

╔══════════════════════════════════════════════╗
║        WIFI DEVICE SIMULATOR - KALI         ║
║      Fake Clients / DHCP / ACL Tester       ║
╚══════════════════════════════════════════════╝

{RESET}""")


def log(message, color=WHITE):
    timestamp = datetime.now().strftime("%H:%M:%S")
    print(f"{color}[{timestamp}] {message}{RESET}")


def run(cmd, silent=False):

    result = subprocess.run(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    output = result.stdout + result.stderr

    if not silent and output.strip():
        print(output.strip())

    return result.returncode, output


# =========================================================
# MAC GENERATOR
# =========================================================

def generate_mac(prefix):
    suffix = [random.randint(0, 255) for _ in range(3)]
    return prefix + ":" + ":".join(f"{x:02X}" for x in suffix)


# =========================================================
# NETWORK FUNCTIONS
# =========================================================

def disconnect():
    run(f"nmcli dev disconnect {INTERFACE}", silent=True)


def set_mac(mac):

    log(f"Changing MAC -> {mac}", BLUE)

    run(f"ip link set {INTERFACE} down", silent=True)
    run(f"macchanger -m {mac} {INTERFACE}", silent=True)
    run(f"ip link set {INTERFACE} up", silent=True)

    time.sleep(2)


def set_hostname(name):

    log(f"Changing hostname -> {name}", BLUE)

    run(f"hostnamectl set-hostname {name}", silent=True)


def connect():

    log("Preparing WiFi profile...", CYAN)

    run("nmcli connection delete fakewifi", silent=True)

    run(
        f'nmcli connection add '
        f'type wifi '
        f'ifname {INTERFACE} '
        f'con-name fakewifi '
        f'ssid "{SSID}"',
        silent=True
    )

    run(
        f'nmcli connection modify fakewifi '
        f'wifi-sec.key-mgmt wpa-psk',
        silent=True
    )

    run(
        f'nmcli connection modify fakewifi '
        f'wifi-sec.psk "{PASSWORD}"',
        silent=True
    )

    log("Attempting connection...", CYAN)

    code, output = run(
        "nmcli connection up fakewifi",
        silent=True
    )

    output_lower = output.lower()

    # =====================================================
    # CONNECTION ANALYSIS
    # =====================================================

    if "successfully activated" in output_lower:

        log("CONNECTED TO ACCESS POINT", GREEN)

        # Check IP
        _, ip_output = run(
            f"ip addr show {INTERFACE}",
            silent=True
        )

        ip_address = None

        for line in ip_output.splitlines():
            if "inet " in line:
                ip_address = line.strip().split()[1]
                break

        if ip_address:
            log(f"DHCP SUCCESS -> {ip_address}", GREEN)
        else:
            log("CONNECTED BUT NO DHCP", YELLOW)

        # Ping test
        log(f"Pinging {PING_TARGET}...", CYAN)

        ping = subprocess.run(
            f"ping -c 1 -W 2 {PING_TARGET}",
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        if ping.returncode == 0:
            log("INTERNET ACCESS OK", GREEN)
        else:
            log("CONNECTED BUT NO INTERNET", YELLOW)

        return True

    elif "wrong password" in output_lower:
        log("WRONG PASSWORD", RED)

    elif "activation failed" in output_lower:
        log("CONNECTION REJECTED", RED)
        log("Possible MAC filtering / ACL / AP limit", YELLOW)

    elif "ssid not found" in output_lower:
        log("SSID NOT FOUND", RED)

    elif "timeout" in output_lower:
        log("TIMEOUT", RED)

    else:
        log("UNKNOWN ERROR", RED)
        print(output)

    return False


# =========================================================
# MAIN
# =========================================================

if os.geteuid() != 0:
    print("Run as root.")
    exit()

banner()

log(f"Interface : {INTERFACE}", CYAN)
log(f"SSID      : {SSID}", CYAN)
log(f"Iterations: {ITERATIONS}", CYAN)

print()

for i in range(ITERATIONS):

    print(f"{BLUE}{'=' * 60}{RESET}")

    device = random.choice(list(DEVICES.keys()))
    prefix = random.choice(DEVICES[device])

    mac = generate_mac(prefix)

    hostname = f"{device}-{random.randint(1000,9999)}"

    log(f"DEVICE #{i+1}", CYAN)

    print()

    log(f"Device Type : {device}", WHITE)
    log(f"Fake MAC    : {mac}", WHITE)
    log(f"Hostname    : {hostname}", WHITE)

    print()

    # Disconnect previous
    disconnect()

    # Identity spoofing
    set_hostname(hostname)
    set_mac(mac)

    print()

    # Connect
    success = connect()

    print()

    if success:
        log(f"Maintaining connection for {WAIT_TIME}s", CYAN)
        time.sleep(WAIT_TIME)

    else:
        log("Skipping wait due to failed connection", YELLOW)

    print()

    # Disconnect
    log("Disconnecting...", CYAN)
    disconnect()

    print()

    time.sleep(2)

print(f"{GREEN}Finished.{RESET}")
