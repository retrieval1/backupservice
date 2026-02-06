**Backup Service**

Automated backup solution for Aruba network switch configurations across 33+ company sites and over 400 switches.

**Overview**:
- **Purpose**: Connects to a list of network devices (one IP per line in `ips.txt`) and saves the running configuration for each device to a local folder.
- **Concurrency**: Uses a thread pool (`ThreadPoolExecutor`) with a configurable `MAX_WORKERS` (default `30`) to process devices in parallel.

**Requirements**:
- Python 3.8+ (recommended)
- `netmiko` (for SSH connections)

Install dependencies:

```bash
pip install netmiko
```

**Configuration**:
- `ips.txt`: Place in the same directory as the script. One IP address per line.
- Credentials: Edit the credential dictionaries in `backups.py` to set `username` and `password` for your devices. The script cycles through multiple credential sets until one succeeds.
- Output folder: Set the `folder` variable in `backups.py` (currently `folder = Path(r"")`) to the directory where you want configs saved. Example: `folder = Path("configs")` or an absolute path.
- Adjust timeouts and other SSH options in the device dictionaries as needed.

**Usage**:

```bash
python backups.py
```

The script prints a brief summary at the end showing successful and failed backups.

**Scheduling**:
- Linux/macOS: use `cron` to run the script periodically.
- Windows: use Task Scheduler

**Troubleshooting**:
- If `ips.txt` is missing, the script exits with an error.
- Connection errors are printed with a timestamp; verify reachability, credentials, and device SSH settings.
- Consider replacing print statements with Python's `logging` module for production/scheduled runs.

**Security**:
- Avoid hard-coding plaintext passwords in versioned files. Consider using environment variables, a secure vault, or an encrypted credentials file.

**Suggested Improvements**:
- Replace `ips.txt` with a CSV to include device type/credential mapping and reduce credential guessing.
- Add a `requirements.txt` or `pyproject.toml` for reproducible installs.
- Add optional notification on failure (email).
