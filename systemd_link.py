from dataclasses import dataclass
from io import StringIO
from typing import Union


@dataclass
class LinkLink:
    """
    https://www.freedesktop.org/software/systemd/man/systemd.link.html#%5BLink%5D%20Section%20Options
    """

    Name: Union[str, None]  # Rename interface to this name
    Description: str
    MACAddressPolicy: str
    AutoNegotiation: str

    # Hardware offloading
    ReceiveChecksumOffload: bool
    TransmitChecksumOffload: bool
    TCPSegmentationOffload: bool
    TCP6SegmentationOffload: bool
    GenericSegmentationOffload: bool
    GenericReceiveOffload: bool
    LargeReceiveOffload: bool

    def __str__(self) -> str:
        o = StringIO()
        o.write(
            '# https://www.freedesktop.org/software/systemd/man/systemd.link.html#%5BLink%5D%20Section%20Options' + "\n")
        o.write('[Link]' + "\n")

        o.write('# Rename interface' + "\n")
        if self.Name is None:
            o.write("#")
        o.write('Name=')
        if self.Name is not None:
            o.write(self.Name)
        else:
            o.write("example0")
        o.write("\n")

        o.write('Description=' + self.Description + "\n")
        o.write('MACAddressPolicy=persistent' + "\n")
        o.write('AutoNegotiation=yes' + "\n")
        o.write("\n")
        o.write('# Disable NIC hardware offloading (because possible hw bugs)' + "\n")
        o.write('ReceiveChecksumOffload=no' + "\n")
        o.write('TransmitChecksumOffload=no' + "\n")
        o.write('TCPSegmentationOffload=no' + "\n")
        o.write('TCP6SegmentationOffload=no' + "\n")
        o.write('GenericSegmentationOffload=no' + "\n")
        o.write('GenericReceiveOffload=no' + "\n")
        o.write('LargeReceiveOffload=no' + "\n")

        return o.getvalue()


@dataclass
class LinkMatch:
    """
    https://www.freedesktop.org/software/systemd/man/systemd.network.html#%5BMatch%5D%20Section%20Options
    """

    interface: str
    MACAddress: Union[str, None] = None

    def __str__(self) -> str:
        o = StringIO()
        o.write(
            '# https://www.freedesktop.org/software/systemd/man/systemd.network.html#%5BMatch%5D%20Section%20Options' + "\n")
        o.write('[Match]' + "\n")
        o.write('MACAddress=' + self.MACAddress + "\n")
        o.write('#Name=' + self.interface + "\n")
        return o.getvalue()


@dataclass
class Link:
    Link: LinkLink
    Match: LinkMatch

    def __str__(self) -> str:
        o = StringIO()
        if self.Link.Name is not None:
            o.write('# Rename NIC with MAC address ' + self.Match.MACAddress + ' to ' + self.Link.Name + "\n")
        o.write(self.Match.__str__())
        o.write("\n")
        o.write(self.Link.__str__())
        return o.getvalue()
