# home-assistant-ddwrt
Support for DD-WRT routers in Home Assistant.

### Installation
Open a shell and go to your Home Assistant config path, and do:
```
mkdir custom_components
cd custom_components
git clone https://github.com/eelcohn/home-assistant-ddwrt ddwrt
```

### Setup and configuration
You can either setup this component using the UI Integrations page, or using the `configuration.yaml` file:
```
ddwrt:
  - host: !secret ddwrt_hostname
    username: !secret ddwrt_username
    password: !secret ddwrt_password
    ssl: true
    verify_ssl: false
    resources:
      - clk_freq
      - cpu_temp
      - ddns_status
      - dhcp_clients
      - sw_build
      - sw_date
      - sw_version
      - ip_connections
      - lan_dhcp_start
      - lan_dhcp_end
      - lan_dhcp_lease_time
      - lan_dns
      - lan_gateway
      - lan_ipaddr
      - lan_mac
      - lan_netmask
      - lan_proto
      - load_average1
      - load_average5
      - load_average15
      - network_bridges
      - nvram_used
      - nvram_total
      - router_manufacturer
      - router_model
      - router_time
      - uptime
      - voltage
      - wan_3g_signal
      - wan_dhcp_remaining
      - wan_dns0
      - wan_dns1
      - wan_dns2
      - wan_dns3
      - wan_dns4
      - wan_dns5
      - wan_gateway
      - wan_ipaddr
      - wan_ip6addr
      - wan_netmask
      - wan_pppoe_ac_name
      - wan_proto
      - wan_status
      - wan_traffic_in
      - wan_traffic_out
      - wan_uptime
      - wl_ack_timing
      - wl_ack_distance
      - wl_active
      - wl_busy
      - wl_channel
      - wl_count
      - wl_mac
      - wl_quality
      - wl_rate
      - wl_rx_packet_error
      - wl_tx_packet_error
      - wl_rx_packet_ok
      - wl_tx_packet_ok
      - wl_ssid
      - wl_xmit
      - wan_connected
      - wl_radio
      - traffic
```

### Support
Support for this module can be requested by opening an [issue](https://github.com/eelcohn/home-assistant-ddwrt/issues). More info can be found in [this thread](https://community.home-assistant.io/t/custom-component-for-dd-wrt-routers/162423)
