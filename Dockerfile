FROM dtcooper/raspberrypi-os:python3.11

ADD . /usr/src/watermeter

WORKDIR /usr/src/watermeter

RUN apt update && DEBIAN_FRONTEND=noninteractive apt install -y python3-libcamera tesseract-ocr libtesseract-dev python3-pyqt5 python3-prctl libatlas-base-dev ffmpeg python3-pip python3-av python3-prctl libcap-dev criu && \
    python3 -m venv --system-site-packages venv && \
    . ./venv/bin/activate && \
    pip3 install -r requirements.txt && \
    rm -rf /var/lib/apt/lists/*

EXPOSE 5000

VOLUME [ "/dev/" ]

CMD ["/usr/src/watermeter/venv/bin/gunicorn", "-w", "2", "'run:app'"]

