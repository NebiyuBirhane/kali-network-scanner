import asyncio
import json
import subprocess
from scapy.all import ARP, Ether, srp

async def async_arp_sweep(target_cidr: str, delay: float = 0.05):
    """Performs a paced ARP sweep across any custom CIDR block."""
    discovered = {}

    # 1. Scapy live ARP sweep with adjustable timeout
    arp_req = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=target_cidr)
    try:
        ans, _ = await asyncio.to_thread(
            srp, arp_req, timeout=3, verbose=False
        )
        for sent, rcv in ans:
            discovered[rcv.psrc] = rcv.hwsrc
            # Small paced delay to avoid flooding the network interface
            await asyncio.sleep(delay)
    except Exception as e:
        print(f"Scapy error: {e}")

    # 2. Read Linux system ARP table for cached hosts
    try:
        proc = await asyncio.create_subprocess_exec(
            "ip", "neigh",
            stdout=subprocess.asyncio.subprocess.PIPE,
            stderr=subprocess.asyncio.subprocess.PIPE
        )
        stdout, _ = await proc.communicate()
        for line in stdout.decode().splitlines():
            parts = line.split()
            if len(parts) >= 5:
                ip = parts[0]
                mac = parts[4]
                if mac != "FAILED" and ip not in discovered:
                    discovered[ip] = mac
    except Exception as e:
        print(f"System ARP table read error: {e}")

    # Yield discovered hosts with stealth pacing
    for ip, mac in discovered.items():
        yield {
            "type": "host_discovered",
            "ip": ip,
            "mac": mac
        }
        await asyncio.sleep(delay)
