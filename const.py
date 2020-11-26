from datetime import timedelta

from homeassistant.components.binary_sensor import (
    DEVICE_CLASS_CONNECTIVITY,
)
from homeassistant.const import (
    ATTR_DEVICE_CLASS,
    ATTR_ICON,
    ATTR_NAME,
    ATTR_UNIT_OF_MEASUREMENT,
    DATA_KILOBYTES,
    DATA_MEGABYTES,
    DATA_RATE_MEGABITS_PER_SECOND,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    LENGTH_METERS,
    TEMP_CELSIUS,
    TIME_MICROSECONDS,
    TIME_MINUTES,
    VOLT,
)

_VERSION = "1.1.0"

ATTRIBUTION = "Data provided by DD-WRT router"

CONF_BINARY_SENSOR = "binary_sensor"
CONF_CAMERA = "camera"
CONF_DEVICE_TRACKER = "device_tracker"
CONF_SENSOR = "sensor"
CONF_TRACK_ARP = "arp_clients"
CONF_TRACK_DHCP = "dhcp_clients"
CONF_TRACK_PPPOE = "pppoe_clients"
CONF_TRACK_PPTP = "pptp_clients"
CONF_TRACK_WDS = "wds_clients"
CONF_TRACK_WIRELESS = "wireless_clients"

COMPONENTS = (
    CONF_BINARY_SENSOR,
    CONF_CAMERA,
    CONF_DEVICE_TRACKER,
    CONF_SENSOR
)

DDWRT_UPNP_MANUFACTURER_URL = "https://www.dd-wrt.com"

DEFAULT_DEVICE_NAME = "DD-WRT router"

DEFAULT_SSL = True
DEFAULT_VERIFY_SSL = False
DEFAULT_WIRELESS_ONLY = True

DOMAIN = "ddwrt"
DATA_LISTENER = "listener"

MIN_SCAN_INTERVAL   = timedelta(seconds=30)
SCAN_INTERVAL_ABOUT = timedelta(hours=6)
SCAN_INTERVAL_DATA  = timedelta(seconds=60)

TOPIC_DATA_UPDATE = f"{DOMAIN}_data_update"

# Define all available services
SERVICE_RUN_COMMAND          = "run_command"
SERVICE_REBOOT               = "reboot"
SERVICE_UPNP_DELETE          = "upnp_delete"
SERVICE_WAKE_ON_LAN          = "wake_on_lan"
SERVICE_WAN_DHCP_RELEASE     = "wan_dhcp_release"
SERVICE_WAN_DHCP_RENEW       = "wan_dhcp_renew"
SERVICE_WAN_PPPOE_CONNECT    = "wan_pppoe_connect"
SERVICE_WAN_PPPOE_DISCONNECT = "wan_pppoe_disconnect"

SERVICES = {
    SERVICE_REBOOT,
    SERVICE_RUN_COMMAND,
    SERVICE_UPNP_DELETE,
    SERVICE_WAKE_ON_LAN,
    SERVICE_WAN_DHCP_RELEASE,
    SERVICE_WAN_DHCP_RENEW,
    SERVICE_WAN_PPPOE_CONNECT,
    SERVICE_WAN_PPPOE_DISCONNECT,
}

# Define attributes
ATTR_ICON_OFF = "icon_off"
ATTR_WIRED    = "wired"

# Define units
DECIBEL_MILLIWATTS = "dBm"
FREQUENCY_MEGAHERTZ = "MHz"

# Define all available binary_sensors, cameras, device_trackers and sensors
BINARY_SENSORS = {
    "wan_connected": {
        ATTR_NAME: "WAN connected",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wan",
        ATTR_ICON_OFF: "mdi:alert-circle-outline",
        ATTR_DEVICE_CLASS: DEVICE_CLASS_CONNECTIVITY,
    },
    "wl_radio": {
        ATTR_NAME: "WiFi radio",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wifi",
        ATTR_ICON_OFF: "mdi:wifi-off",
        ATTR_DEVICE_CLASS: DEVICE_CLASS_CONNECTIVITY,
    },
}

CAMERAS = {
    "traffic": {
        ATTR_NAME: "Monthly traffic",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:swap-vertical-bold",
        ATTR_DEVICE_CLASS: None,
    },
}

DEVICE_TRACKERS = {
    CONF_TRACK_ARP: {
        ATTR_NAME: "ARP clients",
        ATTR_ICON: "mdi:network",
        ATTR_WIRED: True,
    },
    CONF_TRACK_DHCP: {
        ATTR_NAME: "DHCP clients",
        ATTR_ICON: "mdi:network",
        ATTR_WIRED: True,
    },
    CONF_TRACK_PPPOE: {
        ATTR_NAME: "PPPoE clients",
        ATTR_ICON: "mdi:network",
        ATTR_WIRED: True,
    },
    CONF_TRACK_PPTP: {
        ATTR_NAME: "PPTP clients",
        ATTR_ICON: "mdi:network",
        ATTR_WIRED: True,
    },
    CONF_TRACK_WDS: {
        ATTR_NAME: "WDS clients",
        ATTR_ICON: "mdi:access-point-network",
        ATTR_WIRED: False,
    },
    CONF_TRACK_WIRELESS: {
        ATTR_NAME: "WiFi clients",
        ATTR_ICON: "mdi:wireless",
        ATTR_WIRED: False,
    },
}

