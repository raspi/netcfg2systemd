import argparse
import ipaddress
import json
import logging
import os
from tempfile import NamedTemporaryFile

import sys
from datetime import datetime
from io import BytesIO
from os import path
from select import select
from subprocess import Popen, PIPE
from typing import List, BinaryIO, Union

from systemd_link import *

from systemd_network import *


def _run_command(cmd: List[str], target: BinaryIO, errtarget: BinaryIO):
    runcmd = ['stdbuf', '-oL', '-e0']
    runcmd.extend(cmd)

    with Popen(runcmd, stdout=PIPE, stderr=PIPE) as p:
        readable = {
            p.stdout.fileno(): target,
            p.stderr.fileno(): errtarget,
        }

        while readable:
            for fd in select(readable, [], [], 10.0)[0]:
                data = os.read(fd, 8192)
                if not data:  # EOF
                    del readable[fd]
                else:
                    readable[fd].write(data)
                    readable[fd].flush()


if __name__ == '__main__':
    THIS = path.basename(sys.argv[0])
    EXAMPLES = [
    ]

    log = logging.getLogger(__name__)

    logging.basicConfig(
        format='%(asctime)s [%(levelname)s]: %(message)s',
        stream=sys.stdout,
        level=logging.INFO,
    )

    parser = argparse.ArgumentParser(
        usage=f'{THIS} ' +
              "\n  " +
              "\n  ".join(EXAMPLES),
        epilog='',
    )

    parser.add_argument('-i', '--interface', dest='iface', type=str, required=True)
    parser.add_argument('-r', '--rename', dest='newifacename', type=str, required=False,
                        help='Rename interface name to given name, for example lan0')
    parser.add_argument('-P', '--priority', dest='priority', type=int, required=False, default=10,
                        help='Priority for .link file')
    parser.add_argument('--vlan', dest='vlan', type=str, required=False, default='',
                        help='VLAN interface(s) for example: "lan0,wan0"')

    args = parser.parse_args()

    mac_address: Union[str, None] = None

    with open(f'/sys/class/net/{args.iface}/address') as f:
        mac_address: str = f.read().strip()

    if mac_address is None:
        print("could not get MAC address from interface")
        sys.exit(1)

    out = BytesIO()
    _run_command(['ip', '-json', '-details', 'route', 'list', 'dev', args.iface, 'default'], out, sys.stderr.buffer)
    route = json.loads(out.getvalue())
    gw: ipaddress._IPAddressBase = ipaddress.ip_address(route[0]['gateway'])

    out = BytesIO()
    _run_command(['ip', '-json', '-details', 'address', 'show', 'dev', args.iface], out, sys.stderr.buffer)
    addresses = json.loads(out.getvalue())

    # Interface IP address(es)
    ips: list = []

    for dev in addresses:
        for i in dev['addr_info']:
            ips.append(
                {
                    'addr': ipaddress.ip_address(i['local']),
                    'plen': i['prefixlen'],
                }
            )

    now = datetime.now()

    # .link

    dotLink = Link(
        Link=LinkLink(
            Name=args.newifacename,
            Description='Ethernet port N',
            MACAddressPolicy='persistent',
            AutoNegotiation='yes',
            ReceiveChecksumOffload=False,
            TransmitChecksumOffload=False,
            TCPSegmentationOffload=False,
            TCP6SegmentationOffload=False,
            GenericSegmentationOffload=False,
            GenericReceiveOffload=False,
            LargeReceiveOffload=False,
        ),
        Match=LinkMatch(
            MACAddress=mac_address,
            interface=args.iface,
        ),
    )

    vlans = []

    if ',' in args.vlan:
        vlans = args.vlan.split(",")
    elif args.vlan != '':
        vlans = [args.vlan]

    # .network

    dotNetwork = Network(
        Match=NetworkMatch(
            Name=args.iface
        ),
        Network=NetworkNetwork(
            Description='Network for ' + args.iface,
            StaticIps=ips,
            VLANInterfaces=vlans,
        ),
        Route=NetworkRoute(
            Gateway=gw,
        ),
        Link=NetworkLink(
        ),
    )

    print("##### .link:")

    # Save to temporary file
    tmpf = NamedTemporaryFile("w", prefix="", suffix=".link", encoding="utf8", delete=False)
    with tmpf as f:
        f.write(str(dotLink))
        f.flush()
        print(f"Saved {args.priority}-{args.iface}.link as {f.name}")
        print(f"cat {f.name}")
        print(f"cp {f.name} /etc/systemd/network/{args.priority}-{args.iface}.link")

    print()
    print("##### .network:")

    # Save to temporary file
    tmpf = NamedTemporaryFile("w", prefix="", suffix=".network", encoding="utf8", delete=False)
    with tmpf as f:
        f.write(str(dotNetwork))
        f.flush()
        print(f"Saved {args.iface}.network as {f.name}")
        print(f"cat {f.name}")
        print(f"cp {f.name} /etc/systemd/network/{args.iface}.network")
