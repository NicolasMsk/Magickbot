import openai
import pandas as pd
import time
from datetime import datetime
import json
import os
from dotenv import load_dotenv

# Charger les variables d'environnement
load_dotenv()

# Configurer la clé API OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

if not openai.api_key:
    raise ValueError("OPENAI_API_KEY non trouvée dans les variables d'environnement. Vérifiez votre fichier .env")


def generate_e_mail_bijouterie(text):
    try:
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "Tu es un expert en prospection commerciale B2B dans le secteur de la bijouterie. Tu rédiges des e-mails de prospection personnalisés et convaincants qui évitent les filtres anti-spam."},
                {"role": "user", "content": text}
            ],
            max_tokens=500,
            temperature=0.7
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Erreur lors de la génération de l'e-mail : {str(e)}")
        return None



def build_openai_prompt(nom, description, website, demo_url, website_url, booking_url, langue="français"):
    prompt = f"""
Tu es Nicolas Musicki, expert en prospection commerciale B2B dans le secteur de la bijouterie.

Contexte :
- Tu contactes la bijouterie "{nom}".
- Voici leur description publique : "{description}"
- Leur site web : {website}
- Tu proposes un service de **chatbot intelligent** adapté aux bijouteries : disponible 24h/24 pour répondre à toutes les questions des clients, conseiller, générer des ventes, gérer le SAV, soulager les équipes et améliorer l'expérience client.

Ta mission :
- Rédige un e-mail de prospection **personnalisé** et convaincant, en mettant en avant :
    * La valeur ajoutée pour cette bijouterie en particulier (adapte le texte à leur univers, gamme ou valeur)
    * Le fait que tu as déjà créé un chatbot spécialement pour leur site web après avoir analysé leur activité
    * Que si cela les intéresse, ils peuvent booker un créneau avec toi pour une démo en live personnalisée
    * Pendant cette démo, tu pourras poser des questions sur leur site, comprendre leurs besoins spécifiques et leur montrer exactement comment le chatbot peut s'adapter à leur bijouterie
    * Un lien vers ton site web professionnel : {website_url}
    * Un lien pour réserver un créneau dans ton agenda : {booking_url}
    * Ton numéro de téléphone : 07 56 93 16 47
- L'e-mail doit être court (6 à 8 lignes), humain, professionnel, et donner envie de booker un rendez-vous pour la démo personnalisée.
- Termine par une phrase d'appel à l'action claire pour booker la démo.
- Commence toujours par "Bonjour," en t'adressant au responsable, sans formule trop générique.
- Signe avec "Cordialement, Nicolas Musicki" et ajoute ton numéro de téléphone.
- ULTRA IMPORTANT : L'e-mail doit avoir l'air écrit par un humain au maximum. Utilise un ton naturel, spontané et authentique. Évite le jargon commercial et les formules trop polies ou robotiques.
- IMPORTANT : Évite les mots qui déclenchent les filtres anti-spam comme "gratuit", "urgent", "offre limitée", "garantie", "promotion".
- Utilise un ton naturel et professionnel, évite les majuscules excessives et les points d'exclamation multiples.

**Réponds strictement au format JSON suivant :**
{{
  "objet": "Titre de l'objet du mail (professionnel, sans mots spam)",
  "corps": "Le corps du texte du mail"
}}

Langue du message : {langue}

N'ajoute jamais de liens imaginaires : les liens doivent être exactement ceux ci-dessus.
"""
    return prompt

def process_csv_and_generate_emails(csv_path, website_url, booking_url):
    """
    Charge le CSV, génère les emails personnalisés et sauvegarde le résultat
    """
    try:
        # Charger le CSV
        print(f"Chargement du fichier CSV : {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"Nombre de bijouteries trouvées : {len(df)}")
        
        # Prendre seulement les 10 premières lignes pour les tests
        df = df.head(10)
        print(f"Utilisation des 10 premières bijouteries pour les tests")
        
        # Initialiser les colonnes pour les emails
        df['email_objet'] = ''
        df['email_corps'] = ''
        df['email_generation_status'] = ''
        
        # Générer les emails pour chaque bijouterie
        for index, row in df.iterrows():
            print(f"Génération email pour {row['nom']} ({index+1}/{len(df)})")
            
            # Construire le prompt (sans demo_url)
            prompt = build_openai_prompt(
                nom=row['nom'],
                description=row['description'] if pd.notna(row['description']) else "Bijouterie",
                website=row['website'] if pd.notna(row['website']) else "Site web non disponible",
                demo_url="",  # Plus besoin
                website_url=website_url,
                booking_url=booking_url,
                langue="français"
            )
            
            # Générer l'email
            email_response = generate_e_mail_bijouterie(prompt)
            
            if email_response:
                try:
                    # Parser la réponse JSON
                    email_data = json.loads(email_response)
                    df.at[index, 'email_objet'] = email_data.get('objet', '')
                    df.at[index, 'email_corps'] = email_data.get('corps', '')
                    df.at[index, 'email_generation_status'] = 'Succès'
                    print(f"✓ Email généré avec succès pour {row['nom']}")
                except json.JSONDecodeError:
                    df.at[index, 'email_objet'] = ''
                    df.at[index, 'email_corps'] = email_response
                    df.at[index, 'email_generation_status'] = 'Erreur JSON'
                    print(f"✗ Erreur JSON pour {row['nom']}")
            else:
                df.at[index, 'email_objet'] = ''
                df.at[index, 'email_corps'] = ''
                df.at[index, 'email_generation_status'] = 'Erreur génération'
                print(f"✗ Erreur génération pour {row['nom']}")
            
            # Pause pour éviter les limites de taux
            time.sleep(1)
        
        # Sauvegarder le fichier avec les emails générés
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_path = f"data/bijouteries_avec_emails_{timestamp}.csv"
        df.to_csv(output_path, index=False, encoding='utf-8')
        print(f"Fichier sauvegardé : {output_path}")
        
        # Afficher un résumé
        success_count = len(df[df['email_generation_status'] == 'Succès'])
        print(f"\nRésumé :")
        print(f"- Emails générés avec succès : {success_count}/{len(df)}")
        print(f"- Fichier de sortie : {output_path}")
        
        return output_path
        
    except Exception as e:
        print(f"Erreur lors du traitement : {str(e)}")
        return None

# Fonction principale pour exécuter le script
def main():
    # Configuration des URLs (sans demo_url)
    website_url = "https://magickbot.com/"
    booking_url = "https://magickbot.zohobookings.eu/#/magickbot"
    
    # Chemin vers le fichier CSV
    csv_path = "data/trustpilot_bijouteries_final_20250524_152732.csv"
    
    # Vérifier que le fichier existe
    if not os.path.exists(csv_path):
        print(f"Erreur : Le fichier {csv_path} n'existe pas.")
        return
    
    # Traiter le CSV et générer les emails (sans demo_url)
    output_file = process_csv_and_generate_emails(csv_path, website_url, booking_url)
    
    if output_file:
        print(f"Traitement terminé avec succès ! Fichier de sortie : {output_file}")
    else:
        print("Erreur lors du traitement.")

if __name__ == "__main__":
    main()