SENSORS = {
    "clk_freq": {
        ATTR_NAME: "Clock frequency",
        ATTR_UNIT_OF_MEASUREMENT: FREQUENCY_MEGAHERTZ,
        ATTR_ICON: "mdi:metronome",
        ATTR_DEVICE_CLASS: None,
    },
    "cpu_temp": {
        ATTR_NAME: "Temperature",
        ATTR_UNIT_OF_MEASUREMENT: TEMP_CELSIUS,
        ATTR_ICON: "mdi:thermometer",
        ATTR_DEVICE_CLASS: DEVICE_CLASS_TEMPERATURE,
    },
    "ddns_status": {
        ATTR_NAME: "DDNS status",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:dns",
        ATTR_DEVICE_CLASS: None,
    },
    "sw_build": {
        ATTR_NAME: "Firmware build",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wrench",
        ATTR_DEVICE_CLASS: None,
    },
    "sw_date": {
        ATTR_NAME: "Firmware date",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wrench",
        ATTR_DEVICE_CLASS: None,
    },
    "sw_version": {
        ATTR_NAME: "Firmware version",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wrench",
        ATTR_DEVICE_CLASS: None,
    },
    "ip_connections": {
        ATTR_NAME: "LAN IP connections",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:format-list-bulleted",
        ATTR_DEVICE_CLASS: None,
    },
    "lan_dhcp_start": {
        ATTR_NAME: "LAN DHCP start address",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:ip-network",
        ATTR_DEVICE_CLASS: None,
    },
    "lan_dhcp_end": {
        ATTR_NAME: "LAN DHCP end address",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:ip-network",
        ATTR_DEVICE_CLASS: None,
    },
    "lan_dhcp_lease_time": {
        ATTR_NAME: "LAN DHCP lease time",
        ATTR_UNIT_OF_MEASUREMENT: TIME_MINUTES,
        ATTR_ICON: "mdi:ip-network",
        ATTR_DEVICE_CLASS: None,
    },
    "lan_dns": {
        ATTR_NAME: "LAN DNS address",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:dns",
        ATTR_DEVICE_CLASS: None,
    },
    "lan_gateway": {
        ATTR_NAME: "LAN gateway",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:ip-network",
        ATTR_DEVICE_CLASS: None,
    },
    "lan_ipaddr": {
        ATTR_NAME: "LAN IP address",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:ip",
        ATTR_DEVICE_CLASS: None,
    },
    "lan_mac": {
        ATTR_NAME: "LAN MAC address",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:network",
        ATTR_DEVICE_CLASS: None,
    },
    "lan_netmask": {
        ATTR_NAME: "LAN network mask",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:ip",
        ATTR_DEVICE_CLASS: None,
    },
    "lan_proto": {
        ATTR_NAME: "LAN protocol",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:router-network",
        ATTR_DEVICE_CLASS: None,
    },
    "load_average1": {
        ATTR_NAME: "Load average last minute",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:speedometer",
        ATTR_DEVICE_CLASS: None,
    },
    "load_average5": {
        ATTR_NAME: "Load average last 5 minutes",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:speedometer",
        ATTR_DEVICE_CLASS: None,
    },
    "load_average15": {
        ATTR_NAME: "Load average last 15 minutes",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:speedometer",
        ATTR_DEVICE_CLASS: None,
    },
    "network_bridges": {
        ATTR_NAME: "Network bridges",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:bridge",
        ATTR_DEVICE_CLASS: None,
    },
    "nvram_used": {
        ATTR_NAME: "NVRAM Used",
        ATTR_UNIT_OF_MEASUREMENT: DATA_KILOBYTES,
        ATTR_ICON: "mdi:memory",
        ATTR_DEVICE_CLASS: None,
    },
    "nvram_total": {
        ATTR_NAME: "NVRAM Total",
        ATTR_UNIT_OF_MEASUREMENT: DATA_KILOBYTES,
        ATTR_ICON: "mdi:memory",
        ATTR_DEVICE_CLASS: None,
    },
    "router_manufacturer": {
        ATTR_NAME: "Router manufacturer",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:router",
        ATTR_DEVICE_CLASS: None,
    },
    "router_model": {
        ATTR_NAME: "Router model",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:router",
        ATTR_DEVICE_CLASS: None,
    },
    "router_time": {
        ATTR_NAME: "Router time",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:clock-outline",
        ATTR_DEVICE_CLASS: None,
    },
    "uptime": {
        ATTR_NAME: "Uptime",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:clock-outline",
        ATTR_DEVICE_CLASS: None,
    },
    "voltage": {
        ATTR_NAME: "Voltage",
        ATTR_UNIT_OF_MEASUREMENT: VOLT,
        ATTR_ICON: "mdi:current-dc",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_3g_signal": {
        ATTR_NAME: "WAN 3G signal strength",
        ATTR_UNIT_OF_MEASUREMENT: DECIBEL_MILLIWATTS,
        ATTR_ICON: "mdi:signal-3g",
        ATTR_DEVICE_CLASS: DEVICE_CLASS_SIGNAL_STRENGTH,
    },
    "wan_dhcp_remaining": {
        ATTR_NAME: "WAN DHCP remaining",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:ip-network",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_dns0": {
        ATTR_NAME: "WAN DNS address 0",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:dns",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_dns1": {
        ATTR_NAME: "WAN DNS address 1",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:dns",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_dns2": {
        ATTR_NAME: "WAN DNS address 2",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:dns",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_dns3": {
        ATTR_NAME: "WAN DNS address 3",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:dns",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_dns4": {
        ATTR_NAME: "WAN DNS address 4",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:dns",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_dns5": {
        ATTR_NAME: "WAN DNS address 5",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:dns",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_gateway": {
        ATTR_NAME: "WAN gateway address",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wan",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_ipaddr": {
        ATTR_NAME: "WAN IP address",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:ip-network",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_ip6addr": {
        ATTR_NAME: "WAN IP6 address",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:ip-network",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_netmask": {
        ATTR_NAME: "WAN network mask",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:ip-network",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_pppoe_ac_name": {
        ATTR_NAME: "WAN PPPoE access concentrator name",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:router-network",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_proto": {
        ATTR_NAME: "WAN protocol",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:router-network",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_status": {
        ATTR_NAME: "WAN status",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:check-network-outline",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_traffic_in": {
        ATTR_NAME: "WAN traffic inbound",
        ATTR_UNIT_OF_MEASUREMENT: DATA_MEGABYTES,
        ATTR_ICON: "mdi:download",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_traffic_out": {
        ATTR_NAME: "WAN traffic outbound",
        ATTR_UNIT_OF_MEASUREMENT: DATA_MEGABYTES,
        ATTR_ICON: "mdi:upload",
        ATTR_DEVICE_CLASS: None,
    },
    "wan_uptime": {
        ATTR_NAME: "WAN uptime",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:clock-outline",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_ack_timing": {
        ATTR_NAME: "Wireless ACK timing",
        ATTR_UNIT_OF_MEASUREMENT: TIME_MICROSECONDS,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_ack_distance": {
        ATTR_NAME: "Wireless ACK distance",
        ATTR_UNIT_OF_MEASUREMENT: LENGTH_METERS,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_active": {
        ATTR_NAME: "Wireless network active",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_busy": {
        ATTR_NAME: "wl_busy",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_channel": {
        ATTR_NAME: "Wireless channel",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_count": {
        ATTR_NAME: "Wireless clients",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_mac": {
        ATTR_NAME: "Wireless MAC address",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_quality": {
        ATTR_NAME: "wl_quality",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_rate": {
        ATTR_NAME: "Wireless rate",
        ATTR_UNIT_OF_MEASUREMENT: DATA_RATE_MEGABITS_PER_SECOND,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_rx_packet_error": {
        ATTR_NAME: "Wireless packets received errors",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_rx_packet_ok": {
        ATTR_NAME: "Wireless packets received OK",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_ssid": {
        ATTR_NAME: "Wireless SSID",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_tx_packet_error": {
        ATTR_NAME: "Wireless packets transmitted errors",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_tx_packet_ok": {
        ATTR_NAME: "Wireless packets transmitted OK",
        ATTR_UNIT_OF_MEASUREMENT: None,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
    "wl_xmit": {
        ATTR_NAME: "Wireless transmit power",
        ATTR_UNIT_OF_MEASUREMENT: DECIBEL_MILLIWATTS,
        ATTR_ICON: "mdi:wifi",
        ATTR_DEVICE_CLASS: None,
    },
}

RESOURCES = []
RESOURCES.extend(key for key in BINARY_SENSORS)
RESOURCES.extend(key for key in CAMERAS)
RESOURCES.extend(key for key in DEVICE_TRACKERS)
RESOURCES.extend(key for key in SENSORS)

# Defaults for when no binary_sensors, cameras, device_trackers or sensors were given
BINARY_SENSOR_DEFAULTS = [
    "wan_connected",
]

CAMERA_DEFAULTS = [
    "traffic",
]

DEVICE_TRACKER_DEFAULTS = [
    CONF_TRACK_ARP,
    CONF_TRACK_DHCP,
    CONF_TRACK_WIRELESS,
]

SENSOR_DEFAULTS = [
    "wan_status",
]

RESOURCES_DEFAULTS = [
    "wan_connected",
    "traffic",
    CONF_TRACK_ARP,
    CONF_TRACK_DHCP,
    CONF_TRACK_WIRELESS,
    "wan_status",
]

