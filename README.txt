1. To activate your virtual environment:
- virtualenv env
- source env/bin/activate

2. To install flask:
- pip install flask

3. To install package
- pip install flask_socketio
- pip install bcrypt

4.Set the server:
- flask run

Run server:
    gunicorn -b 0.0.0.0:80 app:app



