# Twinder-app-v1: Connecting People Together

Introducing Twinder-app-v1, a platform designed to connect people together. The "connecting-people" repository offers a seamless way to build and deploy a web application for fostering connections between individuals.

## Key Features:

- **User-friendly Interface**: Leverage pre-built templates for creating an engaging and intuitive user experience.
- **Real-time Communication**: Integrated chat functionality using Flask-SocketIO, allowing users to interact and build connections in real time.
- **Secure Authentication**: The app employs the bcrypt library for secure password hashing and protection of user data.
- **Easy Deployment**: Deploy your application effortlessly with gunicorn, ensuring compatibility and optimal performance across various environments.
- **Comprehensive Documentation**: The README.txt file provides clear instructions for setting up a virtual environment, installing dependencies, and running the server.

Twinder-app-v1 is an ideal starting point for developers looking to create a social networking platform that fosters meaningful connections between people. With its easy-to-follow instructions and robust features, you'll be able to get your app up and running in no time.

## Getting Started

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



