import openai
import pandas as pd
import time
from datetime import datetime
import json
import os



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



def build_openai_prompt(nom, description, website, demo_url, linkedin_url, booking_url, langue="français"):
    prompt = f"""
Tu es un expert en prospection commerciale B2B dans le secteur de la bijouterie.

Contexte :
- Tu contactes la bijouterie "{nom}".
- Voici leur description publique : "{description}"
- Leur site web : {website}
- Tu proposes un service de **chatbot intelligent** adapté aux bijouteries : disponible 24h/24 pour répondre à toutes les questions des clients, conseiller, générer des ventes, gérer le SAV, soulager les équipes et améliorer l'expérience client.

Ta mission :
- Rédige un e-mail de prospection **personnalisé** et convaincant, en mettant en avant :
    * La valeur ajoutée pour cette bijouterie en particulier (adapte le texte à leur univers, gamme ou valeur)
    * Le fait que tu as déjà développé une démo spécialement pour eux, accessible ici : {demo_url}
    * Un lien vers ton LinkedIn professionnel : {linkedin_url}
    * Un lien pour réserver un créneau dans ton agenda et discuter en direct : {booking_url}
- L'e-mail doit être court (6 à 8 lignes), humain, professionnel, et donner envie d'essayer la démo ou de booker un rendez-vous.
- Termine par une phrase d'appel à l'action claire.
- Commence toujours par "Bonjour," en t'adressant au responsable, sans formule trop générique.
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



def process_csv_and_generate_emails(csv_path, demo_url, linkedin_url, booking_url):
    """
    Charge le CSV, génère les emails personnalisés et sauvegarde le résultat
    """
    try:
        # Charger le CSV
        print(f"Chargement du fichier CSV : {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"Nombre de bijouteries trouvées : {len(df)}")
        
        # Initialiser les colonnes pour les emails
        df['email_objet'] = ''
        df['email_corps'] = ''
        df['email_generation_status'] = ''
        
        # Générer les emails pour chaque bijouterie
        for index, row in df.iterrows():
            print(f"Génération email pour {row['nom']} ({index+1}/{len(df)})")
            
            # Construire le prompt
            prompt = build_openai_prompt(
                nom=row['nom'],
                description=row['description'] if pd.notna(row['description']) else "Bijouterie",
                website=row['website'] if pd.notna(row['website']) else "Site web non disponible",
                demo_url=demo_url,
                linkedin_url=linkedin_url,
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
    # Configuration des URLs (à modifier selon vos besoins)
    demo_url = "https://votre-demo-url.com"
    linkedin_url = "https://linkedin.com/in/votre-profil"
    booking_url = "https://calendly.com/votre-lien"
    
    # Chemin vers le fichier CSV
    csv_path = "data/trustpilot_bijouteries_final_20250524_152732.csv"
    
    # Vérifier que le fichier existe
    if not os.path.exists(csv_path):
        print(f"Erreur : Le fichier {csv_path} n'existe pas.")
        return
    
    # Traiter le CSV et générer les emails
    output_file = process_csv_and_generate_emails(csv_path, demo_url, linkedin_url, booking_url)
    
    if output_file:
        print(f"Traitement terminé avec succès ! Fichier de sortie : {output_file}")
    else:
        print("Erreur lors du traitement.")

if __name__ == "__main__":
    main()