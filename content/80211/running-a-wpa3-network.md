Title: Running a WPA3 access point with hostapd 2.7 and SAE/Dragonfly
Date: 2019-2-22 18:15
Modified: 2020-12-31 13:15
Category: WPA3
Tags: WPA3, 802.11, hostapd, wpa_supplicant
Slug: running-a-WPA3-access-point-with-hostapd-SAE-Dragonfly
Author: Nikolai Tschacher
Summary: Tutorial that shows how to run an WPA3 access point with hostapd 2.7 and SAE Dragonfly Handshake.

In my master thesis at HU Berlin I investigate the simultaneous authentication of equals (SAE) 
protocol that is going to be used as part of the WPA3 certification. 

In the broadest sense I will investigate the security of the new SAE authentication mechanism and the interaction
with the 4-way-handshake.

This handshake (also referred to as Dragonfly) brings two major advantages compared to the well known WPA/WPA2 authentication:

1. Dragonfly/SAE is resistant against offline dictionary attacks. Guesses on the password
can only happen while interacting with the protocol in a life handshake negotiation session.

2. Dragonfly/SAE provides perfect forward secrecy. This means that an attacker cannot
decrypt traffic that he captured in the past when he learns the decryption key in the present.

Those two major advantages will be present in devices that are certified by the WPA3 certification program.
Devices that support WPA3 are already on the market and are expected to be widely adopted in the near 
future.

In this tutorial I will explain how to setup a WPA3 network on my laptop.

