import socket
from typing import Optional, Dict


def ssh_banner_fingerprint(ip: str, timeout: float = 2.0) -> Optional[Dict]:
    """
    Read SSH banner without authentication
    """

    try:
        sock = socket.create_connection((ip, 22), timeout=timeout)
        sock.settimeout(timeout)

        banner = sock.recv(1024).decode(errors="ignore").strip()
        sock.close()

        if not banner.startswith("SSH-"):
            return None

        return {
            "ip": ip,
            "method": "ssh-banner",
            "banner": banner,
            "os": guess_os_from_banner(banner),
        }

    except Exception:
        return None


def guess_os_from_banner(banner: str) -> str:
    banner = banner.lower()

    if "ubuntu" in banner:
        return "Ubuntu Linux"
    if "debian" in banner:
        return "Debian Linux"
    if "centos" in banner:
        return "CentOS Linux"
    if "openssh" in banner:
        return "Generic Linux/Unix"
    if "mikrotik" in banner or "routeros" in banner:
        return "MikroTik RouterOS"
    if "cisco" in banner:
        return "Cisco Network Device"
    if "dropbear" in banner:
        return "Embedded Linux / Network Device"

    return "Unknown"

