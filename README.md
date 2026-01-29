# Network Switch Configuration Backup Script
**Author:** Cam Roberts (Anthony James Consulting)
**Year:** 2026  
**Company:** Elis  

## Overview
Automated backup solution for Aruba network switch configurations across 33+ company sites and over 400 switches. Supports HP ProCurve and Aruba CX switches (and the ability for more compatibility) with threads & workers. Configurable IP range through .txt file.

## Features
- ✅ - 30* concurrent connections for fast backups
- ✅ - Designed to run as a scheduled task / cron job
- ✅ - Handles timeouts & auth failures
- ✅ - .Exe package to omit installing the dependencies

## Requirements
- A host machine that can handle 30* TCP connections & the small amount of disk space for the backups to go

### If Running Python Script
- Python 3.7+
- Netmiko library: `pip install netmiko` or `python3 -m pip install netmiko`
- Plain text file with just IP's on every new line, named "ips.txt"

### If Running Compiled EXE
- No Python installation required
- Windows 10/11 or Windows Server
- Plain text file with just IP's on every new line, named "ips.txt"

## File Structure
- Script automatically creates backup folder in the current working directory the script is ran in