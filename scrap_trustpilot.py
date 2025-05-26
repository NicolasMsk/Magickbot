import requests 
from bs4 import BeautifulSoup
import pandas as pd
import time
import re
from urllib.parse import urlparse
import random
from fake_useragent import UserAgent

BASE_URL = "https://fr.trustpilot.com"
CAT_URL = f"{BASE_URL}/categories/jewelry_store"

# Pool of User-Agents for rotation
ua = UserAgent()
user_agents = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15"
]

def get_random_headers():
    """Get random headers for requests"""
    return {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "fr-FR,fr;q=0.9,en;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Cache-Control": "max-age=0"
    }

def make_request_with_retry(url, max_retries=3, base_delay=1):
    """Make request with exponential backoff retry"""
    for attempt in range(max_retries):
        try:
            headers = get_random_headers()
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                return response
            elif response.status_code == 403:
                print(f"  ⚠️  403 Forbidden (tentative {attempt + 1}/{max_retries})")
                if attempt < max_retries - 1:
                    time.sleep(delay * 2)  # Double delay on 403
            else:
                response.raise_for_status()
                
        except requests.exceptions.RequestException as e:
            print(f"  ⚠️  Erreur réseau (tentative {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(base_delay * (2 ** attempt))
    
    raise requests.exceptions.RequestException(f"Échec après {max_retries} tentatives")

def save_partial_results(results, filename_prefix="trustpilot_partial"):
    """Save partial results during scraping"""
    df = pd.DataFrame(results)
    filename = f"{filename_prefix}_{len(results)}_entries.csv"
    df.to_csv(filename, index=False)
    return filename

def find_website_in_source(soup, company_name):
    """
    Find website URL in entire page source using smart pattern matching
    """
    # Get all links in the page
    all_links = soup.find_all('a', href=True)
    
    # Common TLDs to look for
    tlds = ['.com', '.fr', '.net', '.org', '.co.uk', '.de', '.it', '.es', '.be', '.ch']
    
    # Clean company name for matching
    if company_name:
        clean_company = re.sub(r'[^a-zA-Z0-9]', '', company_name.lower())
        company_words = company_name.lower().split()
    else:
        clean_company = ""
        company_words = []
    
    for link in all_links:
        href = link.get('href', '')
        link_text = link.get_text(strip=True)
        
        # Skip trustpilot URLs
        if 'trustpilot' in href.lower():
            continue
            
        # Check if it's an external URL with common TLD
        if href.startswith('http'):
            # Parse domain from URL
            try:
                parsed = urlparse(href)
                domain = parsed.netloc.lower()
                
                # Check if domain contains TLD
                has_tld = any(tld in domain for tld in tlds)
                if not has_tld:
                    continue
                
                # Method 1: Check if company name is in domain
                if clean_company and clean_company in domain.replace('-', '').replace('.', ''):
                    clean_domain = domain.replace('www.', '')
                    return clean_domain
                
                # Method 2: Check if any company word is in domain
                for word in company_words:
                    if len(word) > 2 and word in domain:
                        clean_domain = domain.replace('www.', '')
                        return clean_domain
                
                # Method 3: If link text is generic (like "Visiter le site web"), return domain
                generic_texts = ['visiter le site web', 'visit website', 'website', 'site web', 'voir le site']
                if link_text.lower() in generic_texts:
                    clean_domain = domain.replace('www.', '')
                    return clean_domain
                
                # Method 4: Check if link text looks like a website
                if link_text and any(tld in link_text.lower() for tld in tlds):
                    # Avoid false positives (emails, long texts)
                    if '@' not in link_text and len(link_text) < 50 and ' ' not in link_text.strip():
                        return link_text
                        
            except Exception as e:
                continue
    
    return None

def safe_get_text(soup, selectors):
    """Essaie plusieurs selecteurs, retourne le texte ou ''"""
    for sel in selectors:
        if len(sel) == 2:
            tag = soup.find(sel[0], sel[1])
        else:
            tag = soup.find(*sel)
        if tag and tag.get_text(strip=True):
            return tag.get_text(strip=True)
    return ""

def extract_company_info(soup, lien):
    """
    Extract company information using robust methods
    """
    company_data = {
        'nom': '',
        'lien_trustpilot': lien,
        'nombre_avis': '',
        'rating': '',
        'adresse': '',
        'email': '',
        'website': '',
        'phone': '',
        'description': ''
    }
    
    # Extract company name - multiple patterns
    company_data['nom'] = safe_get_text(soup, [
        ("span", {"class": "typography_display-s__pKPhT typography_appearance-default__t8iAq title_displayName__9lGaz"}),
        ("span", {"class": "typography_display-s__pKPhT"}),
        ("p", {"class": "CDS_Typography_appearance-default__bedfe1 CDS_Typography_heading-s__bedfe1 styles_mobileDisplayName__eFqHW"}),
        ("h1", {}),
    ])
    
    # Extract reviews count - multiple patterns
    reviews_text = safe_get_text(soup, [
        ("span", {"class": "typography_body-l__v5JLj typography_appearance-default__t8iAq styles_reviewsAndRating__OIRXy"}),
        ("span", {"class": "styles_reviewsAndRating__OIRXy"}),
        ("span", {"class": re.compile(r".*reviewsAndRating.*")}),
    ])
    
    if reviews_text:
        # Extract all numbers and join them
        numbers = re.findall(r'\d+', reviews_text)
        if numbers:
            reviews_str = ''.join(numbers)
            company_data['nombre_avis'] = reviews_str
    
    # Extract rating
    rating_elem = soup.find('div', class_=re.compile(r'.*rating.*|.*score.*'))
    if rating_elem:
        rating_text = rating_elem.get_text(strip=True)
        rating_match = re.search(r'(\d+[.,]\d+)', rating_text)
        if rating_match:
            company_data['rating'] = rating_match.group(1).replace(',', '.')
    
    # Extract contact information from contact items
    contact_items = soup.find_all('li', class_='styles_itemRow__74s4a')
    
    for item in contact_items:
        # Check for email
        email_link = item.find('a', href=lambda x: x and x.startswith('mailto:'))
        if email_link and not company_data['email']:
            company_data['email'] = email_link.get_text(strip=True)
        
        # Check for phone
        phone_link = item.find('a', href=lambda x: x and x.startswith('tel:'))
        if phone_link and not company_data['phone']:
            company_data['phone'] = phone_link.get_text(strip=True)
        
        # Check for website - search for any external link
        all_links = item.find_all('a', href=True)
        for link in all_links:
            href = link.get('href', '')
            if href.startswith('http') and 'trustpilot' not in href.lower() and not company_data['website']:
                website_text = link.get_text(strip=True)
                company_data['website'] = website_text
                break
        
        # Check for location (look for location icon + text)
        location_svg = item.find('svg')
        if location_svg and not company_data['adresse']:
            svg_content = str(location_svg)
            # Check if it's a location icon
            if 'M3.404 1.904A6.5 6.5' in svg_content:
                location_p = item.find('p')
                if location_p:
                    company_data['adresse'] = location_p.get_text(strip=True)
    
    # Fallback methods for missing data
    
    # Fallback for email (search in entire page)
    if not company_data['email']:
        text = soup.get_text()
        email_matches = re.findall(r'[\w\.-]+@[\w\.-]+\.\w+', text)
        if email_matches:
            company_data['email'] = email_matches[0]
    
    # Fallback for website (search entire page)
    if not company_data['website']:
        # Look for visit website button
        btn = soup.find("a", attrs={"data-visit-website-button-link": True})
        if btn and btn.has_attr("href"):
            company_data['website'] = btn["href"]
        else:
            # Use advanced website finding
            website = find_website_in_source(soup, company_data['nom'])
            if website:
                company_data['website'] = website
    
    # Fallback for location (search in page text)
    if not company_data['adresse']:
        for adr_selector in [
            ('p', {'class': 'typography_body-l__v5JLj typography_appearance-default__t8iAq'}),
        ]:
            adr_tag = soup.find(*adr_selector)
            if adr_tag and any(country in adr_tag.text for country in ['France', 'Belgium', 'Switzerland', 'Canada']):
                company_data['adresse'] = adr_tag.get_text(strip=True)
                break
    
    # Extract description
    desc_section = soup.find("div", attrs={"data-business-unit-about-section": True})
    if desc_section:
        desc_tag = desc_section.find("p", attrs={"data-relevant-review-text-typography": True})
        if desc_tag:
            company_data['description'] = desc_tag.get_text(strip=True)
    
    return company_data

# ----------- SCRAP DE TOUTES LES PAGES DE LISTE ----------- #
liens_uniques = set()

for page in range(1, 41):  # 1 à 41 inclus
    url = CAT_URL if page == 1 else f"{CAT_URL}?page={page}"
    print(f"Scrapping page {page} : {url}")
    
    try:
        # Use random headers for list pages too
        headers = get_random_headers()
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.content, "html.parser")

        for card in soup.find_all("a", href=True):
            href = card.get("href")
            if href and href.startswith("/review/"):
                lien = BASE_URL + href
                liens_uniques.add(lien)
    except Exception as e:
        print(f"  Erreur lors du scraping de la page {page}: {e}")
    
    time.sleep(1)

