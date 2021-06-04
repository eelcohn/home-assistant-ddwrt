"""Class for querying DD-WRT routers"""

from datetime import date
import logging
import re
import ssl
import urllib3
from OpenSSL import crypto
from datetime import datetime
from requests import Session
from requests.exceptions import Timeout, ConnectionError, SSLError

_LOGGER = logging.getLogger(__name__)
_VERSION = "0.9.2"
_X_REQUESTED_WITH = __name__ + "-" + _VERSION
HTTP_X_REQUESTED_WITH = "X-Requested-With"

CONF_TRACK_ARP = "arp_clients"
CONF_TRACK_DHCP = "dhcp_clients"
CONF_TRACK_PPPOE = "pppoe_clients"
CONF_TRACK_PPTP = "pptp_clients"
CONF_TRACK_WDS = "wds_clients"
CONF_TRACK_WIRELESS = "wireless_clients"

DEFAULT_TIMEOUT = 4

ENDPOINT_ABOUT = "About.htm"
ENDPOINT_APPLY = "apply.cgi"
ENDPOINT_AOSS = "AOSS.live.asp"
ENDPOINT_CONNTRACK = "Status_Conntrack.asp"
ENDPOINT_DDNS = "DDNS.live.asp"
ENDPOINT_FREERADIUS = "FreeRadius.live.asp"
ENDPOINT_TTGRAPH = "ttgraph.cgi"
ENDPOINT_INTERNET = "Status_Internet.live.asp"
ENDPOINT_NETWORKING = "Networking.live.asp"
ENDPOINT_STATUSINFO = "Statusinfo.live.asp"
ENDPOINT_LAN = "Status_Lan.live.asp"
ENDPOINT_ROUTER_STATIC = "Status_Router.asp"
ENDPOINT_ROUTER = "Status_Router.live.asp"
ENDPOINT_SPUTNIK = "Status_SputnikAPD.live.asp"
ENDPOINT_WIRELESS = "Status_Wireless.live.asp"
ENDPOINT_UPNP = "UPnP.live.asp"
ENDPOINT_USB = "USB.live.asp"
REBOOT_PARAMETERS = {
    'submit_button': 'Management',
    'action': 'Reboot',
    'change_action': '',
    'submit_type': '',
}
RUN_COMMAND_PARAMETERS = {
    'submit_button': 'Ping',
    'action': 'ApplyTake',
    'submit_type': 'start',
    'change_action': 'gozila_cgi',
    'ping_ip': '',
}
UPNP_DELETE_PARAMETERS = {
    'submit_button': 'UPnP',
    'action': 'Apply',
    'change_action': '',
    'submit_type': '',
    'remove': '',
}
WOL_PARAMETERS = {
    'submit_button': 'Ping',
    'action': 'Apply',
    'submit_type': 'wol',
    'change_action': 'gozila_cgi',
    'manual_wol_mac': '',
    'manual_wol_network': '',
    'manual_wol_port': '',
}
WAN_RELEASE_PARAMETERS = {
    'submit_button': 'Status_Internet',
    'action': 'Apply',
    'change_action': 'gozila_cgi',
    'submit_type': 'release',
}
WAN_RENEW_PARAMETERS = {
    'submit_button': 'Status_Internet',
    'action': 'Apply',
    'change_action': 'gozila_cgi',
    'submit_type': 'renew',
}
WAN_CONNECT_PPPOE_PARAMETERS = {
    'submit_button': 'Status_Internet',
    'action': 'Apply',
    'change_action': 'gozila_cgi',
    'submit_type': 'Connect_pppoe',
}
WAN_DISCONNECT_PPPOE_PARAMETERS = {
    'submit_button': 'Status_Internet',
    'action': 'Apply',
    'change_action': 'gozila_cgi',
    'submit_type': 'Disconnect_pppoe',
}
WIFI_SELECT_INTERFACE_PARAMETERS = {
    'submit_button': 'Status_Wireless',
#    'next_page': 'Status_Wireless.asp',
    'change_action': 'gozila_cgi',
    'submit_type': 'refresh',
    'wifi_display': 'wl0',
}

_DDWRT_DATA_REGEX = re.compile(r"\{(\w+)::([^\}]*)\}")


class DDWrt:
    """This class queries a wireless router running DD-WRT firmware."""

    def __init__(self, aio_session, host, username, password, protocol, verify_ssl):
        """Initialize the DD-WRT class."""

        self._aio_session = aio_session
        self._host = host
        self._username = username
        self._password = password
        self._protocol = protocol
        self._verify_ssl = verify_ssl

        self.data = None
        self.results = {}
        self.clients_arp = {}
        self.clients_dhcp = {}
        self.clients_pppoe = {}
        self.clients_pptp = {}
        self.clients_wds = {}
        self.clients_wireless = {}
        self.upnp_forwards = {}

        self._session = Session()


    def update_about_data(self):
        """Gets firmware version info from the DD-WRT router"""

        _LOGGER.debug("DDWrt.update_about_data: Updating about data...")

        url = f"{self._protocol}://{self._host}/{ENDPOINT_ABOUT}"

        try:
            self.data = self._get_ddwrt_data(url, False)
        except Exception as e:
#            pass
            raise(DDWrt.DDWrtException("Unable to update about data: %s", e))
            return None

        if not self.data:
            return False

        # Get firmware info
        firmware = self.data.partition("DD-WRT v")[2].split("<br />")[0]
        self.results.update({"sw_version": firmware.split("-r")[0]})
        self.results.update({"sw_build": firmware.split("-r")[1].split(" ")[0]})
        self.results.update({"sw_date": firmware.split("(")[1].split(")")[0]})

        url = f"{self._protocol}://{self._host}/{ENDPOINT_ROUTER_STATIC}"

        try:
            self.data = self._get_ddwrt_data(url, False)
        except Exception as e:
#            pass
            raise(DDWrt.DDWrtException("Unable to update router model data: %s", e))
            return None

        if not self.data:
            return False

        # Get router model
        router_model = self.data.partition("Capture(status_router.sys_model)</script></div>")[2].split("</div>")[0].split(" ", 1)
        self.results.update({"router_manufacturer": router_model[0]})
        self.results.update({"router_model": router_model[1]})

        _LOGGER.debug("DDWrt::update_about_data results=%s", self.results)

        return True


    def update_wan_data(self):
        """Gets WAN info from the DD-WRT router"""

        _LOGGER.debug("DDWrt.update_router_data: Updating WAN data...")

        # Get data from internet endpoint
        url = f"{self._protocol}://{self._host}/{ENDPOINT_INTERNET}"
        try:
            self.data = self._get_ddwrt_data(url, True)
        except Exception as e:
            raise(DDWrt.DDWrtException("Unable to update WAN data: %s", e))
            return None

        if not self.data:
            return False

        # Get WAN info
        self.results.update({"wan_3g_signal": self.data.pop("wan_3g_signal").split(" ")[0]})
        if self.results["wan_3g_signal"].lower() == "n.a.":
            self.results.update({"wan_3g_signal": None})
        self._get_parameter("wan_dhcp_remaining", "dhcp_remaining")
        self._get_parameter("wan_dns0", "wan_dns0")
        self._get_parameter("wan_dns1", "wan_dns1")
        self._get_parameter("wan_dns2", "wan_dns2")
        self._get_parameter("wan_dns3", "wan_dns3")
        self._get_parameter("wan_dns4", "wan_dns4")
        self._get_parameter("wan_dns5", "wan_dns5")
        self._get_parameter("wan_gateway", "wan_gateway")
        self._get_parameter("wan_ipaddr", "wan_ipaddr")
        if "wan_ipv6addr" in self.data:
            self.results.update({"wan_ip6addr": self.data.pop("wan_ipv6addr")})
            del self.data["ipinfo"]
        else:
            if "IPv6" in self.data.get("ipinfo", None):
                self.results.update({"wan_ip6addr": self.data.pop("ipinfo").split("IPv6:")[1].strip()})
            else:
                del self.data["ipinfo"]
                self.results.update({"wan_ip6addr": None})
        self._get_parameter("wan_netmask", "wan_netmask")
        self._get_parameter("wan_pppoe_ac_name", "pppoe_ac_name")
        self._get_parameter("wan_proto", "wan_shortproto")
        self._get_parameter("wan_traffic_in", "ttraff_in")
        self._get_parameter("wan_traffic_out", "ttraff_out")
        self.results.update({"wan_status": self.data.pop("wan_status").strip().split("&nbsp;")[0]})
        self.results.update({"wan_connected": True if self.results["wan_status"]  == "Connected" else False})
        self.results.update({"wan_uptime": self.data.pop("wan_uptime").strip().split(",  ")[0]})

        del self.data["uptime"]
        if self.data:
            _LOGGER.warning("Extra fields in WAN data found. Please contact developer to report this warning. (%s)", self.data)

        return True


    def update_router_data(self):
        """Gets router info from the DD-WRT router"""

        _LOGGER.debug("DDWrt.update_router_data: Updating router data...")

        # Get data from router endpoint
        url = f"{self._protocol}://{self._host}/{ENDPOINT_ROUTER}"
        try:
            self.data = self._get_ddwrt_data(url, True)
        except Exception as e:
            raise(DDWrt.DDWrtException("Unable to update router data: %s", e))
            return None

        if not self.data:
            return False

        # Get router info
        cpu_temp = None
        if self.data.get("cpu_temp", None).strip() != "":
            if self.data.get("cpu_temp", None).strip() != "Not available":
                cpu_temp = {}
                for item in self.data.get("cpu_temp", None).split("/"):
                    cpu_temp.update({item.strip().split(" ")[0]: float(item.strip().split(" ")[1])})
        del self.data["cpu_temp"]
        self.results.update({"cpu_temp":        cpu_temp})

        uptime = self.data.get("uptime", None).split(",  ")[0].split(" up ")[1].strip()
        load_average1  = self.data.get("uptime", None).split("load average:")[1].split(",")[0].strip()
        load_average5  = self.data.get("uptime", None).split("load average:")[1].split(",")[1].strip()
        load_average15 = self.data.get("uptime", None).split("load average:")[1].split(",")[2].strip()
        self.results.update({"uptime":          uptime})
        self.results.update({"load_average1":   load_average1})
        self.results.update({"load_average5":   load_average5})
        self.results.update({"load_average15":  load_average15})

        # Add data to the _results array
        self._get_parameter("clk_freq", "clkfreq")
        self._get_parameter("ip_connections", "ip_conntrack")
        self._get_parameter("router_time", "router_time")
        self.results.update({"voltage":         self.data.pop("voltage").strip().split(" ")[0]})
        if "voltage" in self.data:
            if self.data["voltage"] == '':
                self.results.update({"voltage":     None})
            else:
                self.results.update({"voltage":     self.data.pop("voltage").strip().split(" ")[0]})
        else:
            self.results.update({"voltage":     None})
