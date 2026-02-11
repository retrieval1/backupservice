# **Backup Service**

Automated backup solution for Aruba network switch configurations across 33+ company sites and over 400 switches.

# **Purpose**: 
Creates backups of switch configurations that cannot be managed by Aruba Central or otherwise. This script ensures that in event of a switch failure or replacement, a new one can take it's place with the same configuration with little downtime.

## **Overview**:

**Directory Creation & Naming**

The folder variable is set as `folder = Path(r"{current_time}_switch_backups")`, this will create it where you run the script, please add in the full path for where you want the backups to go and leave the existing portion at the end.

**Directory Creation**

`folder.mkdir(parents=True, exist_ok=True)` ensures the directory exists before writing files.

**Logging**

Logging is set up to write to a file named with the current date and time.
All major steps and errors are logged in a file where the script is ran.

**Parallel Processing**

Uses ThreadPoolExecutor to process multiple switches in parallel, with a configurable worker count.
Credentials Handling

Tries all credential sets for each switch until one works. Currently...

**Summary**

Logs a summary of successful and failed backups in the log file

## **Requirements**:
- Python 3.8+ (recommended)
- `netmiko` (for SSH connections)
- Read/write permissions

Install dependencies:

`pip install netmiko
`

## **Configuration**:
- `ips.txt`: Place in the same directory as the script. One IP address per line.
- Credentials: Edit the credential dictionaries in `backups.py` to set `username` and `password` for your devices.
- Output folder: Set the `folder` variable in `backups.py` (currently `folder = Path(r"{current_time}_switch_backups")`) to the directory where you want configs saved. Example: `folder = Path(r"\\server\directory\{current_time}_switch_backups")` or an absolute path.
- Adjust timeouts and other SSH options in the device dictionaries as needed.

**Usage**:

- Linux/macOS: use `cron` to run the script periodically.
- Windows: use Task Scheduler

**Troubleshooting**:
- If `ips.txt` is missing, the script exits with an error. You can see this, along with other errors, in the log file.
- Connection errors are printed with a timestamp; verify reachability, credentials, and device SSH settings.

**Security**:
- Avoid hard-coding plaintext passwords in versioned files. Consider using environment variables, a secure vault, or an encrypted credentials file and edit the device parameters accordingly to use those instead of the plaintext strings.

**Suggested Improvements**:
- Replace `ips.txt` with a CSV to include device type/credential mapping and reduce credential guessing.
- Add a `pyproject.toml` for reproducible installs.
- Add optional notification on failure (email).

Please create an issue or pull request for any suggested improvements.