liens_uniques = list(liens_uniques)
print(f"Total liens uniques trouvés : {len(liens_uniques)}")

# Exit early if no links found
if len(liens_uniques) == 0:
    print("❌ Aucun lien trouvé. Vérifiez la connexion ou les sélecteurs CSS.")
    print("💡 Suggestions:")
    print("   - Vérifiez que le site est accessible")
    print("   - Les sélecteurs CSS ont peut-être changé")
    print("   - Trustpilot bloque peut-être votre IP")
    exit(1)

# ----------- SCRAPING DES PAGES INDIVIDUELLES ----------- #
results = []
errors = []
save_interval = 25  # Save every 25 entries

for i, lien in enumerate(liens_uniques):
    print(f"[{i+1}/{len(liens_uniques)}] Scrapping {lien}")
    
    try:
        # Use retry mechanism
        res = make_request_with_retry(lien, max_retries=3, base_delay=2)
        soup_b = BeautifulSoup(res.content, "html.parser")
        
        # Extract company info using robust method
        company_info = extract_company_info(soup_b, lien)
        results.append(company_info)
        
        # Debug info
        if not any(company_info.values()):
            print(f"  ⚠️  Aucune donnée extraite pour {lien}")
            errors.append(f"No data extracted: {lien}")
        else:
            filled_fields = sum(1 for v in company_info.values() if v)
            print(f"  ✅ {filled_fields}/9 champs remplis")
        
        # Save partial results periodically
        if (i + 1) % save_interval == 0:
            partial_file = save_partial_results(results)
            print(f"  💾 Sauvegarde partielle: {partial_file}")
        
    except Exception as e:
        print(f"  ❌ Erreur définitive : {e}")
        errors.append(f"Error loading {lien}: {e}")
        # Add empty entry to maintain structure
        results.append({
            'nom': '',
            'lien_trustpilot': lien,
            'nombre_avis': '',
            'rating': '',
            'adresse': '',
            'email': '',
            'website': '',
            'phone': '',
            'description': ''
        })
    
    # Progressive delay increase if too many 403 errors
    if len([e for e in errors[-10:] if '403' in str(e)]) > 5:
        print(f"  🛑 Trop d'erreurs 403 récentes, pause longue...")
        time.sleep(30)
    else:
        # Random delay between requests
        delay = random.uniform(1.5, 3.0)
        time.sleep(delay)

