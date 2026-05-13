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

    # =====================================================
    # APPLE
    # =====================================================

    "iPhone 8": [
        "F0:18:98",
        "AC:BC:32",
        "D0:03:4B"
    ],

    "iPhone X": [
        "3C:06:30",
        "B4:F0:AB",
        "14:7D:DA"
    ],

    "iPhone 11": [
        "70:73:CB",
        "A4:CF:12",
        "FC:E9:98"
    ],

    "iPhone 12": [
        "58:FB:84",
        "D8:96:95",
        "F4:34:F0"
    ],

    "iPhone 13": [
        "20:EA:47",
        "9C:20:7B",
        "40:98:AD"
    ],

    "iPhone 14": [
        "E0:2B:E9",
        "5C:E9:31",
        "A8:51:AB"
    ],

    "iPhone 15": [
        "44:00:10",
        "34:15:9E",
        "7C:04:D0"
    ],

    # =====================================================
    # SAMSUNG
    # =====================================================

    "Samsung Galaxy S8": [
        "38:2D:E8",
        "A8:9C:ED",
        "64:BC:0C"
    ],

    "Samsung Galaxy S9": [
        "FC:C2:DE",
        "2C:8A:72",
        "44:91:60"
    ],

    "Samsung Galaxy S10": [
        "68:27:19",
        "CC:07:AB",
        "34:23:87"
    ],

    "Samsung Galaxy S20": [
        "50:2D:F4",
        "8C:F1:12",
        "74:45:CE"
    ],

    "Samsung Galaxy S21": [
        "30:07:4D",
        "A0:C9:A0",
        "E8:50:8B"
    ],

    "Samsung Galaxy S22": [
        "9C:8D:1A",
        "7C:61:93",
        "BC:20:A4"
    ],

    "Samsung Galaxy S23": [
        "54:13:79",
        "98:F1:70",
        "24:4B:FE"
    ],

    "Samsung Galaxy S24": [
        "18:47:3D",
        "D4:53:83",
        "84:25:19"
    ],

    "Samsung Galaxy A10": [
        "3C:BD:D8",
        "8C:71:F8",
        "5C:F3:70"
    ],

    "Samsung Galaxy A20": [
        "F8:A9:D0",
        "68:EB:C5",
        "00:07:AB"
    ],

    "Samsung Galaxy A30": [
        "E4:7D:BD",
        "28:39:5E",
        "D8:5B:2A"
    ],

    "Samsung Galaxy A50": [
        "10:1D:C0",
        "A4:14:37",
        "64:A2:F9"
    ],

    "Samsung Galaxy A51": [
        "94:B0:1F",
        "20:13:E0",
        "48:F1:7F"
    ],

    "Samsung Galaxy A52": [
        "04:FE:7F",
        "6C:2F:2C",
        "84:DB:AC"
    ],

    "Samsung Galaxy A53": [
        "C8:FF:28",
        "F0:25:B7",
        "A0:91:69"
    ],

    "Samsung Galaxy A54": [
        "D0:17:C2",
        "38:AA:3C",
        "50:F5:DA"
    ],

    # =====================================================
    # XIAOMI
    # =====================================================

    "Xiaomi Redmi Note 8": [
        "64:09:80",
        "50:8F:4C",
        "28:6C:07"
    ],

    "Xiaomi Redmi Note 9": [
        "78:11:DC",
        "1C:CC:D6",
        "FC:64:BA"
    ],

    "Xiaomi Redmi Note 10": [
        "20:47:DA",
        "BC:54:36",
        "7C:49:EB"
    ],

    "Xiaomi Redmi Note 11": [
        "DC:3E:F8",
        "F4:29:81",
        "D4:1B:81"
    ],

    "Xiaomi Redmi Note 12": [
        "A4:77:33",
        "B8:87:1E",
        "E0:DC:FF"
    ],

    "Xiaomi Poco X3": [
        "58:44:98",
        "EC:D0:9F",
        "84:08:0A"
    ],

    "Xiaomi Poco X5": [
        "7C:1D:D9",
        "48:5F:99",
        "B4:EA:2B"
    ],

    # =====================================================
    # MOTOROLA
    # =====================================================

    "Moto G7": [
        "9C:4F:DA",
        "00:1A:11",
        "F8:63:3F"
    ],

    "Moto G8": [
        "40:78:6A",
        "D8:37:3B",
        "24:DA:9B"
    ],

    "Moto G9": [
        "54:AE:27",
        "70:5A:B6",
        "A8:96:75"
    ],

    "Moto G20": [
        "A4:CF:99",
        "8C:B8:7E",
        "48:21:0B"
    ],

    "Moto G52": [
        "E8:6A:64",
        "BC:92:6B",
        "44:74:6C"
    ],

    "Motorola Edge 30": [
        "20:82:C0",
        "6C:D9:19",
        "B0:68:E6"
    ],

    # =====================================================
    # HUAWEI
    # =====================================================

    "Huawei P20": [
        "C8:D1:2A",
        "E0:19:1D",
        "F4:4E:FD"
    ],

    "Huawei P30": [
        "68:A0:F6",
        "9C:28:EF",
        "00:E0:FC"
    ],

    "Huawei Mate 20": [
        "10:51:72",
        "D4:94:E8",
        "78:F8:82"
    ],

    # =====================================================
    # GOOGLE PIXEL
    # =====================================================

    "Google Pixel 5": [
        "94:EB:CD",
        "D8:3A:DD",
        "A0:B4:A5"
    ],

    "Google Pixel 6": [
        "7C:2E:DD",
        "CC:F9:E4",
        "90:9A:4A"
    ],

    "Google Pixel 7": [
        "48:D7:05",
        "A0:CE:C8",
        "58:CB:52"
    ],

    # =====================================================
    # ONEPLUS
    # =====================================================

    "OnePlus 8": [
        "88:C9:D0",
        "10:68:3F",
        "F0:79:60"
    ],

    "OnePlus 9": [
        "BC:DD:C2",
        "3C:28:6D",
        "A8:9A:93"
    ],

    "OnePlus 11": [
        "60:01:94",
        "84:C7:EA",
        "FC:73:FB"
    ],

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
