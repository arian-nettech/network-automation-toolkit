from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import List, Dict

from discovery.snmp import snmp_fingerprint
from discovery.ssh import ssh_banner_fingerprint


def safe_fingerprint(ip: str, community="public"):
    try:
        # 1️⃣ SNMP
        snmp = snmp_fingerprint(ip, community, timeout=3)
        if snmp:
            snmp["method"] = "snmp"
            return snmp

        # 2️⃣ SSH Banner
        ssh = ssh_banner_fingerprint(ip)
        if ssh:
            return ssh

        return {
            "ip": ip,
            "method": "unknown",
            "status": "no-snmp-no-ssh"
        }

    except Exception as e:
        return {
            "ip": ip,
            "method": "error",
            "error": str(e)
        }

def parallel_snmp_scan(
    ips: List[str],
    workers: int = 30,
) -> List[Dict]:

    results = []

    with ThreadPoolExecutor(max_workers=workers) as executor:
        futures = {
            executor.submit(safe_fingerprint, ip): ip
            for ip in ips
        }

        # 🔥 اینجا واقعاً تا پایان همه jobها صبر می‌کند
        for future in as_completed(futures):
            res = future.result()
            results.append(res)

    return results

