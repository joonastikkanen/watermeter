import os
from camera import take_picture
from flask import redirect, url_for, app

@app.route('/take_new_picture', methods=['POST'])
def take_new_picture():
    take_picture()
    return redirect(url_for('preview'))