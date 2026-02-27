# To Do List ####################################################################################################

''' Replace ips.txt with a .csv with more information. i.e. IP, device type, site, etc. '''

''' When the above is done, change function to use the specific credential set based on the switch information in the .csv, rather than trying all 4 sets for each switch '''

#################################################################################################################

import os
import sys
import csv
import logging
from pathlib import Path
from datetime import datetime
from netmiko import ConnectHandler
from concurrent.futures import ThreadPoolExecutor, as_completed

current_time = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

# Note: Output folder path for configs, enter path before the {current_time} variable, this will create a new folder for each run of the script with the current date and time. 
folder = Path(rf"{current_time}_switch_backups")

# Note: the password fields are intentionally left blank, fill in the passwords between "" as needed.
procurve_switch = {
    "device_type": "hp_procurve",
    "username": "manager",
    "password": "",
    "ssh_strict": False,
    "timeout": 10,           
    "session_timeout": 30,   
    "auth_timeout": 10,      
    "banner_timeout": 10,     
}

cx_switch = {
    "device_type": "aruba_aoscx",
    "username": "admin",
    "password": "",
    "ssh_strict": False,
    "timeout": 10,           
    "session_timeout": 30,   
    "auth_timeout": 10,      
    "banner_timeout": 10, 
}

successful = 0
failed = 0

logging.basicConfig(filename=f"{current_time}.log", level=logging.INFO, format=f"[%(asctime)s] - [%(levelname)s] - %(message)s")
logging.getLogger("netmiko").setLevel(logging.WARNING)

logging.info(f"{'='*60}")
logging.info("Starting Switch Backup Script")
logging.info(f"Saving configs to: {folder}\n")

def load_devices_from_csv(filepath="ips.csv"):
    """Load device information from a CSV file.
    
    Reads the CSV file containing device IP addresses, OS types, and site names.
    Returns a list of dictionaries with keys: ip, os_type, site.
    """
    if not os.path.exists(filepath):
        logging.error(f"{filepath} file not found!")
        logging.error("Please create an ips.csv file with columns: ip, os_type, site")
        sys.exit(1)
    
    devices = []
    
    with open(filepath, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            devices.append({
                "ip": row["ip"].strip(),
                "os_type": row["os_type"].strip().lower(),
                "site": row["site"].strip()
            })
    
    return devices

def get_credentials_for_os(os_type):
    """Return the credential dictionary for a given OS type.
    
    Args:
        os_type: The OS type string (e.g., 'aruba_aoscx', 'aos-switch')
    
    Returns:
        A dictionary containing device credentials, or None if OS type is unknown.
    """
    os_creds = {
        "aruba_aoscx": cx_switch,
        "aos-switch": procurve_switch,
    }
    
    return os_creds.get(os_type)

def backup_config(device_info):
    """Connect to a switch and save its running configuration to a file.
    
    Connects to the device via SSH, retrieves the running configuration,
    and saves it to a file organized by site.
    
    Args:
        device_info: Dictionary containing ip, site, and device (connection details)
    
    Returns:
        True if backup succeeded, False otherwise.
    """
    connection = None
    ip = device_info["ip"]
    site = device_info["site"]

    try:
        connection = ConnectHandler(**device_info["device"])
        hostname = connection.find_prompt().strip('#').strip('>')
        config = connection.send_command("show running-config")
        site_folder = folder / site
        filename = f"{ip}_{hostname}_config.txt"
        full_path = site_folder / filename

        logging.info(f"Connected to {ip}")
        connection.disable_paging()
        site_folder.mkdir(parents=True, exist_ok=True)
        
        with open(full_path, "w") as file:
            file.write(config)
        
        logging.info(f"Configuration for {ip} ({hostname}) saved to {site}/{filename}")
        return True

    except Exception as e:
        logging.error(f"Unexpected error connecting to {ip}:\n{e}")
        return False
    
    finally:
        if connection:
            connection.disconnect()

def build_device_config(ip, os_type):
    """Build a complete device configuration dictionary for Netmiko.
    
    Combines the appropriate credentials for the OS type with the device IP.
    
    Args:
        ip: The IP address of the device
        os_type: The OS type of the device
    
    Returns:
        A dictionary with all connection details, or None if OS type is unknown.
    """
    creds = get_credentials_for_os(os_type)
    if creds is None:
        return None
    
    device = creds.copy()
    device["ip"] = ip
    return device


def process_switch(device_info):
    """Process a single switch: build config and attempt backup.
    
    Retrieves the appropriate credentials for the device OS type,
    then attempts to connect and back up the configuration.
    
    Args:
        device_info: Dictionary containing ip, os_type, and site
    
    Returns:
        Tuple of (ip, success, os_type) indicating result of backup attempt.
    """
    ip = device_info["ip"]
    os_type = device_info["os_type"]
    
    device = build_device_config(ip, os_type)
    if device is None:
        logging.error(f"Unknown OS type '{os_type}' for {ip}")
        return (ip, False, "Unknown OS")
    
    success = backup_config({**device_info, "device": device})
    return (ip, success, os_type if success else None)

device_list = load_devices_from_csv()
logging.info(f"Processing {len(device_list)} switches...\n")

with ThreadPoolExecutor(max_workers=30) as executor:
    future_to_device = {executor.submit(process_switch, device): device for device in device_list}
    
    for future in as_completed(future_to_device):
        ip, success, cred_type = future.result()
        if success:
            successful += 1
            continue
        failed += 1

logging.info(f"\n{'='*60}")
logging.info(f"Backup process complete!")
logging.info(f"[+] Successful: {successful}")
logging.info(f"[!] Failed: {failed}")
logging.info(f"Total: {len(device_list)}")
logging.info(f"{'='*60}\n")
