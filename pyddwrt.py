"""Class for querying DD-WRT routers"""

import logging
import re
import ssl
import urllib3
from OpenSSL import crypto
from datetime import datetime
from requests import Session
from requests.exceptions import Timeout, ConnectionError, SSLError

_LOGGER = logging.getLogger(__name__)
_VERSION = "0.9.0"
_X_REQUESTED_WITH = __name__ + "-" + _VERSION
HTTP_X_REQUESTED_WITH = "X-Requested-With"

DEFAULT_TIMEOUT = 4

ENDPOINT_ABOUT = "About.htm"
ENDPOINT_AOSS = "AOSS.live.asp"
ENDPOINT_CONNTRACK = "Status_Conntrack.asp"
ENDPOINT_DDNS = "DDNS.live.asp"
ENDPOINT_FREERADIUS = "FreeRadius.live.asp"
ENDPOINT_INTERNET = "Status_Internet.live.asp"
ENDPOINT_NETWORKING = "Networking.live.asp"
ENDPOINT_STATUSINFO = "Statusinfo.live.asp"
ENDPOINT_LAN = "Status_Lan.live.asp"
ENDPOINT_ROUTER = "Status_Router.live.asp"
ENDPOINT_SPUTNIK = "Status_SputnikAPD.live.asp"
ENDPOINT_WIRELESS = "Status_Wireless.live.asp"
ENDPOINT_UPNP = "UPnP.live.asp"
ENDPOINT_USB = "USB.live.asp"

_DDWRT_DATA_REGEX = re.compile(r"\{(\w+)::([^\}]*)\}")


class DDWrt:
    """This class queries a wireless router running DD-WRT firmware."""

    def __init__(self, host, username, password, protocol, verify_ssl):
        """Initialize the DD-WRT class."""

        self._host = host
        self._username = username
        self._password = password
        self._protocol = protocol
        self._verify_ssl = verify_ssl

        self.results = {}
        self.clients_arp = {}
        self.clients_dhcp = {}
        self.clients_pppoe = {}
        self.clients_pptp = {}
        self.clients_wds = {}
        self.clients_wireless = {}

        self._session = Session()


    def update_about_data(self):
        """Gets firmware version info from the DD-WRT router"""

        _LOGGER.debug("Updating about data...")

        url = f"{self._protocol}://{self._host}/{ENDPOINT_ABOUT}"

        try:
            data = self.get_ddwrt_data(url, False)
        except Exception as e:
#            pass
            raise(DDWrt.DDWrtException("Unable to update about data: %s", e))
            return None

        _LOGGER.debug("Data returned from About page: %s", data)

        if not data:
            return False

        # Get firmware info
        firmware = data.partition("DD-WRT v")[2].split("<br />")[0]
        firmware_version = firmware.split("-r")[0]
        firmware_build = firmware.split("-r")[1].split(" ")[0]
        firmware_date = firmware.split("(")[1].split(")")[0]

        self.results.update({"firmware_version": firmware_version})
        self.results.update({"firmware_build": firmware_build})
        self.results.update({"firmware_date": firmware_date})

        return True


    def update_wan_data(self):
        """Gets WAN info from the DD-WRT router"""

        _LOGGER.debug("Updating WAN data...")

        # Get data from internet endpoint
        url = f"{self._protocol}://{self._host}/{ENDPOINT_INTERNET}"
        try:
            data = self.get_ddwrt_data(url, True)
        except Exception as e:
            raise(DDWrt.DDWrtException("Unable to update WAN data: %s", e))
            return None

        _LOGGER.debug("Data returned from Internet page: %s", data)

        if not data:
            return False

        # Get WAN info
        wan_dhcp_remaining = data.get("dhcp_remaining", None)
        wan_status = data.get("wan_status", None).strip().split("&nbsp;")[0]
        wan_3g_signal = data.get("wan_3g_signal", None)
        wan_connected = True if wan_status  == "Connected" else False
        wan_dns0 = data.get("wan_dns0", None)
        wan_dns1 = data.get("wan_dns1", None)
        wan_dns2 = data.get("wan_dns2", None)
        wan_gateway = data.get("wan_gateway", None)
        wan_ipaddr = data.get("wan_ipaddr", None)
        if wan_ipaddr:
            wan_ip6addr = data.get("ipinfo", None).split("IPv6:")[1].strip()
        wan_netmask = data.get("wan_netmask", None)
        wan_pppoe_ac_name = data.get("pppoe_ac_name", None)
        wan_proto = data.get("wan_shortproto", None)
        wan_traffic_in = data.get("ttraff_in", None)
        wan_traffic_out = data.get("ttraff_out", None)
        wan_uptime = data.get("wan_uptime", None).strip().split(",  ")[0]

        self.results.update({"wan_3g_signal": wan_3g_signal})
        self.results.update({"wan_connected": wan_connected})
        self.results.update({"wan_dhcp_remaining": wan_dhcp_remaining})
        self.results.update({"wan_dns0": wan_dns0})
        self.results.update({"wan_dns1": wan_dns1})
        self.results.update({"wan_dns2": wan_dns2})
        self.results.update({"wan_gateway": wan_gateway})
        self.results.update({"wan_ipaddr": wan_ipaddr})
        self.results.update({"wan_ip6addr": wan_ip6addr})
        self.results.update({"wan_netmask": wan_netmask})
        self.results.update({"wan_pppoe_ac_name": wan_pppoe_ac_name})
        self.results.update({"wan_proto": wan_proto})
        self.results.update({"wan_status": wan_status})
        self.results.update({"wan_traffic_in": wan_traffic_in})
        self.results.update({"wan_traffic_out": wan_traffic_out})
        self.results.update({"wan_uptime": wan_uptime})

        return True


    def update_router_data(self):
        """Gets router info from the DD-WRT router"""

        _LOGGER.debug("Updating router data...")

        # Get data from router endpoint
        url = f"{self._protocol}://{self._host}/{ENDPOINT_ROUTER}"
        try:
            data = self.get_ddwrt_data(url, True)
        except Exception as e:
            raise(DDWrt.DDWrtException("Unable to update router data: %s", e))
            return None

        if not data:
            return False

        # Get router info
        clk_freq = data.get("clkfreq", None)
        if data.get("cpu_temp", None) != "Not available":
            cpu_temp = {}
            for item in data.get("cpu_temp", None).split("/"):
                cpu_temp.update({item.strip().split(" ")[0]: float(item.strip().split(" ")[1])})
        else:
            cpu_temp = None
        ip_connections = data.get("ip_conntrack", None)
        router_time = data.get("router_time", None)
        uptime = data.get("uptime", None).split(",  ")[0].split(" up ")[1].strip()
        load_average1 = data.get("uptime", None).split("load average:")[1].split(",")[0].strip()
        load_average5 = data.get("uptime", None).split("load average:")[1].split(",")[1].strip()
        load_average15 = data.get("uptime", None).split("load average:")[1].split(",")[2].strip()
        voltage = data.get("voltage", None).strip().split(" ")[0]
        if voltage:
            _LOGGER.warning("voltage = %s", voltage)
