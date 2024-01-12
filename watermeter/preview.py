import os
from camera import take_picture
from reader import read_image
from flask import render_template_string, app

@app.route('/preview')
def preview():
    take_picture()
    read_image()
    try:
        return render_template_string("""
            <img src="{{ url_for('last_image') }}" alt="Last image">
            <form action="{{ url_for('take_new_picture') }}" method="post">
                <button type="submit">Take New Picture</button><br>
                Sensor data: {{ url_for('root') }}
            </form>
        """)
    except FileNotFoundError:
        return "No image found", 404