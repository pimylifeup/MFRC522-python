# Setup for raspberry headless

- Install raspbian light
- CWD in /boot
- place a file called '**ssh**' in the root for auto start ssh service
- wifi config file **wpa_supplicant.conf**

```
country=US
ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1

network={
    scan_ssid=1
    ssid="your_wifi_ssid"
    psk="your_wifi_password"
}
```

- connect to raspberry via ssh

``` 
ssh pi@raspberrypi.local
```

- setup all other things via **raspi-config**



## Needed pyhton packages

Install only python3 packages

```
sudo apt-get update && apt-get install -y python3 python3-pip rpi.gpio python3-smbus
```

Python pip packages

```
sudo pip3 install -f requirements.txt
```