#            voltage = float(voltage)

        # Add data to the _results array
        self.results.update({"clk_freq":        clk_freq})
        self.results.update({"cpu_temp":        cpu_temp})
        self.results.update({"ip_connections":  ip_connections})
        self.results.update({"load_average1":   load_average1})
        self.results.update({"load_average5":   load_average5})
        self.results.update({"load_average15":  load_average15})
        self.results.update({"router_time":     router_time})
        self.results.update({"uptime":          uptime})
        self.results.update({"voltage":         voltage})

        return True


    def update_network_data(self):
        """Gets Networking info from the DD-WRT router"""

        _LOGGER.debug("Updating Networking data...")

        # Get data from networking endpoint
        url = f"{self._protocol}://{self._host}/{ENDPOINT_NETWORKING}"
        try:
            data = self.get_ddwrt_data(url, True)
        except Exception as e:
            raise(DDWrt.DDWrtException("Unable to update networking data: %s", e))
            return None

        if not data:
            return False

        # Get Networking info
        network_bridges = [item.strip("'").strip() for item in data.get("bridges_table", None).split(",")]

        self.results.update({"network_bridges": network_bridges})

        return True


    def update_wireless_data(self):
        """Gets wireless info from the DD-WRT router"""

        _LOGGER.debug("Updating wireless data...")

        url = f"{self._protocol}://{self._host}/{ENDPOINT_WIRELESS}"
        try:
            data = self.get_ddwrt_data(url, True)
        except Exception as e:
            raise(DDWrt.DDWrtException("Unable to update wireless data: %s", e))
            return None

        if not data:
            return False

        # Get wireless info
        wl_ack = data.get("wl_ack", None)
        wl_active = data.get("wl_active", None)
        wl_busy = data.get("wl_busy", None)
        wl_channel = data.get("wl_channel", None)
        wl_count = data.get("assoc_count", None)
        wl_mac = data.get("wl_mac", None)
        wl_quality = data.get("wl_quality", None)
        wl_radio = True if data.get("wl_radio", None).strip().split(" ")[2]  == "On" else False
        wl_rate = data.get("wl_rate", None).split(" ")[0]
        wl_ssid = data.get("wl_ssid", None)
        wl_xmit = data.get("wl_xmit", None)

        self.results.update({"wl_ack": wl_ack})
        self.results.update({"wl_active": wl_active})
        self.results.update({"wl_busy": wl_busy})
        self.results.update({"wl_channel": wl_channel})
        self.results.update({"wl_count": wl_count})
        self.results.update({"wl_mac": wl_mac})
        self.results.update({"wl_quality": wl_quality})
        self.results.update({"wl_radio": wl_radio})
        self.results.update({"wl_rate": wl_rate})
        self.results.update({"wl_ssid": wl_ssid})
        self.results.update({"wl_xmit": wl_xmit})

        # Get wireless clients
        active_clients = data.get("active_wireless", None)

        if active_clients:
            elements = [item.strip().strip("'") for item in active_clients.strip().split(",")]

            # Wireless elements: MAC Address | Radioname | Interface | Uptime | Tx rate | Rx rate | Info | Signal | Noise | SNR | Signal Quality
            self.clients_wireless = {}
            for i in range(0, len(elements), 11):
                self.clients_wireless.update( {
                    elements[i]: {
                        "name": elements[i + 1],
                        "type": "wireless",
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
            _LOGGER.debug("Wireless clients: %s", self.clients_wireless)

        # Get WDS clients
        active_clients = data.get("active_wds", None)

        if active_clients:
            elements = [item.strip().strip("'") for item in active_clients.strip().split(",")]

            # WDS elements: MAC Address | Interface | Description | Signal | Noise | SNR | Signal Quality
            self.clients_wds = {}
            for i in range(0, len(elements), 7):
                _LOGGER.info("interface=%s", elements[i+4])
                self.clients_wds.update( {
                    elements[i]: {
                        "name": elements[i + 2],
                        "type": "wds",
                        "interface": elements[i + 1],
                        "description": elements[i + 2],
                        "signal": elements[i + 3],
                        "noise": elements[i + 4],
                        "snr": elements[i + 5],
                        "signal_quality": elements[i + 6],
                    }
                }
            )
            _LOGGER.debug("WDS clients: %s", self.clients_wds)

        return True

    def update_lan_data(self):
        """Gets LAN info from the DD-WRT router"""

        _LOGGER.debug("Updating LAN data...")

        url = f"{self._protocol}://{self._host}/{ENDPOINT_LAN}"
        try:
            data = self.get_ddwrt_data(url, True)
        except Exception as e:
            raise(DDWrt.DDWrtException("Unable to update LAN data: %s", e))
            return None

        if not data:
            return False

        # Get LAN info
        lan_dhcp_prefix = data.get("lan_ip_prefix", None)
        lan_dhcp_start = "{}{}".format(lan_dhcp_prefix, data.get("dhcp_start", None))
        lan_dhcp_end = "{}{}".format(lan_dhcp_prefix, int(data.get("dhcp_start", None))+int(data.get("dhcp_num", None))-1)
        lan_dhcp_lease_time = data.get("dhcp_lease_time", None)
        lan_dns = data.get("lan_dns", None)
        lan_gateway = data.get("lan_gateway", None)
        lan_ipaddr = data.get("lan_ip", None)
        lan_mac = data.get("lan_mac", None)
        lan_netmask = data.get("lan_netmask", None)
        lan_proto = data.get("lan_proto", None)

        self.results.update({"lan_dhcp_start": lan_dhcp_start})
        self.results.update({"lan_dhcp_end": lan_dhcp_end})
        self.results.update({"lan_dhcp_lease_time": lan_dhcp_lease_time})
        self.results.update({"lan_dns": lan_dns})
        self.results.update({"lan_gateway": lan_gateway})
        self.results.update({"lan_ipaddr": lan_ipaddr})
        self.results.update({"lan_mac": lan_mac})
        self.results.update({"lan_netmask": lan_netmask})
        self.results.update({"lan_proto": lan_proto})

        # Get clients from ARP table
        active_clients = data.get("arp_table", None)
        if active_clients:
            elements = [item.strip().strip("'") for item in active_clients.strip().split(",")]

            # ARP elements: Hostname | IP Address | MAC Address | Interface | Connections
            self.clients_arp = {}
            for i in range(0, len(elements), 5):
                self.clients_arp.update( {
                    elements[i + 2]: {
                        "name": elements[i],
                        "type": "arp",
                        "ip": elements[i + 1],
                        "hostname": elements[i],
                        "connections": elements[i + 3],
                        "interface": elements[i + 4]
                    }
                }
            )
            _LOGGER.debug("ARP clients: %s", self.clients_arp)

        # Get clients from DHCP leases
        active_clients = data.get("dhcp_leases", None)
        if active_clients:
            elements = [item.strip().strip("'") for item in active_clients.strip().split(",")]

            # DHCP elements: Hostname | IP Address | MAC Address | Lease Expiration
            self.clients_dhcp = {}
            for i in range(0, len(elements), 5):
                self.clients_dhcp.update( {
                    elements[i + 2]: {
                        "name": elements[i],
                        "type": "dhcp",
                        "ip": elements[i + 1],
                        "hostname": elements[i],
                        "lease_expiration": elements[i + 3]
                    }
                }
            )
            _LOGGER.debug("DHCP clients: %s", self.clients_dhcp)

        # Get clients from PPPoE leases
        active_clients = data.get("pppoe_leases", None)
        if active_clients:
            elements = [item.strip().strip("'") for item in active_clients.strip().split(",")]

            # PPPoE elements: Interface | Username | Local IP
            self.clients_pppoe = {}
            for i in range(0, len(elements), 3):
                self.clients_pppoe.update( {
                    elements[i + 2]: {
                        "name": elements[i + 1],
                        "type": "pppoe",
                        "interface": elements[i],
                        "username": elements[i + 1],
                        "local_ip": elements[i + 2]
                    }
                }
            )
            _LOGGER.debug("PPPoE clients: %s", self.clients_pppoe)

        # Get clients from PPTP leases
        active_clients = data.get("pptp_leases", None)
        if active_clients:
            elements = [item.strip().strip("'") for item in active_clients.strip().split(",")]

            # PPTP elements: Interface | Username | Local IP | Remote IP
            self.clients_pptp = {}
            for i in range(0, len(elements), 4):
                self.clients_pptp.update( {
                    elements[i + 2]: {
                        "name": elements[i + 1],
                        "type": "pptp",
                        "interface": elements[i],
                        "username": elements[i + 1],
                        "local_ip": elements[i + 2],
                        "remote_ip": elements[i + 3]
                    }
                }
             )
            _LOGGER.debug("PPTP clients: %s", self.clients_pptp)

        return True

    def get_ddwrt_data(self, url, convert):
        """Retrieve data from DD-WRT router and return parsed result."""

        _LOGGER.debug("Connecting to %s", url)

        # Disable warning on not verifying the certificate
        if not self._verify_ssl:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        try:
            response = self._session.get(
                url,
                auth = (self._username, self._password),
                headers = {HTTP_X_REQUESTED_WITH: _X_REQUESTED_WITH},
                timeout = DEFAULT_TIMEOUT,
                verify = self._verify_ssl,
            )
        except urllib3.exceptions.InsecureRequestWarning as e:
            _LOGGER.debug("Cannot verify certificate")
            raise(DDWrt.ExceptionCannotVerify(e))

        except SSLError as e:
            errmsg = str(e)

            # Check for hostname mismatch error
            if errmsg.startswith("hostname"):
                _LOGGER.debug("SSLError hostname mismatch")
                raise(DDWrt.ExceptionHostnameMismatch(e))

            # Get certificate from the router
            try:
                raw_cert = ssl.get_server_certificate((self._host, 443))
            except Exception as e:
                _LOGGER.debug("SSLError unknown error")
                raise(DDWrt.ExceptionSSLError(e))

            # Check for valid date in certificate
            x509 = crypto.load_certificate(crypto.FILETYPE_PEM, raw_cert)
            now = datetime.now()
            not_after = datetime.strptime(x509.get_notAfter().decode('utf-8'), "%Y%m%d%H%M%SZ")
            not_before = datetime.strptime(x509.get_notBefore().decode('utf-8'), "%Y%m%d%H%M%SZ")
            if now > not_after or now < not_before:
                _LOGGER.debug("SSLError invalid date")
                raise(DDWrt.ExceptionInvalidDate(e))

            # Return self-signed error
            _LOGGER.debug("SSLError self signed")
            raise(DDWrt.ExceptionSelfSigned(e))

        except ConnectionError as e:
            _LOGGER.debug("ConnectionError")
            raise(DDWrt.ExceptionConnectionError(e))

        except Timeout as e:
            _LOGGER.debug("Timeout")
            raise(DDWrt.ExceptionTimeout(e))

        except Exception as e:
            _LOGGER.debug("Unable to connect to the router Connection error: %s", e)
            raise(DDWrt.ExceptionUnknown(e))

        # Valid response
        if response.status_code == 200:
            if response.text:
                if convert:
                    result = dict(_DDWRT_DATA_REGEX.findall(response.text))
                else:
                    result = response.text
                _LOGGER.debug("received data: %s", result)
                return result
            else:
                _LOGGER.debug("DD-WRT: Received empty response querying %s", url)
                raise(DDWrt.ExceptionEmptyResponse())

        # Authentication error
        if response.status_code == 401:
            _LOGGER.debug("Failed to authenticate, please check your username and password")
            raise(DDWrt.ExceptionAuthenticationError())

        # Unknown HTTP error
        _LOGGER.debug("DD-WRT: Invalid HTTP status code %s", response)
        raise(DDWrt.ExceptionHTTPError(response.status_code))

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

