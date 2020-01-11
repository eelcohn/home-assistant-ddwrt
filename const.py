from datetime import timedelta

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_CONNECTIVITY,
)
from homeassistant.const import (
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    TEMP_CELSIUS,
)

ATTRIBUTION = "Data provided by DD-WRT router"

CONF_BINARY_SENSOR = "binary_sensor"
CONF_DEVICE_TRACKER = "device_tracker"
CONF_SENSOR = "sensor"
CONF_TRACK_ARP = "arp"
CONF_TRACK_DHCP = "dhcp"
CONF_TRACK_PPPOE = "pppoe"
CONF_TRACK_PPTP = "pptp"
CONF_TRACK_WDS = "wds"
CONF_TRACK_WIRELESS = "wireless"

DDWRT_MANUFACTURERURL = "https://www.dd-wrt.com"

DEFAULT_SSL = False
DEFAULT_VERIFY_SSL = True
DEFAULT_WIRELESS_ONLY = True

DOMAIN = "ddwrt"
DATA_KEY = DOMAIN
DEFAULT_NAME = "ddwrt"

SCAN_INTERVAL_ABOUT = timedelta(hours=6)
SCAN_INTERVAL_DATA = timedelta(seconds=60)

SOURCE_TYPE_ARP = "arp"
SOURCE_TYPE_DHCP = "dhcp"
SOURCE_TYPE_PPPOE = "pppoe"
SOURCE_TYPE_PPTP = "pptp"
SOURCE_TYPE_WDS = "wds"
SOURCE_TYPE_WIRELESS = "wireless"

_NAME = "name"
_UNIT = "unit"
_ICON = "icon"
_ICON_OFF = "icon_off"
_CLASS = "class"

