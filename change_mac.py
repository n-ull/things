#!/usr/bin/env python3
import subprocess
import sys
import os
import re
import random

def validate_mac(mac):
    """Validate MAC address format"""
    pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
    return bool(pattern.match(mac))

def generate_random_mac():
    """Generate a random MAC address"""
    # Common OUIs for various manufacturers
    ouis = [
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
    
    # Choose a random OUI or generate a completely random one
    if random.random() < 0.7:  # 70% chance to use a real manufacturer OUI
        oui = random.choice(ouis)
    else:  # 30% chance to use a completely random OUI
        oui = "%02x:%02x:%02x" % (
            random.randint(0, 255),
            random.randint(0, 255),
            random.randint(0, 255)
        )
    
    # Generate the rest of the MAC address
    return "%s:%02x:%02x:%02x" % (
        oui,
        random.randint(0, 255),
        random.randint(0, 255),
        random.randint(0, 255)
    )

def change_mac(interface, new_mac):
    """Change MAC address of a network interface"""
    if os.geteuid() != 0:
        print("This script requires root privileges")
        return False
    
    if not validate_mac(new_mac):
        print("Invalid MAC address format. Use format like: AA:BB:CC:DD:EE:FF")
        return False
    
    try:
        # Bring down the interface
        subprocess.run(['ip', 'link', 'set', interface, 'down'], check=True)
        
        # Change MAC address
        subprocess.run(['ip', 'link', 'set', interface, 'address', new_mac], check=True)
        
        # Bring up the interface
        subprocess.run(['ip', 'link', 'set', interface, 'up'], check=True)
        
        print(f"MAC address of {interface} changed to: {new_mac}")
        return True
    except Exception as e:
        print(f"Error changing MAC address: {e}")
        return False

def list_interfaces():
    """List available network interfaces"""
    try:
        result = subprocess.run(['ip', 'link', 'show'], capture_output=True, text=True)
        interfaces = []
        for line in result.stdout.split('\n'):
            if ': ' in line and not line.startswith(' '):
                parts = line.split(': ')
                if len(parts) >= 2:
                    interface = parts[1].split('@')[0]  # Remove VLAN info if present
                    if interface != 'lo':  # Skip loopback
                        interfaces.append(interface)
        return interfaces
    except:
        return []

def get_current_mac(interface):
    """Get the current MAC address of an interface"""
    try:
        result = subprocess.run(['ip', 'link', 'show', interface], capture_output=True, text=True)
        for line in result.stdout.split('\n'):
            if 'link/ether' in line:
                return line.split('link/ether ')[1].split(' ')[0]
        return None
    except:
        return None

def main():
    if len(sys.argv) < 2:
        print("Usage: sudo python3 change_mac.py <interface> [new_mac]")
        print("\nAvailable interfaces:")
        for interface in list_interfaces():
            current_mac = get_current_mac(interface)
            print(f"  {interface}: {current_mac if current_mac else 'Unknown'}")
        return
    
    interface = sys.argv[1]
    
    # Check if interface exists
    if interface not in list_interfaces():
        print(f"Interface '{interface}' not found")
        return
    
    # Get current MAC
    current_mac = get_current_mac(interface)
    print(f"Current MAC address of {interface}: {current_mac}")
    
    # Generate or use provided MAC
    if len(sys.argv) >= 3:
        new_mac = sys.argv[2]
        if not validate_mac(new_mac):
            print("Invalid MAC address format. Use format like: AA:BB:CC:DD:EE:FF")
            return
    else:
        new_mac = generate_random_mac()
        print(f"Generated random MAC address: {new_mac}")
    
    # Change MAC address
    change_mac(interface, new_mac)

if __name__ == "__main__":
    main()