# ----------- EXPORT FINAL ----------- #
df = pd.DataFrame(results)

print("\n" + "="*50)
print("RÉSUMÉ DU SCRAPING")
print("="*50)
print(f"Total liens traités: {len(liens_uniques)}")
print(f"Résultats obtenus: {len(results)}")
print(f"Erreurs rencontrées: {len(errors)}")

# Count different error types
error_403 = len([e for e in errors if '403' in str(e)])
error_network = len([e for e in errors if 'Error loading' in str(e)])
error_no_data = len([e for e in errors if 'No data extracted' in str(e)])

print(f"  - Erreurs 403 (Forbidden): {error_403}")
print(f"  - Erreurs réseau: {error_network}")
print(f"  - Aucune donnée extraite: {error_no_data}")

# Statistics on filled fields - Fix division by zero
filled_stats = {}
for field in ['nom', 'nombre_avis', 'rating', 'adresse', 'email', 'website', 'phone', 'description']:
    filled_count = sum(1 for row in results if row[field])
    filled_stats[field] = filled_count
    if len(results) > 0:
        percentage = filled_count/len(results)*100
        print(f"{field}: {filled_count}/{len(results)} ({percentage:.1f}%)")
    else:
        print(f"{field}: 0/0 (0.0%)")

if len(results) > 0:
    print("\n" + "="*50)
    print(df.head(10))

    # Save final results with timestamp
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    final_filename = f"trustpilot_bijouteries_final_{timestamp}.csv"
    df.to_csv(final_filename, index=False)
    print(f"\nDonnées finales sauvegardées dans '{final_filename}'")

    # Success rate analysis
    success_rate = (len(results) - error_no_data) / len(results) * 100
    print(f"\nTaux de succès global: {success_rate:.1f}%")
else:
    print("\n❌ Aucun résultat à sauvegarder.")

# Save errors log if any
if errors:
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    error_filename = f"trustpilot_scraping_errors_{timestamp}.txt"
    with open(error_filename, "w", encoding='utf-8') as f:
        f.write(f"Rapport d'erreurs - {datetime.now()}\n")
        f.write("="*50 + "\n\n")
        for error in errors:
            f.write(error + "\n")
    print(f"Log des erreurs sauvegardé dans '{error_filename}'")

# Recommendations
print("\n" + "="*50)
print("RECOMMANDATIONS")
print("="*50)

if len(liens_uniques) == 0:
    print("🔍 PROBLÈME DE COLLECTE DES LIENS:")
    print("   - Vérifiez votre connexion Internet")
    print("   - Trustpilot a peut-être changé sa structure")
    print("   - Votre IP est peut-être bloquée")
    print("   - Essayez avec un VPN")
elif error_403 > 50:
    print("⚠️  Beaucoup d'erreurs 403 détectées")
    print("   - Considérez utiliser un proxy rotatif")
    print("   - Augmentez les délais entre requêtes")
    print("   - Lancez le script à différents moments")

if len(results) > 0:
    success_rate = (len(results) - error_no_data) / len(results) * 100
    if success_rate > 80:
        print("✅ Excellent taux de succès!")
    elif success_rate > 60:
        print("👍 Bon taux de succès")
    else:
        print("⚠️  Taux de succès faible - optimisations nécessaires")
else:
    print("❌ Aucun résultat obtenu - script à déboguer")