# Raspberry PI Watermeter using camera

NOT FULLY TESTED YEAT!!

I was inspired by old project nohn's project about using raspberry PI camera as to bring smartness to old school watermeter. 

Links:
* The nohn's project: https://github.com/nohn/watermeter/tree/main

## Install dependencies

```bash
sudo apt install -y python3-libcamera tesseract-ocr libtesseract-dev python3-pyqt5 python3-prctl libatlas-base-dev ffmpeg python3-pip python3-av python3-prctl libcap-dev
```

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate 
pip3 install -r requirements.txt
export PYTHONPATH=$PYTHONPATH:~/Documents/git/watermeter/watermeter
export FLASK_APP=main.py
```

To run flask app

```
flask run --debug
```

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
