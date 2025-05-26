from flask import Flask, request, jsonify
from flask_cors import CORS
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from datetime import datetime
import logging

# Configuration
app = Flask(__name__)
CORS(app)  # Permettre les requêtes depuis le frontend

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration email Zoho
SMTP_SERVER = "smtp.zoho.eu"
SMTP_PORT = 587  # STARTTLS
EMAIL_ADDRESS = "contact@magickbot.com"
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD', 'VOTRE_MOT_DE_PASSE_ZOHO')  # À mettre dans les variables d'environnement

def send_email(nom, email, entreprise, telephone, budget, message):
    """Envoie un email avec les informations du formulaire"""
    try:
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = EMAIL_ADDRESS
        msg['To'] = EMAIL_ADDRESS
        msg['Subject'] = f"Nouveau contact Magickbot - {nom}"
        
        # Corps de l'email
        body = f"""
        Nouveau message de contact depuis le site Magickbot :
        
        📧 INFORMATIONS CLIENT
        ───────────────────────
        Nom : {nom}
        Email : {email}
        Entreprise : {entreprise or 'Non spécifiée'}
        Téléphone : {telephone or 'Non spécifié'}
        Budget : {budget or 'Non spécifié'}
        
        💬 MESSAGE
        ───────────────────────
        {message}
        
        📅 Reçu le : {datetime.now().strftime('%d/%m/%Y à %H:%M:%S')}
        
        ───────────────────────
        Email automatique - Magickbot Contact Form
        """
        
        msg.attach(MIMEText(body, 'plain', 'utf-8'))
        
        # Connexion et envoi
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Activer le chiffrement
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        
        text = msg.as_string()
        server.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, text)
        server.quit()
        
        logger.info(f"Email envoyé avec succès pour {nom} ({email})")
        return True
        
    except Exception as e:
        logger.error(f"Erreur lors de l'envoi de l'email : {str(e)}")
        return False

@app.route('/api/contact', methods=['POST'])
def handle_contact():
    """Endpoint pour traiter les soumissions du formulaire de contact"""
    try:
        # Récupérer les données du formulaire
        data = request.get_json()
        
        # Validation des champs requis
        required_fields = ['nom', 'email', 'message']
        for field in required_fields:
            if not data.get(field):
                return jsonify({
                    'success': False,
                    'message': f'Le champ {field} est requis'
                }), 400
        
        # Extraire les données
        nom = data.get('nom', '').strip()
        email = data.get('email', '').strip()
        entreprise = data.get('entreprise', '').strip()
        telephone = data.get('telephone', '').strip()
        budget = data.get('budget', '').strip()
        message = data.get('message', '').strip()
        
        # Validation email basique
        if '@' not in email or '.' not in email:
            return jsonify({
                'success': False,
                'message': 'Adresse email invalide'
            }), 400
        
        # Envoyer l'email
        if send_email(nom, email, entreprise, telephone, budget, message):
            return jsonify({
                'success': True,
                'message': 'Votre message a été envoyé avec succès ! Nous vous répondrons rapidement.'
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Erreur lors de l\'envoi du message. Veuillez réessayer.'
            }), 500
            
    except Exception as e:
        logger.error(f"Erreur dans handle_contact : {str(e)}")
        return jsonify({
            'success': False,
            'message': 'Une erreur inattendue s\'est produite'
        }), 500

@app.route('/api/health', methods=['GET'])
def health_check():
    """Endpoint pour vérifier que l'API fonctionne"""
    return jsonify({
        'status': 'OK',
        'message': 'Backend Magickbot opérationnel',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/', methods=['GET'])
def home():
    """Page d'accueil de l'API"""
    return jsonify({
        'message': 'API Magickbot Contact Form',
        'version': '1.0',
        'endpoints': {
            'POST /api/contact': 'Envoyer un message de contact',
            'GET /api/health': 'Vérifier le statut de l\'API'
        }
    })

if __name__ == '__main__':
    # Pour le développement local
    app.run(debug=True, host='0.0.0.0', port=5000)