Unfortunately I could not setup a WPA3 network that makes use of **[protected management frames = IEEE 802.11w](https://en.wikipedia.org/wiki/IEEE_802.11w-2009)**

The reason is most likely that the device drivers do not support PMF.

For a WPA3 certified device, PMF are necessary, therefore the network we create in this tutorial is not a complete WPA3 certified network.

### Setup

In my case I have a Ubuntu 18.04 on my laptop and Kali Linux 2019.1 in a VMWare virtual machine.

I have three 802.11 network devices. 

1. One integrated wireless card in my laptop: 
```text
$ lspci -k
02:00.0 Network controller: Intel Corporation Centrino Advanced-N 6235 (rev 24)
Subsystem: Intel Corporation Centrino Advanced-N 6235 AGN
Kernel driver in use: iwlwifi
Kernel modules: iwlwifi
```
    
2. The Alfa dual band AWUS036ACH USB NIC. This is the driver I used: https://github.com/aircrack-ng/rtl8812au
    To install the driver, read this blog post: https://forums.hak5.org/topic/43124-alfa-awus036ach-kali-configuration-guide/
    We will not use this device in this tutorial, because it caused me too much headache and trouble.
    
3. A Panda N600 Wireless USB adapter using a Ralink chipset


I run **the access point on the kali machine with hostapd version 2.7**. I will use the Panda N600 Wireless USB adapter for the access point.

The **supplicant will run on the host machine of my laptop**. I will use my integrated Centrino Advanced-N 6235 AGN as the network card of the supplicant.

This setup means that 802.11 network is not mere hardware simulated, all frames are sent over the air!

### Compile Hostapd on Kali Linux 2019.1

All commands are executed from within the virtual machine running Kali Linux 2019.1

Download and extract the latest version of hostapd:

```bash
wget https://w1.fi/releases/hostapd-2.7.tar.gz
tar xzvf hostapd-2.7.tar.gz
cd hostapd-2.7/hostapd
```

After downloading the sources of hostapd, we need to install several packages/libraries that are necessary to compile hostapd and the supplicant.

```bash
apt install pkg-config
apt install libnl-3-dev
apt install libssl-dev
apt install libnl-genl-3-dev
```

Append the following lines to the end of the **defconfig** file:

```text
CONFIG_SAE=y
```

then compile hostapd

```bash
cp defconfig .config
make -j 2
cd ..
```

Now you should have a fresh binary **hostapd** that is compiled to support SAE as key management.

You can confirm that by running

```text
/hostapd-2.7/hostapd$ ./hostapd -v
hostapd v2.7
User space daemon for IEEE 802.11 AP management,
IEEE 802.1X/WPA/WPA2/EAP/RADIUS Authenticator
Copyright (c) 2002-2018, Jouni Malinen <j@w1.fi> and contributors
```

### Configure Hostapd to use SAE/Dragonfly

This is the configuration file (**wpa3.conf**) for hostapd that enbables WPA3 authentication:

```text
interface=wlan0
ssid=WPA3-Network

hw_mode=g
channel=1

wpa=2
wpa_passphrase=abcdefgh
wpa_key_mgmt=SAE
rsn_pairwise=CCMP
#ieee80211w=2
```

The line `wpa_key_mgmt=SAE` is the crucial part. It tells hostapd to use SAE as key management protocol.

Before you start hostapd, it's necessary to kill some programs that might interfere with hostapd.

My **/etc/NetworkManager/NetworkManager.conf** looks like this:

```
[main]
plugins=ifupdown,keyfile

[ifupdown]
managed=false

[device]
wifi.scan-rand-mac-address=no
```

I created this script (**prepare.sh**) to stop the potentially interfering network-manager:

```bash
#!/bin/bash

  if [ -z "$1" ]
  then
    echo "please specify interface as first arg";
  else
    # use airmon to stop interfering processes
    sudo airmon-ng check kill
  
    # then stop network manager
    # because airmon doesn't do a good job
    sudo service network-manager stop
    
    # enable hardware sim
    #sudo modprobe mac80211_hwsim radios=3
    rfkill unblock wifi

    # Optionally kill other Wi-Fi clients the brute-for way:
    sudo pkill wpa_supplicant

    # Put the interface in monitor mode the old fashioned way
    # Probably not necessary
    sudo ifconfig $1 down
    sudo iwconfig $1 mode monitor
    sudo ifconfig $1 up

    # To monitor traffic in wireshark you can execute
    # sudo ifconfig hwsim0 up
  fi
```

Execute the script with:

```bash
chmod +x prepare.sh
./prepare wlan0
```

Now we can finally start hostapd with

```bash
./hostapd wpa3.conf -dd -K
```


### Configure wpa_supplicant to connect to the wpa3 network

This commands need to be executed on the laptop (host machine).

First compile wpa_supplicant similar to how we compiled hostapd:

```bash
wget https://w1.fi/releases/wpa_supplicant-2.7.tar.gz
tar xzvf wpa_supplicant-2.7.tar.gz
cd wpa_supplicant-2.7/wpa_supplicant
```

Append `CONFIG_SAE=y` to **defconfig**

then

```bash
cp defconfig .config
make -j 2
cd ..
```

then save the supplicant configuration as **supp.conf** with the following contents:

```text
network={
	ssid="WPA3-Network"
	psk="abcdefgh"
	key_mgmt=SAE
	#ieee80211w=2
}
```

Kill all interfering processes with the following commands:

```bash
sudo service network-manager stop
sudo pkill wpa_supplicant
```

Then run the supplicant with

```bash
sudo ./wpa_supplicant -D nl80211 -i wlan0 -c supp.conf -K -dd
```

## Results

This are the outputs of the logfiles:

+ [wpa_supplicant log outputs](/data/supplicant_wpa3.log)
+ [hostapd log outputs](/data/hostapd_wpa3.log)

The interesting parts are the following exerpt from the wpa_supplicant logfile:

```text
SAE: counter = 40
SAE: pwd-seed - hexdump(len=32): af c2 76 6d e8 b7 ab c3 df da 4c 40 8d 04 a3 65 f8 03 90 2f d0 f9 ea cb 5b 41 63 6e cb 14 d3 ab
SAE: pwd-value - hexdump(len=32): d5 79 09 44 00 2f 7d ca 0e 6b 82 22 37 00 ea 43 84 c0 75 94 7e eb 40 74 c4 55 a6 62 1b 0e e8 da
Get randomness: len=32 entropy=0
Get randomness: len=32 entropy=0
Get randomness: len=32 entropy=0
SAE: own commit-scalar - hexdump(len=32): b0 d9 b4 04 38 49 44 4d 5b dd f7 ff 3d 3f 0d 4a 81 d7 bb f5 66 dc 4f cb ee 95 90 0d 9e 88 46 ef
SAE: own commit-element(x) - hexdump(len=32): ed 6b 81 c3 42 bb f1 9c 27 6f 87 98 07 37 ce cf 28 2e c0 81 75 16 e7 d0 0b db f6 de 8c 7b 26 0e
SAE: own commit-element(y) - hexdump(len=32): 90 ab e3 58 aa 19 64 12 15 2e ce bc 23 e2 10 25 3f e1 10 31 1b 1f 3d 4b 67 e1 44 25 94 c0 10 e0
EAPOL: External notification - EAP success=0
EAPOL: External notification - EAP fail=0
EAPOL: External notification - portControl=Auto
wlan0: Cancelling scan request
wlan0: SME: Trying to authenticate with 9c:ef:d5:fc:0e:a8 (SSID='WPA3-Network' freq=2412 MHz)
EAPOL: External notification - portValid=0
wlan0: State: SCANNING -> AUTHENTICATING
nl80211: Authenticate (ifindex=3)
  * bssid=9c:ef:d5:fc:0e:a8
  * freq=2412
  * SSID - hexdump_ascii(len=12):
     57 50 41 33 2d 4e 65 74 77 6f 72 6b               WPA3-Network    
  * IEs - hexdump(len=0): [NULL]
  * auth_data - hexdump(len=102): 01 00 00 00 13 00 b0 d9 b4 04 38 49 44 4d 5b dd f7 ff 3d 3f 0d 4a 81 d7 bb f5 66 dc 4f cb ee 95 90 0d 9e 88 46 ef ed 6b 81 c3 42 bb f1 9c 27 6f 87 98 07 37 ce cf 28 2e c0 81 75 16 e7 d0 0b db f6 de 8c 7b 26 0e 90 ab e3 58 aa 19 64 12 15 2e ce bc 23 e2 10 25 3f e1 10 31 1b 1f 3d 4b 67 e1 44 25 94 c0 10 e0
  * Auth Type 4
nl80211: Authentication request send successfully
nl80211: Event message available
nl80211: Drv Event 19 (NL80211_CMD_NEW_STATION) received for wlan0
nl80211: New station 9c:ef:d5:fc:0e:a8
nl80211: Event message available
nl80211: Drv Event 37 (NL80211_CMD_AUTHENTICATE) received for wlan0
nl80211: MLME event 37 (NL80211_CMD_AUTHENTICATE) on wlan0(c8:f7:33:d4:5a:e9) A1=c8:f7:33:d4:5a:e9 A2=9c:ef:d5:fc:0e:a8
nl80211: MLME event frame - hexdump(len=128): b0 00 3a 01 c8 f7 33 d4 5a e9 9c ef d5 fc 0e a8 9c ef d5 fc 0e a8 e0 1a 03 00 01 00 00 00 13 00 8c d8 b9 1c d9 d4 c1 1e 9b 55 2b 1e c7 cc 15 6d d7 e1 80 c0 cd 19 10 40 4a 14 27 1d 23 51 bf 00 76 ea 86 3b b4 b6 13 2f 1e 8d ba 94 a2 85 e6 28 cf 8b 45 4b 85 ad 3d 3a a2 47 74 39 3a 4a 68 06 a4 fa 78 d9 1c de 93 94 66 af ff 76 1e 2d 4f a7 c4 40 5a 0f f4 df 1c 5d 5a 47 88 39 84 7d 52 e0
nl80211: Authenticate event
wlan0: Event AUTH (10) received
wlan0: SME: Authentication response: peer=9c:ef:d5:fc:0e:a8 auth_type=3 auth_transaction=1 status_code=0
SME: Authentication response IEs - hexdump(len=98): 13 00 8c d8 b9 1c d9 d4 c1 1e 9b 55 2b 1e c7 cc 15 6d d7 e1 80 c0 cd 19 10 40 4a 14 27 1d 23 51 bf 00 76 ea 86 3b b4 b6 13 2f 1e 8d ba 94 a2 85 e6 28 cf 8b 45 4b 85 ad 3d 3a a2 47 74 39 3a 4a 68 06 a4 fa 78 d9 1c de 93 94 66 af ff 76 1e 2d 4f a7 c4 40 5a 0f f4 df 1c 5d 5a 47 88 39 84 7d 52 e0
wlan0: SME: SAE authentication transaction 1 status code 0
wlan0: SME SAE commit
SAE: Peer commit-scalar - hexdump(len=32): 8c d8 b9 1c d9 d4 c1 1e 9b 55 2b 1e c7 cc 15 6d d7 e1 80 c0 cd 19 10 40 4a 14 27 1d 23 51 bf 00
SAE: Peer commit-element(x) - hexdump(len=32): 76 ea 86 3b b4 b6 13 2f 1e 8d ba 94 a2 85 e6 28 cf 8b 45 4b 85 ad 3d 3a a2 47 74 39 3a 4a 68 06
SAE: Peer commit-element(y) - hexdump(len=32): a4 fa 78 d9 1c de 93 94 66 af ff 76 1e 2d 4f a7 c4 40 5a 0f f4 df 1c 5d 5a 47 88 39 84 7d 52 e0
SAE: Possible elements at the end of the frame - hexdump(len=0):
SAE: k - hexdump(len=32): 58 4a a1 15 2d 2b 89 37 11 27 6c 12 36 8e 3a 6c ed a8 06 7d fd 46 d4 9f 97 76 91 7f 66 b7 5f 3e
SAE: keyseed - hexdump(len=32): 77 21 44 e0 10 2c c9 05 4c 24 5a 9a 5f fb fb d6 9d be 1c 08 4d e8 7a b1 84 d7 8e 33 73 fb 55 5a
SAE: PMKID - hexdump(len=16): 3d b2 6d 22 12 1e 05 6a f7 33 23 1e 05 0b 22 b8
SAE: KCK - hexdump(len=32): 5e b5 32 c6 88 22 ad c9 7d 43 33 e9 b9 ea 7a 94 32 40 f0 a1 ed e8 7b af 5a 58 16 af 5a ff 46 57
SAE: PMK - hexdump(len=32): d8 ee 92 4b ba ff e4 7b 2f ea 85 5f be 12 fb f2 89 38 ad 8f 92 ec 99 3d 20 2f 10 76 9f e9 1a 38
wlan0: Automatic auth_alg selection: 0x1
wlan0: Using SAE auth_alg
RSN: PMKSA cache search - network_ctx=0x5566b646f620 try_opportunistic=0 akmp=0x0
RSN: Search for BSSID 9c:ef:d5:fc:0e:a8
RSN: No PMKSA cache entry found
wlan0: RSN: using IEEE 802.11i/D9.0
wlan0: WPA: Selected cipher suites: group 16 pairwise 16 key_mgmt 1024 proto 2
wlan0: WPA: Selected mgmt group cipher 32
wlan0: WPA: clearing AP WPA IE
WPA: set AP RSN IE - hexdump(len=22): 30 14 01 00 00 0f ac 04 01 00 00 0f ac 04 01 00 00 0f ac 08 00 00
wlan0: WPA: using GTK CCMP
wlan0: WPA: using PTK CCMP
wlan0: RSN: using KEY_MGMT SAE
wlan0: WPA: not using MGMT group cipher
WPA: Set own WPA IE default - hexdump(len=22): 30 14 01 00 00 0f ac 04 01 00 00 0f ac 04 01 00 00 0f ac 08 00 00
WPA: Leave previously set WPA IE default - hexdump(len=22): 30 14 01 00 00 0f ac 04 01 00 00 0f ac 04 01 00 00 0f ac 08 00 00
RRM: Determining whether RRM can be used - device support: 0x10
RRM: No RRM in network
Added supported operating classes IE - hexdump(len=19): 3b 11 51 51 53 54 73 74 75 76 77 78 79 7a 7b 7c 7d 7e 7f
RSN: PMKSA cache search - network_ctx=0x5566b646f620 try_opportunistic=0 akmp=0x400
RSN: Search for BSSID 9c:ef:d5:fc:0e:a8
RSN: No PMKSA cache entry found
EAPOL: External notification - EAP success=0
EAPOL: External notification - EAP fail=0
EAPOL: External notification - portControl=Auto
wlan0: Cancelling scan request
wlan0: SME: Trying to authenticate with 9c:ef:d5:fc:0e:a8 (SSID='WPA3-Network' freq=2412 MHz)
EAPOL: External notification - portValid=0
wlan0: State: AUTHENTICATING -> AUTHENTICATING
nl80211: Authenticate (ifindex=3)
  * bssid=9c:ef:d5:fc:0e:a8
  * freq=2412
  * SSID - hexdump_ascii(len=12):
     57 50 41 33 2d 4e 65 74 77 6f 72 6b               WPA3-Network    
  * IEs - hexdump(len=0): [NULL]
  * auth_data - hexdump(len=38): 02 00 00 00 00 00 bd 5a c1 80 bb 5a 5c 3c c7 c0 56 ab a3 d0 8a a3 8c 58 a0 79 00 e2 17 be 3a f1 fe 47 68 c6 26 11
  * Auth Type 4
nl80211: Authentication request send successfully
nl80211: Event message available
nl80211: Drv Event 20 (NL80211_CMD_DEL_STATION) received for wlan0
nl80211: Delete station 9c:ef:d5:fc:0e:a8
nl80211: Event message available
nl80211: Drv Event 19 (NL80211_CMD_NEW_STATION) received for wlan0
nl80211: New station 9c:ef:d5:fc:0e:a8
nl80211: Event message available
nl80211: Drv Event 37 (NL80211_CMD_AUTHENTICATE) received for wlan0
nl80211: MLME event 37 (NL80211_CMD_AUTHENTICATE) on wlan0(c8:f7:33:d4:5a:e9) A1=c8:f7:33:d4:5a:e9 A2=9c:ef:d5:fc:0e:a8
nl80211: MLME event frame - hexdump(len=64): b0 00 3a 01 c8 f7 33 d4 5a e9 9c ef d5 fc 0e a8 9c ef d5 fc 0e a8 f0 1a 03 00 02 00 00 00 00 00 31 f6 23 46 42 56 06 9f 8b da 5a 7b ef 66 6f 1a 43 7f 78 ce 1c 19 fb b1 c7 35 20 27 a2 72 e1 ea
nl80211: Authenticate event
wlan0: Event AUTH (10) received
wlan0: SME: Authentication response: peer=9c:ef:d5:fc:0e:a8 auth_type=3 auth_transaction=2 status_code=0
SME: Authentication response IEs - hexdump(len=34): 00 00 31 f6 23 46 42 56 06 9f 8b da 5a 7b ef 66 6f 1a 43 7f 78 ce 1c 19 fb b1 c7 35 20 27 a2 72 e1 ea
wlan0: SME: SAE authentication transaction 2 status code 0
wlan0: SME SAE confirm
SAE: peer-send-confirm 0
SME: SAE completed - setting PMK for 4-way handshake
```

At the end you can see the message **SME: SAE completed - setting PMK for 4-way handshake**.

This tells us that SEA was used to derive a PMK that will be used for the 4-way handshake.

## Open questions

Unfortunately I could not manage to support `ieee80211w=2` in my configuration.

The reason is probably because the drivers do not support the ieee80211w amendment.
