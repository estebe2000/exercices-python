"""
Modèles de base de données pour l'application Flask.

Ce module contient les définitions des modèles SQLAlchemy utilisés dans l'application.
"""

from flask_sqlalchemy import SQLAlchemy

# Cette instance sera initialisée dans app.py
db = SQLAlchemy()

# Modèle Document
class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom_fichier = db.Column(db.String(255), nullable=False)
    nom_unique = db.Column(db.String(36), unique=True)  # UUID4
    date_upload = db.Column(db.DateTime, default=db.func.current_timestamp())
    taille_fichier = db.Column(db.Integer)  # Taille en octets
    type_mime = db.Column(db.String(100))  # Type MIME du fichier
    description = db.Column(db.Text)  # Description optionnelle
    user_id = db.Column(db.Integer)
    est_cours = db.Column(db.Boolean, default=False)  # Indique si le document est un cours
    tags = db.relationship('Tag', secondary='document_tags', backref='documents')

# Modèle Tag
class Tag(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nom = db.Column(db.String(50), unique=True)

# Table de liaison
class DocumentTag(db.Model):
    __tablename__ = 'document_tags'
    document_id = db.Column(db.Integer, db.ForeignKey('document.id'), primary_key=True)
    tag_id = db.Column(db.Integer, db.ForeignKey('tag.id'), primary_key=True)
