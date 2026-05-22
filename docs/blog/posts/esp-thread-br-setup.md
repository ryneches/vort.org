---
authors:
- ryneches
date: 2026-05-15
description: My notes on building a Thread border router using Espressif's dev board,
  covering topics the official documentation doesn't (e.g., getting it to work with
  Home Assistant running in a container on a Linux host, including things like CasaOS
  or Portainer).
done: {}
tags:
- microcontroller
- esp32
- thread
- matter
- docker
- home-assistant
- projects
title: Building Thread border router with an Espressif development kit
---

# Building Thread border router with an Espressif development kit

These are my notes for setting up a Thread border router based on the [OpenThread](https://openthread.io/guides/border-router) stack using the Espressif Thread Border Router development board. This board is a weird little guy, with an ESP32-S3 and an ESP32-H2 grafted together on one board bridged by UART/SPI. The idea is that the S3 functions as the host and lives on your WiFi network (or Ethernet, if you buy the daughter board), and the H2 runs Zigbee or Thread and talks to the S3. It costs about $10 shipped. You can actually get the price even lower by plugging an [ESP32-H2 directly into your Home Assistant host by USB-C](https://community.home-assistant.io/t/make-your-own-thread-border-router-for-just-5/962780) and running the border router stack on the host. But, I think Espressif's dev board gives you the good parts of a stand-alone border router with a completely self-hosted, open source stack and zero ties to anyone's cloud service. As a smart person once advised me, let network stuff do network stuff, and let server stuff do server stuff; networking infrastructure should fade into the background and should be upgraded or replaced very, very rarely.

I paid 1,326円 to get mine from AliExpress.

- Hardware : Gadget : [https://ja.aliexpress.com/item/1005005872059584.html](https://ja.aliexpress.com/item/1005005872059584.html)
- Official docs : [https://github.com/espressif/esp-thread-br](https://github.com/espressif/esp-thread-br)
- Firmware : https://github.com/espressif/esp-thread-br

It took me a couple of hours to get everything working, which could have gone a lot more smoothly if I'd been a little bit more methodical and a little less excited. These notes detail exactly what I did to get Matter over Thread working in Home Assistant running in a Docker container on my little home server, which runs Debian. I've removed all of my mistakes, swearing and confusion. If you're interested in replicating this setup, these notes should give you a straight shot from opening the box to commissioning your first Matter device in Home Assistant.

______________________________________________________________________

## Prerequisites

You'll need this hardware :

- Espressif ESP Thread Border Router board (ESP32-S3 + ESP32-H2)
- Linux host running Home Assistant container and Matter server container
- A WiFi network
- An Android of iOS device running the Home Assistant companion app
- A Matter device to test with

You'll also need these repos :

- [esp-idf **v5.5.4**](https://github.com/espressif/esp-idf) (not the 6.x series — see below)
- [esp-thread-br](https://github.com/espressif/esp-thread-br) repository

______________________________________________________________________

## Part 1: Building and Flashing the Firmware

### 1.1 Install esp-idf v5.5.4

The esp-thread-br project requires esp-idf v5.5.4. The 6.x series has API changes that break the build. This will require about 3.8 GB after everything is downloaded and built.

```bash
git clone -b v5.5.4 --recursive https://github.com/espressif/esp-idf.git esp-idf-v5.5.4
cd esp-idf-v5.5.4
./install.sh
. ./export.sh
```

Note the leading `.` when sourcing `export.sh`. This script needs to be sourced, not just executed. Add an alias to your shell config for convenience :

```bash
alias get_idf='. ~/path/to/esp-idf-v5.5.4/export.sh'
```

You must source `export.sh` in every new terminal session before building.

### 1.2 Build the RCP firmware

The RCP (Radio Co-Processor) firmware runs on the ESP32-H2. It must be built before the main border router firmware, as it gets bundled in and flashed to the H2 automatically on first boot. Think of this as the "baseband" for this device, if you like.

```bash
cd esp-idf-v5.5.4/examples/openthread/ot_rcp
idf.py set-target esp32h2
idf.py build
```

### 1.3 Clone esp-thread-br

This is the firmware for the ESP32-S3, which is what we'll actually be interacting with. This repo will take up about 1.2 GB once everything is downloaded and built.

```bash
git clone --recursive https://github.com/espressif/esp-thread-br.git
cd esp-thread-br/examples/basic_thread_border_router
```

Use the `basic_thread_border_router` example. The `ot_br` example from esp-idf is a simpler standalone example without the full partition table (OTA, rcp_fw) we need for this board.

### 1.4 Configure

```bash
idf.py set-target esp32s3
idf.py menuconfig
```

Key settings to configure. It's kind of amazing how capable the ESP32 platform is, and so I think it is pretty interesting to explore the features in the menuconfig TUI. It is a bit overwhelming though, so you can also use `/` to search each symbol by name) :

| Symbol | Setting |
|--------|---------|
| `EXAMPLE_WIFI_SSID` | Your WiFi network name |
| `EXAMPLE_WIFI_PASSWORD` | Your WiFi password |
| `OPENTHREAD_BR_AUTO_START` | Enable |
| `OPENTHREAD_BR_START_WEB` | Enable (web UI) |
| `ESPTOOLPY_FLASHSIZE` | 8MB |
| `OPENTHREAD_CLI_WIFI` | **Disable** (conflicts with auto-start) |
| `OPENTHREAD_CSL` | **Disable** (causes linker errors) |
| `OPENTHREAD_MAC_FILTER` | Enable (recommended for security) |
| `OPENTHREAD_DIAG` | Consider disabling for production |

There are various ways to get your WiFi credentials set up, but unfortunately there are some compile-time conflicts. The path of least resistance is just to bake them into your firmware image.

### 1.5 Build and flash

The board has two USB-C ports. One is for the ESP32-S3 (host), and one for the ESP32-H2 (RCP). Flash the main firmware via the **S3 port** :

```bash
idf.py build flash monitor
```

The H2 will be flashed automatically from the bundled RCP firmware on first boot. If you see RCP-related crashes, flash it manually via the H2 port :

```bash
cd esp-idf-v5.5.4/examples/openthread/ot_rcp
idf.py -p <H2_port> flash
```

To exit the monitor: `Ctrl+]`

______________________________________________________________________

## Part 2: Configuring the Thread Network

If you built the web admin interface into your firmware, you can see a lot of cool diagnostic information. However, I found that some key settings do not actually stick if you enter them by the web admin interface, and it will sometimes show the default values for things like the network name even if you've set them correctly. Treat information reported by the console interface as the actual truth.

### 2.1 Verify the border router is up

Now that the board is flashed and booted, we'll have to configure it. Connect to the ESP32-S3 console and check the Thread state :

```
ot state
```

If it shows `disabled`, bring the interface up :

```
ot ifconfig up
ot thread start
```

Wait a few seconds. It should transition to `leader`.

### 2.2 Generate a fresh dataset

The default dataset ships with dummy values that must be replaced :

```
ot dataset init new
ot dataset networkname <your-network-name>
ot dataset commit active
ot thread stop
ot thread start
```

Verify the new dataset :

```
ot dataset active
```

Confirm the network key is not `00112233445566778899aabbccddeeff` and PAN ID is not `0x1234`.

### 2.3 Useful CLI commands for monitoring

```
ot neighbor table           # see connected Thread devices
ot router table             # see Thread routers
ot netdata show             # see advertised prefixes and services
ot srp-server host list     # see registered SRP hosts
ot srp-server service list  # see registered services
```

______________________________________________________________________

## Part 3: Home Assistant Integration

### 3.1 Install required integrations

In Home Assistant, install :

- **Matter** integration
- **Thread** integration
- **OpenThread Border Router** integration

There are a couple of ways to set this up, but I'm running the [The Open Home Foundation Matter Server](https://github.com/matter-js/python-matter-server/pkgs/container/python-matter-server) in a Docker container.

### 3.2 Add the border router

In Home Assistant, go to Settings → Devices & Services → Add Integration → OpenThread Border Router, enter :

```
http://<border-router-ip>:80
```

Or, it's probably more likely that Home Assistant will see that there's a Thread Border Router advertising itself on your network and offer to set it up. Once you've added the border router, go to the Thread integration → Configure and set the ESP border router as the preferred network.

### 3.3 Sync Thread credentials to your phone

Before commissioning any Matter devices, sync the Thread credentials to your phone via the Home Assistant Companion app :

**Android:** Settings → Companion app → Troubleshooting → Sync Thread credentials

This step is important! Without it, Matter commissioning will fail with a misleading "your device requires a Thread border router" error even though the border router is working correctly. You only have to do this once, though.

______________________________________________________________________

## Part 4: IPv6 Routing on the Linux Host

This was actually the most troublesome part of the whole process. The Matter server needs IPv6 connectivity to the Thread network prefix in order to commission devices. But, Matter is running in a Docker container, and it's fairly unlikely that the network plumbing is set up correctly to allow the container to hear IPv6 Router Advertisements on the host's physical network port. By default, Linux ignores Route Info Options in Router Advertisements when IPv6 forwarding is enabled, which prevents the Thread prefix route from being installed.

So, we'll have to re-plumb things for IPv6 a little bit.

### 4.1 Verify the problem

Check if the Thread prefix route is present :

```bash
ip -6 route | grep <thread-prefix>
```

You should able to see your border routers's IPv6 prefix in the ESP32 console messages, or by running `ot netdata show`.

If it's missing, check what RAs are arriving :

```bash
sudo tcpdump -i enp1s0 -vv icmp6 and ip6[40] == 134
```

You should see RAs from the border router advertising the Thread prefix as a route info option.

### 4.2 Fix: accept Route Info Options

Linux requires `accept_ra_rt_info_max_plen` to be set to a non-zero value to process route info options from RAs. Also, `accept_ra=2` is needed when IPv6 forwarding is enabled (which Docker enables).

To apply immediately :

```bash
sudo sysctl net.ipv6.conf.enp1s0.accept_ra=2
sudo sysctl net.ipv6.conf.enp1s0.accept_ra_rt_info_max_plen=64
```

Replace `enp1s0` with your actual Ethernet interface name.

### 4.3 Make permanent

To make these settings stick, create or edit `/etc/sysctl.d/ipv6.conf`:

```
net.ipv6.conf.enp1s0.accept_ra=2
net.ipv6.conf.enp1s0.accept_ra_rt_info_max_plen=64
```

Apply :

```bash
sudo sysctl --system
```

### 4.4 Verify

After the next RA cycle (up to ~2 minutes), the route should appear :

```bash
ip -6 route | grep <thread-prefix>
```

You should also be able to ping Thread devices directly from the Home Assistant host and from inside the Matter container :

```bash
ping -6 -c 3 <thread-device-ipv6>
```

### 4.5 Matter server container networking

The Matter server container must use host networking to access the Thread IPv6 prefix. Bridge networking will not work. Ensure your compose file has :

```yaml
network_mode: host
```

With no `ports:` mappings (this is not needed with host networking).

______________________________________________________________________

## Troubleshooting

Instead of relating all of my screwups in narrative form, please use this table to learn from my mistakes.

| Symptom | Likely cause |
| ------------------------------------------------------ | ------------------------------------------------------------------------- |
| Reboot loop, RCP capabilities error | H2 not flashed or wrong firmware version |
| Build fails with `esp_ot_wifi_*` undefined | Using esp-idf 6.x instead of 5.5.4 |
| Build fails with `OPENTHREAD_CLI_WIFI` conflict | Disable `OPENTHREAD_CLI_WIFI` in menuconfig |
| Linker errors for `otPlatRadioEnableCsl` | Disable `OPENTHREAD_CSL` in menuconfig |
| "Your device requires a Thread border router" | Phone Thread credentials not synced, sync via Companion app, see Part 3.3 |
| Matter commissioning fails, "Network is unreachable" | IPv6 routing not configured on host, see Part 4 |
| Thread prefix route not appearing despite RAs arriving | `accept_ra_rt_info_max_plen=0`, see Part 4.2 |
| Border router on WiFi, host on Ethernet, no route | Normal, solved by sysctl settings, not a bridge/AP issue |
