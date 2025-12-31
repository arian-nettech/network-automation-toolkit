import ipaddress
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed


def ping(ip: str, timeout=1) -> bool:
    """
    Ping a single IP address.
    """
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "-W", str(timeout), ip],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return result.returncode == 0
    except Exception:
        return False


def scan_subnet(cidr: str, threads: int = 50) -> list[str]:
    """
    Scan a subnet and return alive hosts.
    """
    network = ipaddress.ip_network(cidr, strict=False)
    alive_hosts = []

    with ThreadPoolExecutor(max_workers=threads) as executor:
        futures = {
            executor.submit(ping, str(ip)): str(ip)
            for ip in network.hosts()
        }

        for future in as_completed(futures):
            ip = futures[future]
            if future.result():
                alive_hosts.append(ip)

    return alive_hosts

