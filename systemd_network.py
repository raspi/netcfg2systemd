import ipaddress
from dataclasses import dataclass
from io import StringIO
from typing import List, Union


@dataclass
class NetworkMatch:
    """
    https://www.freedesktop.org/software/systemd/man/systemd.network.html#%5BMatch%5D%20Section%20Options
    """
    Name: str

    def __str__(self) -> str:
        o = StringIO()
        # Match
        o.write(
            '# https://www.freedesktop.org/software/systemd/man/systemd.network.html#%5BMatch%5D%20Section%20Options' + "\n")
        o.write('[Match]' + "\n")
        o.write('Name=' + self.Name + "\n")
        o.write("\n")

        return o.getvalue()


@dataclass
class NetworkNetwork:
    """
    https://www.freedesktop.org/software/systemd/man/systemd.network.html#%5BNetwork%5D%20Section%20Options
    """
    Description: str
    StaticIps: Union[List[ipaddress._IPAddressBase], None]
    VLANInterfaces: List[str]

    def __str__(self) -> str:
        o = StringIO()
        # Network
        o.write(
            '# https://www.freedesktop.org/software/systemd/man/systemd.network.html#%5BNetwork%5D%20Section%20Options' + "\n")
        o.write('[Network]' + "\n")
        o.write('Description=' + self.Description + "\n")
        o.write('# DHCP no|yes|ipv4|ipv6' + "\n")
        o.write('DHCP=no' + "\n")

        if self.StaticIps is not None:
            for i in self.StaticIps:
                o.write('Address=' + str(i['addr']) + '/' + str(i['plen']) + "\n")

        o.write('# VLAN interface(s)' + "\n")
        if len(self.VLANInterfaces) == 0:
            o.write('#VLAN=example0' + "\n")
            o.write('#VLAN=example1' + "\n")
        else:
            for i in self.VLANInterfaces:
                o.write('VLAN=' + i + "\n")

        o.write('#IPForward=yes' + "\n")
        o.write('IPMasquerade=no' + "\n")
        o.write('LinkLocalAddressing=no' + "\n")
        o.write('LLDP=no' + "\n")
        o.write("\n")

        return o.getvalue()

@dataclass
class NetworkRoute:
    """
    https://www.freedesktop.org/software/systemd/man/systemd.network.html#%5BRoute%5D%20Section%20Options
    """
    Gateway: ipaddress._IPAddressBase

    def __str__(self) -> str:
        o = StringIO()
        # Route
        o.write(
            '# https://www.freedesktop.org/software/systemd/man/systemd.network.html#%5BRoute%5D%20Section%20Options' + "\n")
        o.write('[Route]' + "\n")
        o.write('# Gateway IP address or _dhcp4, _dhcp6')
        o.write('Gateway=' + str(self.Gateway) + "\n")
        o.write('#GatewayOnLink=' + "\n")
        o.write('# Metric ' + "\n")
        o.write('#Metric=100' + "\n")
        o.write('# Scope "global", "site", "link", "host", or "nowhere":' + "\n")
        o.write('#Scope=' + "\n")
        o.write("\n")

        return o.getvalue()

@dataclass
class NetworkLink:
    """
    https://www.freedesktop.org/software/systemd/man/systemd.network.html#%5BLink%5D%20Section%20Options
    """

    def __str__(self) -> str:
        o = StringIO()
        o.write(
            '# https://www.freedesktop.org/software/systemd/man/systemd.network.html#%5BLink%5D%20Section%20Options' + "\n")
        o.write('[Link]' + "\n")
        o.write('RequiredForOnline=yes' + "\n")
        o.write('#ARP=no' + "\n")
        o.write('Multicast=no' + "\n")
        o.write('AllMulticast=no' + "\n")
        o.write('Unmanaged=no' + "\n")
        o.write('Promiscuous=no' + "\n")
        o.write("\n")
        return o.getvalue()


@dataclass
class Network:
    Match: NetworkMatch
    Network: NetworkNetwork
    Link: NetworkLink
    Route:NetworkRoute

    def __str__(self) -> str:
        o = StringIO()
        o.write(self.Match.__str__())
        o.write(self.Network.__str__())
        o.write(self.Route.__str__())
        o.write(self.Link.__str__())
        return o.getvalue()
