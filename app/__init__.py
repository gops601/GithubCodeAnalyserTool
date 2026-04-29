from flask import Flask
from app.models import db
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    db_host = os.getenv('DB_HOST', 'localhost')
    db_user = os.getenv('DB_USER', 'root')
    db_pass = os.getenv('DB_PASSWORD', 'Admin123')
    db_name = os.getenv('DB_NAME', 'sonar_devops')
    
    app.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+mysqlconnector://{db_user}:{db_pass}@{db_host}/{db_name}'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret')

    # Create database if not exists
    try:
        conn = mysql.connector.connect(host=db_host, user=db_user, password=db_pass)
        cursor = conn.cursor()
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Warning: Could not auto-create database: {e}")

    db.init_app(app)

    with app.app_context():
        from app import routes
        app.register_blueprint(routes.bp)
        db.create_all()

    return app
