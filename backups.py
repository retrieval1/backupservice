# To Do List ####################################################################################################

''' Replace ips.txt with a .csv with more information. i.e. IP, device type, site, etc. '''

''' When the above is done, change function to use the specific credential set based on the switch information in the .csv, rather than trying all 4 sets for each switch '''

#################################################################################################################

import os
import sys
import logging
from pathlib import Path
from datetime import datetime
from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor, as_completed

logging.basicConfig(filename=f"{datetime.now().strftime('%Y-%m-%d')}.log", level=logging.INFO, format=f"[%(asctime)s] - [%(levelname)s] - %(message)s")

# Note: Output folder path for configs, change as needed
folder = Path(r"")

# Note: the password fields are intentionally left blank, as I don't want to share any credentials. Fill in the passwords as needed.
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

logging.info(f"{'='*60}")
logging.info("Starting Switch Backup Script")
logging.info(f"Saving configs to: {folder}\n")

if not os.path.exists("ips.txt"):
    logging.error("ips.txt file not found!")
    logging.error("Please create an ips.txt file with one IP address per line.")
    sys.exit(1)

# Convert ips.txt to useable list
with open("ips.txt", "r") as ip_list:
    ips = [line.strip() for line in ip_list]

# Function to back up config
def backup_config(device):
    net_connect = None

    try:
        net_connect = ConnectHandler(**device)
        net_connect.disable_paging()

        logging.info(f"Connected to {device['ip']}")

        hostname = net_connect.find_prompt().strip('#').strip('>')
        config = net_connect.send_command("show running-config")

        directory = Path(folder)
        directory.mkdir(parents=True, exist_ok=True)
        filename = f"{hostname}_config.txt"
        full_path = directory / filename
        
        with open(full_path, "w") as file:
            file.write(config)
        
        logging.info(f"Configuration for {device['ip']} ({hostname}) saved to {filename}")
        return True

    except Exception as e:
        logging.error(f"Unexpected error connecting to {device['ip']}:\n{e}")
        return False
    # Ensure the connection is closed
    finally:
        if net_connect:
            net_connect.disconnect()

# Function to process the switches with all the credentials, this may be changed in the future to use specific credentials based on the information in the .csv file, but for now it just tries all 4 sets of credentials for each switch until it finds one that works.
def process_switch(ip):
    for cred_name, device_dict in credentials:
        device = device_dict.copy()
        device["ip"] = ip
        
        if backup_config(device):
            return (ip, True, cred_name)
    
    return (ip, False, None)

# How many workers to use in the thread pool
MAX_WORKERS = 30

logging.info(f"Starting backup process with {MAX_WORKERS} workers...")
logging.info(f"Processing {len(ips)} switches...\n")

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
logging.info(f"\n{'='*60}")
logging.info(f"Backup process complete!")
logging.info(f"[+] Successful: {successful}")
logging.info(f"[!] Failed: {failed}")
logging.info(f"Total: {len(ips)}")
logging.info(f"{'='*60}\n")
