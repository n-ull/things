#!/usr/bin/env python3
import subprocess
import sys
import os

def change_hostname(new_hostname):
    """Change the system hostname"""
    if os.geteuid() != 0:
        print("This script requires root privileges")
        return False
    
    try:
        # Change hostname temporarily
        subprocess.run(['hostname', new_hostname], check=True)
        
        # Update /etc/hostname
        with open('/etc/hostname', 'w') as f:
            f.write(new_hostname + '\n')
        
        # Update /etc/hosts
        with open('/etc/hosts', 'r') as f:
            hosts_content = f.read()
        
        # Replace old hostname with new one
        new_hosts_content = hosts_content.replace('127.0.1.1\t' + os.uname().nodename, 
                                                '127.0.1.1\t' + new_hostname)
        
        with open('/etc/hosts', 'w') as f:
            f.write(new_hosts_content)
        
        print(f"Hostname changed to: {new_hostname}")
        print("Changes will take full effect after reboot")
        return True
    except Exception as e:
        print(f"Error changing hostname: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: sudo python3 change_hostname.py <new_hostname>")
        return
    
    new_hostname = sys.argv[1]
    change_hostname(new_hostname)

if __name__ == "__main__":
    main()