SENSORS = {
    "clk_freq": {
        _NAME: "Clock frequency",
        _UNIT: "MHz",
        _ICON: "mdi:metronome",
        _CLASS: None,
    },
    "cpu_temp": {
        _NAME: "Temperature",
        _UNIT: TEMP_CELSIUS,
        _ICON: "mdi:thermometer",
        _CLASS: DEVICE_CLASS_TEMPERATURE,
    },
    "ddns_status": {
        _NAME: "DDNS status",
        _UNIT: None,
        _ICON: "mdi:dns",
        _CLASS: None,
    },
    "firmware_build": {
        _NAME: "Firmware build",
        _UNIT: None,
        _ICON: "mdi:wrench",
        _CLASS: None,
    },
    "firmware_date": {
        _NAME: "Firmware date",
        _UNIT: None,
        _ICON: "mdi:wrench",
        _CLASS: None,
    },
    "firmware_version": {
        _NAME: "Firmware version",
        _UNIT: None,
        _ICON: "mdi:wrench",
        _CLASS: None,
    },
    "ip_connections": {
        _NAME: "LAN IP connections",
        _UNIT: None,
        _ICON: "mdi:format-list-bulleted",
        _CLASS: None,
    },
    "lan_dhcp_start": {
        _NAME: "LAN DHCP start address",
        _UNIT: None,
        _ICON: "mdi:ip-network",
        _CLASS: None,
    },
    "lan_dhcp_end": {
        _NAME: "LAN DHCP end address",
        _UNIT: None,
        _ICON: "mdi:ip-network",
        _CLASS: None,
    },
    "lan_dhcp_lease_time": {
        _NAME: "LAN DHCP lease time",
        _UNIT: None,
        _ICON: "mdi:ip-network",
        _CLASS: None,
    },
    "lan_dns": {
        _NAME: "LAN DNS address",
        _UNIT: None,
        _ICON: "mdi:dns",
        _CLASS: None,
    },
    "lan_gateway": {
        _NAME: "LAN gateway",
        _UNIT: None,
        _ICON: "mdi:ip-network",
        _CLASS: None,
    },
    "lan_ipaddr": {
        _NAME: "LAN IP address",
        _UNIT: None,
        _ICON: "mdi:ip",
        _CLASS: None,
    },
    "lan_mac": {
        _NAME: "LAN IP address",
        _UNIT: None,
        _ICON: "mdi:network",
        _CLASS: None,
    },
    "lan_netmask": {
        _NAME: "LAN network mask",
        _UNIT: None,
        _ICON: "mdi:ip",
        _CLASS: None,
    },
    "lan_proto": {
        _NAME: "LAN protocol",
        _UNIT: None,
        _ICON: "mdi:network-router",
        _CLASS: None,
    },
    "load_average1": {
        _NAME: "Load average last minute",
        _UNIT: None,
        _ICON: "mdi:speedometer",
        _CLASS: None,
    },
    "load_average5": {
        _NAME: "Load average last 5 minutes",
        _UNIT: None,
        _ICON: "mdi:speedometer",
        _CLASS: None,
    },
    "load_average15": {
        _NAME: "Load average last 15 minutes",
        _UNIT: None,
        _ICON: "mdi:speedometer",
        _CLASS: None,
    },
    "network_bridges": {
        _NAME: "Network bridges",
        _UNIT: None,
        _ICON: "mdi:bridge",
        _CLASS: None,
    },
    "router_time": {
        _NAME: "Router time",
        _UNIT: None,
        _ICON: "mdi:clock-outline",
        _CLASS: None,
    },
    "uptime": {
        _NAME: "Uptime",
        _UNIT: None,
        _ICON: "mdi:clock-outline",
        _CLASS: None,
    },
    "voltage": {
        _NAME: "Voltage",
        _UNIT: "V",
        _ICON: "mdi:current-dc",
        _CLASS: None,
    },
    "wan_3g_signal": {
        _NAME: "WAN 3G signal strength",
        _UNIT: "DBm",
        _ICON: "mdi:signal-3g",
        _CLASS: DEVICE_CLASS_SIGNAL_STRENGTH,
    },
    "wan_dhcp_remaining": {
        _NAME: "WAN DHCP remaining",
        _UNIT: None,
        _ICON: "mdi:ip-network",
        _CLASS: None,
    },
    "wan_dns0": {
        _NAME: "WAN DNS address 0",
        _UNIT: None,
        _ICON: "mdi:dns",
        _CLASS: None,
    },
    "wan_dns1": {
        _NAME: "WAN DNS address 1",
        _UNIT: None,
        _ICON: "mdi:dns",
        _CLASS: None,
    },
    "wan_dns2": {
        _NAME: "WAN DNS address 2",
        _UNIT: None,
        _ICON: "mdi:dns",
        _CLASS: None,
    },
    "wan_gateway": {
        _NAME: "WAN gateway address",
        _UNIT: None,
        _ICON: "mdi:wan",
        _CLASS: None,
    },
    "wan_ipaddr": {
        _NAME: "WAN IP address",
        _UNIT: None,
        _ICON: "mdi:ip-network",
        _CLASS: None,
    },
    "wan_ip6addr": {
        _NAME: "WAN IP6 address",
        _UNIT: None,
        _ICON: "mdi:ip-network",
        _CLASS: None,
    },
    "wan_netmask": {
        _NAME: "WAN network mask",
        _UNIT: None,
        _ICON: "mdi:ip-network",
        _CLASS: None,
    },
    "wan_pppoe_ac_name": {
        _NAME: "WAN PPPoE access concentrator name",
        _UNIT: None,
        _ICON: "mdi:network-router",
        _CLASS: None,
    },
    "wan_proto": {
        _NAME: "WAN protocol",
        _UNIT: None,
        _ICON: "mdi:network-router",
        _CLASS: None,
    },
    "wan_status": {
        _NAME: "WAN status",
        _UNIT: None,
        _ICON: "mdi:check-network-outline",
        _CLASS: None,
    },
    "wan_traffic_in": {
        _NAME: "WAN traffic inbound",
        _UNIT: "MB",
        _ICON: "mdi:download",
        _CLASS: None,
    },
    "wan_traffic_out": {
        _NAME: "WAN traffic outbound",
        _UNIT: "MB",
        _ICON: "mdi:upload",
        _CLASS: None,
    },
    "wan_uptime": {
        _NAME: "WAN uptime",
        _UNIT: None,
        _ICON: "mdi:clock-outline",
        _CLASS: None,
    },
    "wl_ack": {
        _NAME: "wl_ack",
        _UNIT: None,
        _ICON: "mdi:wifi",
        _CLASS: None,
    },
    "wl_active": {
        _NAME: "wl_active",
        _UNIT: None,
        _ICON: "mdi:wifi",
        _CLASS: None,
    },
    "wl_busy": {
        _NAME: "wl_busy",
        _UNIT: None,
        _ICON: "mdi:wifi",
        _CLASS: None,
    },
    "wl_channel": {
        _NAME: "Wireless channel",
        _UNIT: None,
        _ICON: "mdi:wifi",
        _CLASS: None,
    },
    "wl_count": {
        _NAME: "Wireless clients",
        _UNIT: None,
        _ICON: "mdi:wifi",
        _CLASS: None,
    },
    "wl_mac": {
        _NAME: "Wireless MAC address",
        _UNIT: None,
        _ICON: "mdi:wifi",
        _CLASS: None,
    },
    "wl_quality": {
        _NAME: "wl_quality",
        _UNIT: None,
        _ICON: "mdi:wifi",
        _CLASS: None,
    },
    "wl_rate": {
        _NAME: "Wireless rate",
        _UNIT: "Mbps",
        _ICON: "mdi:wifi",
        _CLASS: None,
    },
    "wl_ssid": {
        _NAME: "Wireless SSID",
        _UNIT: None,
        _ICON: "mdi:wifi",
        _CLASS: None,
    },
    "wl_xmit": {
        _NAME: "Wireless transmit power",
        _UNIT: None,
        _ICON: "mdi:wifi",
        _CLASS: None,
    },
}

BINARY_SENSORS = {
    "wan_connected": {
        _NAME: "WAN connected",
        _UNIT: None,
        _ICON: "mdi:wan",
        _ICON_OFF: "mdi:alert-circle-outline",
        _CLASS: DEVICE_CLASS_CONNECTIVITY,
    },
    "wl_radio": {
        _NAME: "WiFi radio",
        _UNIT: None,
        _ICON: "mdi:wifi",
        _ICON_OFF: "mdi:wifi-off",
        _CLASS: DEVICE_CLASS_CONNECTIVITY,
    },
}

DEVICE_TRACKERS = [
    CONF_TRACK_ARP,
    CONF_TRACK_DHCP,
    CONF_TRACK_PPPOE,
    CONF_TRACK_PPTP,
    CONF_TRACK_WDS,
    CONF_TRACK_WIRELESS,
]

SENSOR_DEFAULTS = [
    "wan_status",
]

BINARY_SENSOR_DEFAULTS = [
    "wan_connected",
]

DEVICE_TRACKER_DEFAULTS = [
    CONF_TRACK_ARP,
    CONF_TRACK_DHCP,
    CONF_TRACK_WIRELESS,
]

