# Raspberry PI Watermeter using camera

NOT FULLY TESTED YEAT!!

I was inspired by old project nohn's project about using raspberry PI camera as to bring smartness to old school watermeter. 

Links:
* The nohn's project: https://github.com/nohn/watermeter/tree/main

## Install dependencies

```bash
sudo apt install -y python3-libcamera tesseract-ocr libtesseract-dev python3-pyqt5 python3-prctl libatlas-base-dev ffmpeg python3-pip
```

```bash
python3 -m venv venv
source venv/bin/activate 
pip3 install -r requirements.txt
```

## Install to Raspberry

Copy files

Create Systemd Service:

```bash
sudo nano /etc/systemd/system/watermeter.service
```

Create systemd file:

```ini
[Unit]
Description=My Watermeter

[Service]
ExecStart=/usr/bin/python3 /path/to/your/main.py

Restart=always
User=${USER}
Environment=PICAMERA_IMAGE_PATH=/run/shm/watermeter_last.jpg
Environment=PICAMERA_CONFIG='{"size": (1920, 1080)}'
Environment=TESSERACT_PATH=/usr/bin/tesseract
Environment=TESSERACT_CONFIG='--psm 6 -c tessedit_char_whitelist=0123456789'

[Install]
WantedBy=multi-user.target
```

Replace `/path/to/your/main.py` with the actual path to your `main.py` file and `yourusername` with your actual username. Also, replace `your_token` with your actual Home Assistant token.

3. Save the file and exit the editor.

4. Reload the systemd manager configuration:

```bash
sudo systemctl daemon-reload
```

5. Enable your service to start on boot:

```bash
sudo systemctl enable watermeter
```

6. Start your service:

```bash
sudo systemctl start watermeter
```

Now, your Python script will run as a systemd service. It will start automatically when your system boots, and if it crashes, systemd will restart it.

## HomeAssistant sensor

```yaml
sensor:
  - platform: rest
    name: Water
    resource: "http://ip.or.hostname.of.watermeter:3000/"
    scan_interval: 60
    unit_of_measurement: 'm³'
    device_class: water
    state_class: total_increasing
```