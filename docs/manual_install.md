# Install Watermeter manually

Base OS is Rasbian Bookworm 64bit.

## Install dependencies

```bash
sudo apt install -y python3-libcamera python3-pyqt5 python3-prctl libatlas-base-dev ffmpeg python3-pip python3-av python3-prctl libcap-dev
```

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate 
pip3 install -r requirements.txt
```

## To run flask app on debug mode

```
export FLASK_APP=run.py
flask run --debug
```