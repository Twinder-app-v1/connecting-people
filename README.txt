## To activate your virtual environment:
- virtualenv env
- source env/bin/activate

## To install flask:
- pip install flask

## To install package
- pip install flask_socketio
- pip install bcrypt

## Set the server:
- flask run

Run server:
    gunicorn -b 0.0.0.0:80 app:app



