import os
import logging
from flask import Flask
from flask_login import LoginManager
from flask_pymongo import PyMongo

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Create the Flask application
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev-secret-key")

# Configure MongoDB
app.config["MONGO_URI"] = "mongodb://localhost:27017/ticketApp"
print(f"\n\n\n\n\n{app.config['MONGO_URI']}\n\n\n\n\n")
mongo = PyMongo(app)

# Setup Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Import models after initialization to avoid circular imports
from models import User

@login_manager.user_loader
def load_user(user_id):
    return User.get_by_id(user_id)

# Import routes after app initialization to avoid circular imports
from routes import *
