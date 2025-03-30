"""
Routes pour la Gestion Électronique de Documents (GED).

Ce module contient les routes pour la GED, qui permet de gérer les documents
(upload, visualisation, édition, suppression, etc.).
"""

import os
import uuid
from flask import render_template, request, jsonify, redirect, url_for, send_file
from werkzeug.utils import secure_filename
from models import Document, Tag, db

def init_routes(app):
    """
    Initialise les routes pour la GED.
    
    Args:
        app: L'application Flask
    """
    
    @app.route('/ged')
    def ged():
        """Route pour afficher la page principale de la GED."""
        # Récupérer tous les documents et tags
        documents = Document.query.order_by(Document.date_upload.desc()).all()
        tags = Tag.query.order_by(Tag.nom).all()
        return render_template('ged.html', documents=documents, tags=tags)

    @app.route('/ged/upload', methods=['POST'])
    def upload_document():
        """Route pour uploader un nouveau document."""
        if 'file' not in request.files:
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'Aucun fichier sélectionné'}), 400
        
        # Générer un nom unique pour le fichier
        unique_filename = str(uuid.uuid4())
        
        # Récupérer les tags
        tag_names = request.form.get('tags', '').split(',')
        tag_names = [tag.strip() for tag in tag_names if tag.strip()]
        
        # Sauvegarder le fichier
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
        file.save(file_path)
        
        # Créer le document en base de données
        document = Document(
            nom_fichier=filename,
            nom_unique=unique_filename,
            taille_fichier=os.path.getsize(file_path),
            type_mime=file.content_type,
            description=request.form.get('description', ''),
            user_id=1  # À remplacer par l'ID de l'utilisateur connecté
        )
        
        # Ajouter les tags
        for tag_name in tag_names:
            # Vérifier si le tag existe déjà
            tag = Tag.query.filter_by(nom=tag_name).first()
            if not tag:
                # Créer le tag s'il n'existe pas
                tag = Tag(nom=tag_name)
                db.session.add(tag)
            document.tags.append(tag)
        
        db.session.add(document)
        db.session.commit()
        
        return jsonify({'success': True, 'document_id': document.id})

    @app.route('/ged/document/<int:document_id>')
    def view_document(document_id):
        """Route pour visualiser un document."""
        document = Document.query.get_or_404(document_id)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], document.nom_unique)
        return send_file(file_path, download_name=document.nom_fichier)

    @app.route('/ged/edit/<int:document_id>', methods=['GET', 'POST'])
    def edit_document(document_id):
        """Route pour éditer un document."""
        document = Document.query.get_or_404(document_id)
        
        if request.method == 'POST':
            # Mettre à jour les informations du document
            document.nom_fichier = request.form.get('nom_fichier', document.nom_fichier)
            document.description = request.form.get('description', document.description)
            
            # Mettre à jour les tags
            tag_names = request.form.get('tags', '').split(',')
            tag_names = [tag.strip() for tag in tag_names if tag.strip()]
            
            # Supprimer tous les tags existants
            document.tags = []
            
            # Ajouter les nouveaux tags
            for tag_name in tag_names:
                # Vérifier si le tag existe déjà
                tag = Tag.query.filter_by(nom=tag_name).first()
                if not tag:
                    # Créer le tag s'il n'existe pas
                    tag = Tag(nom=tag_name)
                    db.session.add(tag)
                document.tags.append(tag)
            
            db.session.commit()
            return redirect(url_for('ged'))
        
        # Récupérer tous les tags pour l'autocomplétion
        all_tags = Tag.query.order_by(Tag.nom).all()
        
        return render_template('edit_document.html', document=document, all_tags=all_tags)

    @app.route('/ged/delete/<int:document_id>', methods=['POST'])
    def delete_document(document_id):
        """Route pour supprimer un document."""
        document = Document.query.get_or_404(document_id)
        
        # Supprimer le fichier physique
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], document.nom_unique)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Supprimer le document de la base de données
        db.session.delete(document)
        db.session.commit()
        
        return redirect(url_for('ged'))

    @app.route('/ged/toggle-cours/<int:document_id>', methods=['POST'])
    def toggle_cours(document_id):
        """Route pour marquer/démarquer un document comme cours."""
        document = Document.query.get_or_404(document_id)
        
        # Inverser la valeur du champ est_cours
        document.est_cours = not document.est_cours
        
        db.session.commit()
        
        return jsonify({
            'success': True,
            'est_cours': document.est_cours
        })

    @app.route('/cours')
    def cours():
        """Route pour afficher la page des cours (documents en mode lecture avec style bibliothèque)."""
        query = request.args.get('q', '')
        tag = request.args.get('tag', '')
        
        # Base de la requête - ne récupérer que les documents marqués comme cours
        documents_query = Document.query.filter_by(est_cours=True)
        
        # Filtrer par texte de recherche
        if query:
            documents_query = documents_query.filter(Document.nom_fichier.ilike(f'%{query}%'))
        
        # Filtrer par tag
        if tag:
            documents_query = documents_query.join(Document.tags).filter(Tag.nom == tag)
        
        # Exécuter la requête
        documents = documents_query.order_by(Document.date_upload.desc()).all()
        
        # Récupérer tous les tags pour les filtres
        tags = Tag.query.order_by(Tag.nom).all()
        
        return render_template('cours.html', documents=documents, tags=tags, query=query, selected_tag=tag)

    @app.route('/ged/search')
    def search_documents():
        """Route pour rechercher des documents."""
        query = request.args.get('q', '')
        tag = request.args.get('tag', '')
        
        # Base de la requête
        documents_query = Document.query
        
        # Filtrer par texte de recherche
        if query:
            documents_query = documents_query.filter(Document.nom_fichier.ilike(f'%{query}%'))
        
        # Filtrer par tag
        if tag:
            documents_query = documents_query.join(Document.tags).filter(Tag.nom == tag)
        
        # Exécuter la requête
        documents = documents_query.order_by(Document.date_upload.desc()).all()
        
        # Récupérer tous les tags pour les filtres
        tags = Tag.query.order_by(Tag.nom).all()
        
        return render_template('ged.html', documents=documents, tags=tags, query=query, selected_tag=tag)
