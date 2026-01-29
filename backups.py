# To Do List #

# Implement error logging, through either the logging module or netmiko logging
# Device / IP pulling from Netedit (I have no idea how to do this yet)

import os
import sys
from datetime import datetime
from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor, as_completed

print("\n[+] Starting Switch Configuration Backup Script...")

if not os.path.exists("ips.txt"):
    print("[!] ERROR: ips.txt file not found!")
    print("[!] Please create an ips.txt file with one IP address per line.")
    sys.exit(1)

# Convert ips.txt to list, may need to add regex version later or pull from Netedit...
with open("ips.txt", "r") as ip_list:
    ips = [line.strip() for line in ip_list]

folder = "SwitchBackups"

if not os.path.exists(folder):
    os.makedirs(folder)

os.chdir(folder)

print(f"[+] Folder {folder} already exists or has been created.")
print(f"[+] Changed working directory to {folder}.\n")

# Credential sets & other options for switches, see netmiko docs for details
procurve = {
    "device_type": "hp_procurve",
    "username": "manager",
    "password": "",
    "ssh_strict": False,
    "timeout": 10,           
    "session_timeout": 30,   
    "auth_timeout": 10,      
    "banner_timeout": 10,     
}

aruba_cx = {
    "device_type": "aruba_aoscx",
    "username": "admin",
    "password": "",
    "ssh_strict": False,
    "timeout": 10,           
    "session_timeout": 30,   
    "auth_timeout": 10,      
    "banner_timeout": 10, 
}

procurve_no_pass = {**procurve, "password": ""}   

aruba_cx_no_pass = {**aruba_cx, "password": ""}

credentials = [
        ("ProCurve", procurve),
        ("ProCurve no pass", procurve_no_pass),
        ("Aruba CX", aruba_cx),
        ("Aruba CX no pass", aruba_cx_no_pass)
    ]
# Function to back up config
def backup_config(device):
    net_connect = None

    try:
        net_connect = ConnectHandler(**device)
        net_connect.disable_paging()

        print(f"[+] Connected to {device['ip']}")

        hostname = net_connect.find_prompt().strip('#').strip('>')
        config = net_connect.send_command("show running-config")
        
        filename = f"{hostname}_config.txt"
        
        with open(filename, "w") as file:
            file.write(config)
        
        print(f"[+] Configuration for {device['ip']} ({hostname}) saved to {filename}")
        return True

    except Exception as e:
        print(f"{datetime.now()}: [!] Unexpected error connecting to {device['ip']}:\n{e}")
        return False
    # Ensure the connection is closed
    finally:
        if net_connect:
            net_connect.disconnect()

# Function process the switches with all the credentials, not sure if this is the best way but it works
def process_switch(ip):
    for cred_name, device_dict in credentials:
        device = device_dict.copy()
        device["ip"] = ip
        
        if backup_config(device):
            return (ip, True, cred_name)
    
    return (ip, False, None)

# How many workers to use in the thread pool
MAX_WORKERS = 30

print(f"[+] Starting backup process with {MAX_WORKERS} workers...")
print(f"[+] Processing {len(ips)} switches...\n")

successful = 0
failed = 0

with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
    future_to_ip = {executor.submit(process_switch, ip): ip for ip in ips}
    
    for future in as_completed(future_to_ip):
        ip, success, cred_type = future.result()
        if success:
            successful += 1
            continue
        failed += 1

# Print summary :D
print(f"\n{'='*60}")
print(f"[+] Backup process complete!")
print(f"[+] Successful: {successful}")
print(f"[!] Failed: {failed}")
print(f"[+] Total: {len(ips)}")
print(f"{'='*60}\n")