#                self.results["voltage"] = float(self.results["voltage"])
        nvram = self.data.pop("nvram", None).split(" / ")
        self.results.update({"nvram_used":     nvram[0].split(" ")[0]})
        self.results.update({"nvram_total":     nvram[1].split(" ")[0]})

        # TODO: mem_info isn't implemented in pyddwrt yet
        del self.data["mem_info"]
        del self.data["uptime"]
        del self.data["ipinfo"]
        if self.data:
            _LOGGER.warning("Extra fields in router data found. Please contact developer to report this warning. (%s)", self.data)

        return True


    def update_network_data(self):
        """Gets Networking info from the DD-WRT router"""

        _LOGGER.debug("DDWrt.update_network_data: Updating Networking data...")

        # Get data from networking endpoint
        url = f"{self._protocol}://{self._host}/{ENDPOINT_NETWORKING}"
        try:
            self.data = self._get_ddwrt_data(url, True)
        except Exception as e:
            raise(DDWrt.DDWrtException("Unable to update networking data: %s", e))
            return None

        if not self.data:
            return False

        # Get Networking info
        network_bridges = [item.strip("'").strip() for item in self.data.pop("bridges_table").split(",")]

        self.results.update({"network_bridges": network_bridges})

        del self.data["uptime"]
        del self.data["ipinfo"]
        if self.data:
            _LOGGER.warning("Extra fields in networking data found. Please contact developer to report this warning. (%s)", self.data)

        return True


    def update_wireless_data(self):
        """Gets wireless info from the DD-WRT router"""

        _LOGGER.debug("DDWrt.update_wireless_data: Updating wireless data...")

        url = f"{self._protocol}://{self._host}/{ENDPOINT_WIRELESS}"
        try:
            self.data = self._get_ddwrt_data(url, True)
        except Exception as e:
            raise(DDWrt.DDWrtException("Unable to update wireless data: %s", e))
            return None

        if not self.data:
            return False

        # Get wireless info
        wl_ack = self.data.pop("wl_ack")
        if wl_ack and not wl_ack == "":
            self.results.update({"wl_ack_timing": wl_ack.split("&#181;")[0]})
            self.results.update({"wl_ack_distance": wl_ack.split("(")[1].split("m")[0]})
        else:
            self.results.update({"wl_ack_timing": None})
            self.results.update({"wl_ack_distance": None})
        self._get_parameter("wl_active", "wl_active")
        self._get_parameter("wl_busy", "wl_busy")
        self._get_parameter("wl_channel", "wl_channel")
        self._get_parameter("wl_count", "assoc_count")
        self._get_parameter("wl_mac", "wl_mac")
        self._get_parameter("wl_quality", "wl_quality")
        self.results.update({"wl_radio": True if self.data.pop("wl_radio").strip().split(" ")[2]  == "On" else False})
        self.results.update({"wl_rate": self.data.pop("wl_rate").split(" ")[0]})
        self._get_parameter("wl_ssid", "wl_ssid")
        self.results.update({"wl_xmit": self.data.pop("wl_xmit").split(" ")[0]})
        if self.results["wl_xmit"] == "Radio":
            self.results.update({"wl_xmit": None})

        # Get wireless packet info
        packet_info = self.data.pop("packet_info")

        if packet_info:
            elements = dict((key.strip(), value.strip()) for key, value in (item.split('=') for item in packet_info.strip(';').split(';')))

            wl_rx_packet_error = elements.get("SWRXerrorPacket", None)
            wl_rx_packet_ok = elements.get("SWRXgoodPacket", None)
            wl_tx_packet_error = elements.get("SWTXerrorPacket", None)
            wl_tx_packet_ok = elements.get("SWTXgoodPacket", None)

            self.results.update({"wl_rx_packet_error": wl_rx_packet_error})
            self.results.update({"wl_rx_packet_ok": wl_rx_packet_ok})
            self.results.update({"wl_tx_packet_error": wl_tx_packet_error})
            self.results.update({"wl_tx_packet_ok": wl_tx_packet_ok})
        else:
            self.results.update({"wl_rx_packet_error": None})
            self.results.update({"wl_rx_packet_ok": None})
            self.results.update({"wl_tx_packet_error": None})
            self.results.update({"wl_tx_packet_ok": None})


        # Get wireless clients
        active_clients = self.data.pop("active_wireless", None)

        if active_clients:
            self.clients_wireless = {}
            elements = [item.strip().strip("'") for item in active_clients.strip().split(",")]
            if (len(elements) != 0) and ((len(elements) % 11) == 0):
                # Wireless elements: MAC Address | Radioname | Interface | Uptime | Tx rate | Rx rate | Info | Signal | Noise | SNR | Signal Quality
                for i in range(0, len(elements), 11):
                    self.clients_wireless.update( {
                        elements[i]: {
                            "name": elements[i + 1],
                            "type": CONF_TRACK_WIRELESS,
                            "ap_mac": self.results["wl_mac"],
                            "radioname": elements[i + 1],
                            "interface": elements[i + 2],
                            "uptime": elements[i + 3],
                            "tx_rate": elements[i + 4],
                            "rx_rate": elements[i + 5],
                            "info": elements[i + 6],
                            "signal": elements[i + 7],
                            "noise": elements[i + 8],
                            "snr": elements[i + 9],
                            "signal_quality": elements[i + 10],
                        }
                    }
                )
            else:
                _LOGGER.warning("update_wireless_data(): invalid number of elements in active_wireless (expected 11, found %i)", len(elements))

        _LOGGER.debug("DDWrt.update_wireless_data: Wireless clients: %s", self.clients_wireless)

        # Get WDS clients
        active_clients = self.data.pop("active_wds", None)

        if active_clients:
            self.clients_wds = {}
            elements = [item.strip().strip("'") for item in active_clients.strip().split(",")]
            if (len(elements) != 0) and ((len(elements) % 7) == 0):
                # WDS elements: MAC Address | Interface | Description | Signal | Noise | SNR | Signal Quality
                for i in range(0, len(elements), 7):
                    _LOGGER.info("interface=%s", elements[i+4])
                    self.clients_wds.update( {
                        elements[i]: {
                            "name": elements[i + 2],
                            "type": CONF_TRACK_WDS,
                            "interface": elements[i + 1],
                            "description": elements[i + 2],
                            "signal": elements[i + 3],
                            "noise": elements[i + 4],
                            "snr": elements[i + 5],
                            "signal_quality": elements[i + 6],
                        }
                    }
                )
            else:
                _LOGGER.warning("update_wireless_data(): invalid number of elements in active_wds (expected 7, found %i)", len(elements))

        _LOGGER.debug("DDWrt.update_wireless_data: WDS clients: %s", self.clients_wds)

        del self.data["uptime"]
        del self.data["ipinfo"]
        if self.data:
            _LOGGER.warning("Extra fields in wireless data found. Please contact developer to report this warning. (%s)", self.data)

        return True


    def update_lan_data(self):
        """Gets LAN info from the DD-WRT router"""

        _LOGGER.debug("DDWrt.update_lan_data: Updating LAN data...")

        url = f"{self._protocol}://{self._host}/{ENDPOINT_LAN}"
        try:
            self.data = self._get_ddwrt_data(url, True)
        except Exception as e:
            raise(DDWrt.DDWrtException("Unable to update LAN data: %s", e))
            return None

        if not self.data:
            return False

        # Get LAN info
        if "lan_ip_prefix" in self.data:
            dhcp_prefix = self.data.pop("lan_ip_prefix")
            dhcp_start = self.data.pop("dhcp_start")
            lan_dhcp_start = "{}{}".format(dhcp_prefix, dhcp_start)
            lan_dhcp_end = "{}{}".format(dhcp_prefix, int(dhcp_start)+int(self.data.pop("dhcp_num"))-1)
        else:
            lan_dhcp_start = self.data.pop("dhcp_start")
            lan_dhcp_end = self.data.pop("dhcp_end")
            del self.data["dhcp_num"]
        self.results.update({"lan_dhcp_start": lan_dhcp_start})
        self.results.update({"lan_dhcp_end": lan_dhcp_end})

        self._get_parameter("lan_dhcp_daemon", "dhcp_daemon")
        self._get_parameter("lan_dhcp_lease_time", "dhcp_lease_time")

        self._get_parameter("lan_dns", "lan_dns")
        self._get_parameter("lan_gateway", "lan_gateway")
        self._get_parameter("lan_ipaddr", "lan_ip")
        self._get_parameter("lan_mac", "lan_mac")
        self._get_parameter("lan_netmask", "lan_netmask")
        self._get_parameter("lan_proto", "lan_proto")

        # Get clients from ARP table
        active_clients = self.data.pop("arp_table", None)
        if active_clients:
            elements = [item.strip().strip("'") for item in active_clients.strip().split(",")]

            # ARP elements: Hostname | IP Address | MAC Address | Connections (| Interface)
            self.clients_arp = {}

            # Check if this specific router returns the interface in the ARP list
            if len(elements) % 4 == 0:
                items_per_element = 4
                interface = None
            elif len(elements) % 5 == 0:
                items_per_element = 5
            else:
                _LOGGER.warning("update_lan_data(): invalid number of elements in arp_table (expected 4 or 5, found %i)", len(elements))

            for i in range(0, len(elements), items_per_element):
                if items_per_element == 5:
                    interface = elements[i + 4]

                self.clients_arp.update( {
                    elements[i + 2]: {
                        "name": elements[i],
                        "type": CONF_TRACK_ARP,
                        "ip": elements[i + 1],
                        "hostname": elements[i],
                        "connections": elements[i + 3],
                        "interface": interface
                    }
                }
            )

        _LOGGER.debug("DDWrt.update_lan_data: ARP clients: %s", self.clients_arp)

        # Get clients from DHCP leases
        active_clients = self.data.pop("dhcp_leases", None)
        if active_clients:
            self.clients_dhcp = {}
            elements = [item.strip().strip("'") for item in active_clients.strip().split(",")]

            # DHCP elements: Hostname | IP Address | MAC Address | Lease Expiration
            if (len(elements) != 0) and ((len(elements) % 5) == 0):
                for i in range(0, len(elements), 5):
                    self.clients_dhcp.update( {
                        elements[i + 2]: {
                            "name": elements[i],
                            "type": CONF_TRACK_DHCP,
                            "ip": elements[i + 1],
                            "hostname": elements[i],
                            "lease_expiration": elements[i + 3]
                        }
                    }
                )
            else:
                _LOGGER.warning("update_lan_data(): invalid number of elements in dhcp_leases (expected 5, found %i)", len(elements))

        _LOGGER.debug("DDWrt.update_lan_data: DHCP clients: %s", self.clients_dhcp)

        # Get clients from PPPoE leases
        active_clients = self.data.pop("pppoe_leases", None)
        if active_clients:
            self.clients_pppoe = {}
            elements = [item.strip().strip("'") for item in active_clients.strip().split(",")]

            # PPPoE elements: Interface | Username | Local IP
            if (len(elements) != 0) and ((len(elements) % 3) == 0):
                for i in range(0, len(elements), 3):
                    self.clients_pppoe.update( {
                        elements[i + 2]: {
                            "name": elements[i + 1],
                            "type": CONF_TRACK_PPPOE,
                            "interface": elements[i],
                            "username": elements[i + 1],
                            "local_ip": elements[i + 2]
                       }
                    }
                )
            else:
                _LOGGER.warning("update_lan_data(): invalid number of elements in pppoe_leases (expected 3, found %i)", len(elements))

        _LOGGER.debug("DDWrt.update_lan_data: PPPoE clients: %s", self.clients_pppoe)

        # Get clients from PPTP leases
        active_clients = self.data.pop("pptp_leases", None)
        if active_clients:
            self.clients_pptp = {}
            elements = [item.strip().strip("'") for item in active_clients.strip().split(",")]

            # PPTP elements: Interface | Username | Local IP | Remote IP
            if (len(elements) != 0) and ((len(elements) % 4) == 0):
                for i in range(0, len(elements), 4):
                    self.clients_pptp.update( {
                        elements[i + 2]: {
                            "name": elements[i + 1],
                            "type": CONF_TRACK_PPTP,
                            "interface": elements[i],
                            "username": elements[i + 1],
                            "local_ip": elements[i + 2],
                            "remote_ip": elements[i + 3]
                        }
                    }
                 )
            else:
                _LOGGER.warning("update_lan_data(): invalid number of elements in pptp_leases (expected 4, found %i)", len(elements))

        _LOGGER.debug("DDWrt.update_lan_data: PPTP clients: %s", self.clients_pptp)

        del self.data["uptime"]
        del self.data["ipinfo"]
        if self.data:
            _LOGGER.warning("Extra fields in LAN data found. Please contact developer to report this warning. (%s)", self.data)

        return True


    def update_upnp_data(self):
        """Gets UPNP info from the DD-WRT router"""

        _LOGGER.debug("DDWrt.update_upnp_data: Updating UPNP data...")

        url = f"{self._protocol}://{self._host}/{ENDPOINT_UPNP}"
        try:
            self.data = self._get_ddwrt_data(url, True)
        except Exception as e:
            raise(DDWrt.DDWrtException("Unable to update UPNP data: %s", e))
            return None

        if not self.data:
            return False

        # Get UPNP forwards
        upnp_data = self.data.pop("upnp_forwards", None)

        if upnp_data:
            self.upnp_forwards = {}
            elements = [item.strip().strip("'") for item in upnp_data.strip().split(",")]

            _LOGGER.debug("DDWrt.update_upnp_data: UPNP len=%s elements=%s", len(elements), elements)

            # UPNP forwards:  WAN start port-WAN end port>LAN IP address:LAN start port-LAN end port | Protocol | Enabled | Name
            if (len(elements) != 0) and ((len(elements) % 4) == 0):
                for i in range(0, len(elements), 4):
                    if elements[i] != '':
                        upnp_temp = re.split('[->:]+', elements[i])
                        self.upnp_forwards.update( {
                            elements[i + 3]: {
                                "name": elements[i + 3],
                                "wan_port_start": upnp_temp[0],
                                "wan_port_end": upnp_temp[1],
                                "lan_port_start": upnp_temp[3],
                                "lan_port_end": upnp_temp[4],
                                "lan_ip": upnp_temp[2],
                                "protocol": elements[i + 1],
                                "enabled": elements[i + 2],
                            }
                        }
                )
            else:
                _LOGGER.warning("update_upnp_data(): invalid number of elements in pptp_leases (expected 4, found %i)", len(elements))

        _LOGGER.debug("DDWrt.update_upnp_data: UPNP forwards: %s", self.upnp_forwards)

        del self.data["uptime"]
        del self.data["ipinfo"]
        if self.data:
            _LOGGER.warning("Extra fields in UPNP data found. Please contact developer to report this warning. (%s)", self.data)

        return True


    def wan_dhcp_release(self):
        """Releases the DHCP lease from the WAN interface."""

        url = f"{self._protocol}://{self._host}/{ENDPOINT_APPLY}"

        try:
            self.data = self._post_ddwrt_data(url, WAN_RELEASE_PARAMETERS)
        except Exception as e:
            _LOGGER.debug("DDWrt.wan_dhcp_release: Unable to send WAN DHCP release command.")
            raise(DDWrt.DDWrtException("Unable to send WAN DHCP release command: %s", e))

        if not self.data:
            _LOGGER.debug("DDWrt.wan_dhcp_release: Unable to release DHCP lease from WAN interface (no data returned).")
            raise(DDWrt.DDWrtException("Unable to release DHCP lease from WAN interface (no data returned)"))

        _LOGGER.debug("DDWrt.wan_dhcp_release: succes.")
        return True


    def wan_dhcp_renew(self):
        """Renews the DHCP lease for the WAN interface."""

        url = f"{self._protocol}://{self._host}/{ENDPOINT_APPLY}"

        try:
            self.data = self._post_ddwrt_data(url, WAN_RENEW_PARAMETERS)
        except Exception as e:
            _LOGGER.debug("DDWrt.wan_dhcp_renew: Unable to send WAN DHCP renew command.")
            raise(DDWrt.DDWrtException("Unable to send WAN DHCP renew command: %s", e))

        if not self.data:
            _LOGGER.debug("DDWrt.wan_dhcp_renew: Unable to renew DHCP lease from WAN interface (no data returned).")
            raise(DDWrt.DDWrtException("Unable to renew DHCP lease from WAN interface (no data returned)"))

        _LOGGER.debug("DDWrt.wan_dhcp_renew: succes.")
        return True


    def wan_pppoe_connect(self):
        """Connects the PPPoE WAN interface."""

        _LOGGER.debug("DDWrt.wan_pppoe_connect: Connecting PPPoE WAN interface...")

        url = f"{self._protocol}://{self._host}/{ENDPOINT_APPLY}"

        try:
            self.data = self._post_ddwrt_data(url, WAN_CONNECT_PPPOE_PARAMETERS)
        except Exception as e:
            _LOGGER.debug("DDWrt.pppoe_connect: Unable to send PPPoE WAN connect command.")
            raise(DDWrt.DDWrtException("Unable to send PPPoE WAN connect command: %s", e))

        if not self.data:
            _LOGGER.debug("DDWrt.pppoe_connect: Unable to connect from WAN PPPoE interface (no data returned).")
            raise(DDWrt.DDWrtException("Unable to connect from WAN PPPoE interface (no data returned)"))

        _LOGGER.debug("DDWrt.pppoe_disconnect: succes.")
        return True


    def wan_pppoe_disconnect(self):
        """Disconnects the PPPoE WAN interface."""

        _LOGGER.debug("DDWrt.wan_pppoe_disconnect: Disconnecting PPPoE WAN interface...")

        url = f"{self._protocol}://{self._host}/{ENDPOINT_APPLY}"

        try:
            self.data = self._post_ddwrt_data(url, WAN_DISCONNECT_PPPOE_PARAMETERS)
        except Exception as e:
            _LOGGER.debug("DDWrt.pppoe_disconnect: Unable to send PPPoE WAN disconnect command.")
            raise(DDWrt.DDWrtException("Unable to send PPPoE WAN disconnect command: %s", e))

        if not self.data:
            _LOGGER.debug("DDWrt.pppoe_disconnect: Unable to disconnect from WAN PPPoE interface (no data returned).")
            raise(DDWrt.DDWrtException("Unable to disconnect from WAN PPPoE interface (no data returned)"))

        _LOGGER.debug("DDWrt.pppoe_disconnect: succes.")
        return True


    def run_command(self, commands):
        """Execute a command on the router."""

        commands = commands.replace(' ', '+')
        commands = commands.replace('=', '%3D')
        commands = commands.replace('\n', '%0A')
        commands = commands.replace('\r', '%0D')

        url = f"{self._protocol}://{self._host}/{ENDPOINT_APPLY}"

        parameters = RUN_COMMAND_PARAMETERS.update({'ping_ip': commands})

        try:
            self.data = self._post_ddwrt_data(url, parameters)
        except Exception as e:
            _LOGGER.debug("DDWrt.run_command: Unable to send run_command.")
            raise(DDWrt.DDWrtException("Unable to send reboot command: %s", e))
            return None

        if not self.data:
            _LOGGER.debug("DDWrt.run_command: Rebooting router failed (no data returned).")
            raise(DDWrt.DDWrtException("Unable to run command (no data returned)"))

        _LOGGER.debug("DDWrt.run_command: succes.")
        return True


    def upnp_delete(self, rule='all'):
        """Delete an UPnP rule on the router."""

        url = f"{self._protocol}://{self._host}/{ENDPOINT_APPLY}"

        parameters = UPNP_DELETE_PARAMETERS.update({'remove': rule})

        try:
            self.data = self._post_ddwrt_data(url, parameters)
        except Exception as e:
            _LOGGER.debug("DDWrt.run_command: Unable to send upnp_delete.")
            raise(DDWrt.DDWrtException("Unable to send UPnP delete command: %s", e))
            return None

        if not self.data:
            _LOGGER.debug("DDWrt.run_command: Deleting UPnP rule failed (no data returned).")
            raise(DDWrt.DDWrtException("Unable to delete UPnP rule (no data returned)"))

        _LOGGER.debug("DDWrt.upnp_delete: succes.")
        return True


    def wake_on_lan(self, mac, network, port):
        """Perform a Wake-On-Lan on the router."""

        url = f"{self._protocol}://{self._host}/{ENDPOINT_APPLY}"

        parameters = RUN_COMMAND_PARAMETERS.update({
            'manual_wol_mac': mac,
            'manual_wol_network': network,
            'manual_wol_port': port,
        })

        try:
            self.data = self._post_ddwrt_data(url, parameters)
        except Exception as e:
            _LOGGER.debug("DDWrt.wake_on_lan: Unable to send Wake-On-Lan.")
            raise(DDWrt.DDWrtException("Unable to send Wake-On-Lan command: %s", e))
            return None

        if not self.data:
            _LOGGER.debug("DDWrt.wake_on_lan: Wake-On-Lan failed (no data returned).")
            raise(DDWrt.DDWrtException("Unable to run Wake-On-Lan (no data returned)"))

        _LOGGER.debug("DDWrt.wake_on_lan: succes.")
        return True


    def reboot(self):
        """Reboots the router."""

        url = f"{self._protocol}://{self._host}/{ENDPOINT_APPLY}"

        try:
            self.data = self._post_ddwrt_data(url, REBOOT_PARAMETERS)
        except Exception as e:
            _LOGGER.debug("DDWrt.reboot: Rebooting router failed.")
            raise(DDWrt.DDWrtException("Unable to send reboot command: %s", e))
            return None

        if not self.data:
            _LOGGER.debug("DDWrt.reboot: Rebooting router failed (no data returned).")
            raise(DDWrt.DDWrtException("Rebooting router failed (no data returned)"))

        _LOGGER.debug("DDWrt.reboot: succes.")
        return True


    def traffic_graph_url(self, convert):
        """Returns an URL to a traffic graph"""

        month = date.today().month
        year = date.today().year
        url = f"{self._protocol}://{self._host}/{ENDPOINT_TTGRAPH}?{month}-{year}"

        if convert:
            _LOGGER.debug("DDWrt.traffic_graph_url: Returning traffic graph image for %s", url)
            return _get_ddwrt_image(url)
        else:
            _LOGGER.debug("DDWrt.traffic_graph_url: Returning traffic graph URL: %s", url)
            return url


    # Make a GET request to the router
    def _get_ddwrt_data(self, url, convert):
        """Make a GET request to a DD-WRT router and return parsed result."""

        _LOGGER.debug("DDWrt._get_ddwrt_data: Connecting to %s", url)

        # Disable warning on not verifying the certificate
        if not self._verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        try:
            response = self._session.get(
                url = url,
                auth = (self._username, self._password),
                headers = {HTTP_X_REQUESTED_WITH: _X_REQUESTED_WITH},
                timeout = DEFAULT_TIMEOUT,
                verify = self._verify_ssl,
            )
        except urllib3.exceptions.InsecureRequestWarning as e:
            _LOGGER.debug("DDWrt._get_ddwrt_data: Cannot verify certificate")
            raise(DDWrt.ExceptionCannotVerify(e))

        except SSLError as e:
            errmsg = str(e)

            # Check for hostname mismatch error
            if errmsg.startswith("hostname"):
                _LOGGER.debug("DDWrt._get_ddwrt_data: SSLError hostname mismatch")
                raise(DDWrt.ExceptionHostnameMismatch(e))

            # Get certificate from the router
            try:
                raw_cert = ssl.get_server_certificate((self._host, 443))
            except Exception as e:
                _LOGGER.debug("DDWrt._get_ddwrt_data: SSLError unknown error")
                raise(DDWrt.ExceptionSSLError(e))

            # Check for valid date in certificate
            x509 = crypto.load_certificate(crypto.FILETYPE_PEM, raw_cert)
            now = datetime.now()
            not_after = datetime.strptime(x509.get_notAfter().decode('utf-8'), "%Y%m%d%H%M%SZ")
            not_before = datetime.strptime(x509.get_notBefore().decode('utf-8'), "%Y%m%d%H%M%SZ")
            if now > not_after or now < not_before:
                _LOGGER.debug("DDWrt._get_ddwrt_data: SSLError invalid date")
                raise(DDWrt.ExceptionInvalidDate(e))

            # Return self-signed error
            _LOGGER.debug("DDWrt._get_ddwrt_data: SSLError self signed")
            raise(DDWrt.ExceptionSelfSigned(e))

        except ConnectionError as e:
            _LOGGER.debug("DDWrt._get_ddwrt_data: ConnectionError")
            raise(DDWrt.ExceptionConnectionError(e))

        except Timeout as e:
            _LOGGER.debug("DDWrt._get_ddwrt_data: Timeout")
            raise(DDWrt.ExceptionTimeout(e))

        except Exception as e:
            _LOGGER.debug("DDWrt._get_ddwrt_data: Unable to connect to the router Connection error: %s", e)
            raise(DDWrt.ExceptionUnknown(e))

        # Valid response
        if response.status_code == 200:
            if response.text:
                if convert:
                    result = dict(_DDWRT_DATA_REGEX.findall(response.text))
                else:
                    result = response.text
                _LOGGER.debug("DDWrt._get_ddwrt_data: received data: %s", result)
                return result
            else:
                _LOGGER.debug("DDWrt._get_ddwrt_data: Received empty response querying %s", url)
                raise(DDWrt.ExceptionEmptyResponse())

        # Authentication error
        if response.status_code == 401:
            _LOGGER.debug("DDWrt._get_ddwrt_data: Failed to authenticate, please check your username and password")
            raise(DDWrt.ExceptionAuthenticationError())

        # Unknown HTTP error
        _LOGGER.debug("DDWrt._get_ddwrt_data: Invalid HTTP status code %s", response)
        raise(DDWrt.ExceptionHTTPError(response.status_code))


    # Make a POST request to the router
    def _post_ddwrt_data(self, url, data):
        """Make a POST request to a DD-WRT router."""

        _LOGGER.debug("DDWrt._post_ddwrt_data: Connecting to %s", url)

        # Disable warning on not verifying the certificate
        if not self._verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        try:
            response = self._session.post(
                url = url,
                auth = (self._username, self._password),
                data = data,
                headers = {HTTP_X_REQUESTED_WITH: _X_REQUESTED_WITH},
                timeout = DEFAULT_TIMEOUT,
                verify = self._verify_ssl,
            )
        except urllib3.exceptions.InsecureRequestWarning as e:
            _LOGGER.debug("DDWrt._post_ddwrt_data: Cannot verify certificate")
            raise(DDWrt.ExceptionCannotVerify(e))

        except SSLError as e:
            errmsg = str(e)

            # Check for hostname mismatch error
            if errmsg.startswith("hostname"):
                _LOGGER.debug("DDWrt._post_ddwrt_data: SSLError hostname mismatch")
                raise(DDWrt.ExceptionHostnameMismatch(e))

            # Get certificate from the router
            try:
                raw_cert = ssl.get_server_certificate((self._host, 443))
            except Exception as e:
                _LOGGER.debug("DDWrt._post_ddwrt_data: SSLError unknown error")
                raise(DDWrt.ExceptionSSLError(e))

            # Check for valid date in certificate
            x509 = crypto.load_certificate(crypto.FILETYPE_PEM, raw_cert)
            now = datetime.now()
            not_after = datetime.strptime(x509.get_notAfter().decode('utf-8'), "%Y%m%d%H%M%SZ")
            not_before = datetime.strptime(x509.get_notBefore().decode('utf-8'), "%Y%m%d%H%M%SZ")
            if now > not_after or now < not_before:
                _LOGGER.debug("DDWrt._post_ddwrt_data: SSLError invalid date")
                raise(DDWrt.ExceptionInvalidDate(e))

            # Return self-signed error
            _LOGGER.debug("DDWrt._post_ddwrt_data: SSLError self signed")
            raise(DDWrt.ExceptionSelfSigned(e))

        except ConnectionError as e:
            _LOGGER.debug("DDWrt._post_ddwrt_data: ConnectionError")
            raise(DDWrt.ExceptionConnectionError(e))

        except Timeout as e:
            _LOGGER.debug("DDWrt._post_ddwrt_data: Timeout")
            raise(DDWrt.ExceptionTimeout(e))

        except Exception as e:
            _LOGGER.debug("DDWrt._post_ddwrt_data: Unable to connect to the router Connection error: %s", e)
            raise(DDWrt.ExceptionUnknown(e))

        # Valid response
        if response.status_code == 200:
            _LOGGER.debug("DDWrt._post_ddwrt_data: Received valid response for %s", url)
            return True

        # Authentication error
        if response.status_code == 401:
            _LOGGER.debug("DDWrt._post_ddwrt_data: Failed to authenticate, please check your username and password")
            raise(DDWrt.ExceptionAuthenticationError())

        # Unknown HTTP error
        _LOGGER.debug("DDWrt._post_ddwrt_data: Invalid HTTP status code %s", response)
        raise(DDWrt.ExceptionHTTPError(response.status_code))


    # Return an image from the router by making a GET request
    def _get_ddwrt_image(self, url):
        """Make a GET request to a DD-WRT router and return parsed result."""

        _LOGGER.debug("DDWrt._get_ddwrt_image: Connecting to %s", url)

        # Disable warning on not verifying the certificate
        if not self._verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        try:
            response = self._session.get(
                url = url,
                auth = (self._username, self._password),
                headers = {HTTP_X_REQUESTED_WITH: _X_REQUESTED_WITH},
                timeout = DEFAULT_TIMEOUT,
                verify = self._verify_ssl,
            )
        except urllib3.exceptions.InsecureRequestWarning as e:
            _LOGGER.debug("DDWrt._get_ddwrt_image: Cannot verify certificate")
            raise(DDWrt.ExceptionCannotVerify(e))

        except SSLError as e:
            errmsg = str(e)

            # Check for hostname mismatch error
            if errmsg.startswith("hostname"):
                _LOGGER.debug("DDWrt._get_ddwrt_image: SSLError hostname mismatch")
                raise(DDWrt.ExceptionHostnameMismatch(e))

            # Get certificate from the router
            try:
                raw_cert = ssl.get_server_certificate((self._host, 443))
            except Exception as e:
                _LOGGER.debug("DDWrt._get_ddwrt_image: SSLError unknown error")
                raise(DDWrt.ExceptionSSLError(e))

            # Check for valid date in certificate
            x509 = crypto.load_certificate(crypto.FILETYPE_PEM, raw_cert)
            now = datetime.now()
            not_after = datetime.strptime(x509.get_notAfter().decode('utf-8'), "%Y%m%d%H%M%SZ")
            not_before = datetime.strptime(x509.get_notBefore().decode('utf-8'), "%Y%m%d%H%M%SZ")
            if now > not_after or now < not_before:
                _LOGGER.debug("DDWrt._get_ddwrt_image: SSLError invalid date")
                raise(DDWrt.ExceptionInvalidDate(e))

            # Return self-signed error
            _LOGGER.debug("DDWrt._get_ddwrt_image: SSLError self signed")
            raise(DDWrt.ExceptionSelfSigned(e))

        except ConnectionError as e:
            _LOGGER.debug("DDWrt._get_ddwrt_image: ConnectionError")
            raise(DDWrt.ExceptionConnectionError(e))

        except Timeout as e:
            _LOGGER.debug("DDWrt._get_ddwrt_image: Timeout")
            raise(DDWrt.ExceptionTimeout(e))

        except Exception as e:
            _LOGGER.debug("DDWrt._get_ddwrt_image: Unable to connect to the router Connection error: %s", e)
            raise(DDWrt.ExceptionUnknown(e))

        # Valid response
        if response.status_code == 200:
            if response.content:
                _LOGGER.debug("DDWrt._get_ddwrt_image: received image")
                return response.content
            else:
                _LOGGER.debug("DDWrt._get_ddwrt_image: Received empty response querying %s", url)
                raise(DDWrt.ExceptionEmptyResponse())

        # Authentication error
        if response.status_code == 401:
            _LOGGER.debug("DDWrt._get_ddwrt_image: Failed to authenticate, please check your username and password")
            raise(DDWrt.ExceptionAuthenticationError())

        # Unknown HTTP error
        _LOGGER.debug("DDWrt._get_ddwrt_image: Invalid HTTP status code %s", response)
        raise(DDWrt.ExceptionHTTPError(response.status_code))

    def _get_parameter(self, py_parameter, router_parameter):
        if router_parameter in self.data:
            self.results.update({py_parameter: self.data.pop(router_parameter)})
            if self.results[py_parameter] == "":
                self.results.update({py_parameter: None})


    class DDWrtException(Exception):
        pass

    class ExceptionAuthenticationError(Exception):
        pass

    class ExceptionEmptyResponse(Exception):
        pass

    class ExceptionHTTPError(Exception):
        pass

    class ExceptionSSLError(Exception):
        pass

    class ExceptionConnectionError(Exception):
        pass

    class ExceptionInvalidDate(Exception):
        pass

    class ExceptionSelfSigned(Exception):
        pass

    class ExceptionCannotVerify(Exception):
        pass

    class ExceptionHostnameMismatch(Exception):
        pass

    class ExceptionUnknown(Exception):
        pass

    class ExceptionTimeout(Exception):
        pass

