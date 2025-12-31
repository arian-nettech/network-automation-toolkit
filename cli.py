import click

from discovery.subnet_scanner import scan_subnet
from discovery.parallel import parallel_snmp_scan


@click.group()
def cli():
    """Network Automation Toolkit"""
    pass


@cli.command()
@click.argument("subnets", nargs=-1)
@click.option("--threads", default=50, show_default=True)
@click.option("--snmp-workers", default=30, show_default=True)
@click.option("--community", default="public", show_default=True)
def discover(subnets, threads, snmp_workers, community):
    """Discover devices using ICMP + SNMP"""

    for subnet in subnets:
        click.echo(f"\n🔍 Scanning subnet: {subnet}")
        alive = scan_subnet(subnet, threads)

        if not alive:
            click.echo("❌ No alive hosts found")
            continue

        click.echo(f"✅ Found {len(alive)} alive hosts")

        results = parallel_snmp_scan(
            alive,
            workers=snmp_workers,
        )

    for r in results:
        if r.get("method") == "snmp":
            click.echo(
                f"🧠 {r['ip']} [SNMP] → {r['hostname']} | {r['description']}"
            )

        elif r.get("method") == "ssh-banner":
            click.echo(
                f"🔐 {r['ip']} [SSH] → {r['banner']} ({r['os']})"
            )

        else:
            click.echo(
                f"⚠️ {r['ip']} → Unknown device"
            )

        click.echo("-" * 60)


if __name__ == "__main__":
    cli()

