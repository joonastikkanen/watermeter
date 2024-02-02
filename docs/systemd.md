# Watermeter systemd service

Create file to **/etc/systemd/system/watermeter.service**

Modify the service template:
```
[Unit]
Description=Watermeter
After=network.target

[Service]
User=$USER
WorkingDirectory=<DIR TO APP>/app
Environment="USER=<USER>"
Environment="PATH=<DIR TO APP>/venv/bin"
ExecStart=<DIR TO APP>/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 run:app

[Install]
WantedBy=multi-user.target
```

Reload and restart

```bash
$ sudo systemctl daemon-reload 
$ sudo systemctl start watermeter
$ systemctl status watermeter
```

