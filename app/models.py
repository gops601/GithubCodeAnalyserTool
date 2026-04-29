from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class Batch(db.Model):
    __tablename__ = 'batches'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    repositories = db.relationship('Repository', backref='batch', lazy=True, cascade="all, delete-orphan")

class Repository(db.Model):
    __tablename__ = 'repositories'
    id = db.Column(db.Integer, primary_key=True)
    batch_id = db.Column(db.Integer, db.ForeignKey('batches.id'), nullable=False)
    url = db.Column(db.String(1024), nullable=False)
    project_key = db.Column(db.String(255), nullable=False)
    status = db.Column(db.String(50), default='Pending')  # Pending, Running, Completed, Failed
    error_message = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    results = db.relationship('AnalysisResult', backref='repository', lazy=True, cascade="all, delete-orphan")

class AnalysisResult(db.Model):
    __tablename__ = 'analysis_results'
    id = db.Column(db.Integer, primary_key=True)
    repository_id = db.Column(db.Integer, db.ForeignKey('repositories.id'), nullable=False)
    bugs = db.Column(db.Integer, default=0)
    vulnerabilities = db.Column(db.Integer, default=0)
    code_smells = db.Column(db.Integer, default=0)
    coverage = db.Column(db.Float, default=0.0)
    duplications = db.Column(db.Float, default=0.0)
    ncloc = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
