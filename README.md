# Network Automation Toolkit (NAT)

**Network Automation Toolkit (NAT)** is a professional tool for **network scanning, device discovery, and gathering initial information** about network devices.  
This version represents the first milestone of the project and includes the following features.

---

## Features (Milestone 1)

- **Subnet Scanning**: Scan specified subnets to detect alive hosts.
- **SNMP Fingerprinting**: Retrieve hostname (`sysName`) and device description (`sysDescr`) from devices with SNMP enabled.
- **Timeout and Error Handling**: Devices without SNMP or unreachable hosts do not block the scanning process.
- **User-friendly CLI**: Clear console output with icons:
  - 🧠 → SNMP-enabled device  
  - ⚠️ → Device without SNMP
- **Parallel Scanning**: Uses `ThreadPoolExecutor` to speed up scanning multiple hosts simultaneously.
- **Future-proof Design**: Ready to add SSH banner fingerprinting or other discovery methods later.

---

## Challenges and Fixes

- Older `pysnmp` versions were incompatible with Python 3.12 → rewrote using `AsyncioDispatcher`.
- Asyncio issues were fixed to remove `No current event loop` and `Task was destroyed but it is pending` warnings.
- SNMP timeout and error handling improved to ensure scanning continues smoothly on hosts without SNMP.

---

## Prerequisites

Requires **Python >= 3.12** and the following packages:

```bash
pip install -r requirements.txt
Packages:
netaddr → subnet and IP management

requests → HTTP fingerprint (future use)

pysnmp → SNMP fingerprinting

paramiko → SSH banner fingerprinting

click → CLI interface

tqdm → progress bar (optional)

PyYAML → YAML config support (optional)

(Future) netmiko → executing commands via SSH on network devices

Usage
bash
Copy code
python cli.py discover 172.20.20.0/24 172.20.16.0/24 --threads 50
discover → main command to scan devices

subnets → one or more subnets to scan

--threads → number of threads (default: 50)

Sample Output
arduino
Copy code
🔍 Scanning subnet: 172.20.20.0/24
✅ Found 3 alive hosts
🧠 172.20.20.1 [SNMP] → Core-Mik3011 | RouterOS RB3011UiAS
------------------------------------------------------------
⚠️ 172.20.20.2 → Unknown device
------------------------------------------------------------
🔐 172.20.20.12 [SSH] → SSH-2.0-OpenSSH_9.6p1 Ubuntu-3ubuntu13.14 (Ubuntu Linux)
------------------------------------------------------------
🔍 Scanning subnet: 172.20.20.0/24
✅ Found 3 alive hosts
🧠 172.20.16.1 [SNMP] → Core-Mik3011 | RouterOS RB3011UiAS
------------------------------------------------------------
🔐 172.20.16.2 [SSH] → SSH-1.99-Cisco-1.25 (Cisco Network Device)
------------------------------------------------------------

Important Notes
If a device does not have SNMP enabled, its real hostname cannot be retrieved.

Later, other fingerprinting methods can be added:

SSH banners

NetBIOS / SMB

Reverse DNS / PTR

HTTP/HTTPS headers

The current architecture allows for easy extension of discovery methods and storage of device information.

Project Structure
Copy code
NAT/
├── cli.py
├── discovery/
│   ├── fingerprint.py
│   ├── parallel.py
│   ├── snmp.py
│   ├── ssh.py
│   └── subnet_scanner.py
├── requirements.txt
└── README.md
Milestone Summary
This commit/milestone establishes a stable foundation for:

Discovering network devices across subnets

Retrieving basic device information via SNMP

Handling network errors gracefully

Providing a clear CLI interface for users

