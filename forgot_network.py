#!/usr/bin/env python3
import subprocess
import sys
import os
import re

def list_networks():
    """List saved network connections"""
    try:
        result = subprocess.run(['nmcli', 'connection', 'show'], capture_output=True, text=True)
        networks = []
        for line in result.stdout.split('\n'):
            if line.strip():
                networks.append(line.strip())
        return networks
    except:
        return []

def forget_network(network_name):
    """Remove/forget a saved network connection"""
    try:
        subprocess.run(['nmcli', 'connection', 'delete', network_name], check=True)
        print(f"Network '{network_name}' has been forgotten")
        return True
    except Exception as e:
        print(f"Error forgetting network: {e}")
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: python3 forget_network.py <network_name>")
        print("\nAvailable saved networks:")
        for network in list_networks():
            print(f"  {network}")
        return
    
    network_name = ' '.join(sys.argv[1:])  # Handle network names with spaces
    forget_network(network_name)

if __name__ == "__main__":
    main()
