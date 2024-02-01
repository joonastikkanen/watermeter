FROM dtcooper/raspberrypi-os:python3.11

WORKDIR /usr/src/watermeter

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt update && \ 
DEBIAN_FRONTEND=noninteractive apt install -y python3-libcamera tesseract-ocr libtesseract-dev python3-pyqt5 python3-prctl \ 
               libatlas-base-dev ffmpeg python3-pip python3-av python3-prctl libcap-dev \ 
               python3-gunicorn python3-kms++ libcamera0.1 libyaml-dev python3-yaml python3-ply \
               python3-jinja2 libcamera-ipa libpython3-dev pybind11-dev libraspberrypi0


COPY requirements.txt /usr/src/watermeter/requirements.txt

RUN python -m venv --system-site-packages /usr/src/watermeter/venv

ENV PATH="/usr/src/watermeter/venv/bin:$PATH"

RUN pip3 install --upgrade pip && pip3 install -r requirements.txt

COPY . /usr/src/watermeter

EXPOSE 5000

CMD ["/usr/src/watermeter/venv/bin/gunicorn", "-w", "2", "run:app", "--bind", "0.0.0.0:8000"]
