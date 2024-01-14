from camera import take_picture
from reader import read_image
from flask import Flask
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    return app

app = create_app()

def load_sensor_data():
    watermeter_last_value_file = app.config['watermeter_last_value_file']
    try:
        with open(watermeter_last_value_file, 'r') as f:
            sensor_data = int(f.read())
    except FileNotFoundError:
        print(f"Info: The last value file {watermeter_last_value_file} is not found. Running reader function.")
        take_picture()
        read_image()

    return sensor_data
