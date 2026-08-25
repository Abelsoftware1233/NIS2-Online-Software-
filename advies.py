# Adviesgenerator op basis van scores - Jip-en-Janneke taal

def generate_advice(scores):
    """Genereer concreet advies op basis van de scores per categorie"""
    advice = []
    
    # Algemene status bepaling
    overall_percentage = scores.get('percentage', 0)
    
    # Algemene inleiding
    if overall_percentage >= 80:
        advice.append({
            'priority': 'groen',
            'title': 'Geweldig! Je cybersecurity is op orde!',
            'action': 'Je hebt een sterke cybersecurity-huishouding. Blijf vooral doorgaan met onderhoud en verbetering. Periodiek blijven evalueren is belangrijk om op niveau te blijven.'
        })
    elif overall_percentage >= 60:
        advice.append({
            'priority': 'geel',
            'title': 'Goed bezig, maar er is nog werk aan de winkel!',
            'action': 'Je hebt een solide basis, maar sommige onderdelen kunnen beter. Pak de categorieën met de laagste scores aan als eerste prioriteit.'
        })
    else:
        advice.append({
            'priority': 'rood',
            'title': 'Tijd om actie te ondernemen!',
            'action': 'Er zijn serieuze verbeteringen nodig om aan de NIS2-vereisten te voldoen. Begin met de belangrijkste risico\'s en werk stap voor stap.'
        })
    
    # Specifiek advies per categorie
    for category, data in scores.get('categories', {}).items():
        percentage = data['percentage']
        
        if percentage < 40:
            advice.append({
                'priority': 'rood',
                'title': f'🚨 {category}: Direct actie nodig!',
                'action': get_category_advice(category, percentage, 'rood')
            })
        elif percentage < 70:
            advice.append({
                'priority': 'geel',
                'title': f'⚠️ {category}: Verbeterpunten gesignaleerd',
                'action': get_category_advice(category, percentage, 'geel')
            })
        else:
            advice.append({
                'priority': 'groen',
                'title': f'✅ {category}: Op orde, onderhoud blijft belangrijk!',
                'action': get_category_advice(category, percentage, 'groen')
            })
    
    # Concretiseer acties
    concrete_actions = get_concrete_actions(scores)
    if concrete_actions:
        advice.append({
            'priority': 'blauw',
            'title': 'Concrete acties voor de korte termijn',
            'action': concrete_actions
        })
    
    return advice

def get_category_advice(category, percentage, level):
    """Geef specifiek advies per categorie"""
    advice_map = {
        'Risicomanagement': {
            'rood': 'Start met een basis risico-inventarisatie. Maak een lijst van alle digitale systemen en bedreigingen. Begin klein, maar begin vandaag nog!',
            'geel': 'Breid je risicomanagement uit. Evalueer de impact van risico\'s op je bedrijfsvoering. Betrek ook leveranciers en partners bij de risicoanalyse.',
            'groen': 'Blijf je risicoregister up-to-date houden. Organiseer een jaarlijkse risicosessie met het management om nieuwe dreigingen te bespreken.'
        },
        'Securitybeleid': {
            'rood': 'Stel een eenvoudig securitybeleid op met duidelijke regels voor alle medewerkers. Houd het begrijpelijk en praktisch, niet te juridisch.',
            'geel': 'Herzie je huidige beleid en maak het concreter. Voeg praktische voorbeelden toe en zorg dat het voor iedereen toegankelijk is.',
            'groen': 'Zorg dat je beleid blijft leven. Plan periodieke reviews en betrek medewerkers bij de evaluatie van het beleid.'
        },
        'Toegangsbeheer': {
            'rood': 'Start met het toepassen van het principe van minimale rechten. Geef medewerkers alleen toegang tot wat ze echt nodig hebben. Begin vandaag nog met een inventarisatie.',
            'geel': 'Implementeer 2-factor authenticatie voor de meest kritieke systemen. Dit is een relatief simpele stap die veel veiligheid oplevert.',
            'groen': 'Evalueer periodiek de toegangsrechten van medewerkers en verwijder verouderde accounts. Automatiseer het in- en uitschrijfproces.'
        },
        'Bewustwording & Training': {
            'rood': 'Organiseer een basis cybersecurity-training voor alle medewerkers. Begin met de gevaren van phishing en veilig wachtwoordgebruik. Er zijn veel gratis online trainingen beschikbaar.',
            'geel': 'Voer phishing-simulaties uit om het bewustzijn te testen en te verbeteren. Bied extra training aan teams die extra risico lopen.',
            'groen': 'Organiseer jaarlijks een security-dag of -week met interactieve sessies. Blijf investeren in bewustwording, het levert altijd op!'
        },
        'Incidentrespons': {
            'rood': 'Maak een eenvoudig incidentresponsplan. Noteer wie er gebeld moet worden, wat de stappen zijn en oefen het plan met een tafeloefening.',
            'geel': 'Oefen je incidentresponsplan met een echte oefening. Test de communicatiekanalen en evalueer waar het mis gaat.',
            'groen': 'Plan jaarlijks een grote incidentrespons-oefening en evalueer grondig. Blijf het plan verbeteren op basis van lessen uit oefeningen en echte incidenten.'
        },
        'Business Continuity': {
            'rood': 'Zorg voor regelmatige backups van alle kritieke data. Bewaar backups op een aparte locatie en test of herstellen werkt. Begin vandaag nog!',
            'geel': 'Maak een business continuity plan voor de meest kritieke processen. Identificeer welke systemen echt essentieel zijn voor je bedrijfsvoering.',
            'groen': 'Test je backups en BCP plan minimaal jaarlijks. Automatiseer backups en monitoring voor extra zekerheid.'
        },
        'Patchmanagement': {
            'rood': 'Implementeer een patchbeleid: patches moeten binnen 7 dagen worden geïnstalleerd voor kritieke systemen. Start met een inventarisatie van alle systemen.',
            'geel': 'Automateer het patchen waar mogelijk. Gebruik tools voor patchmanagement om overzicht te houden over alle systemen.',
            'groen': 'Blijf je patchproces verbeteren. Overweeg maandelijkse patching-cycles en test patches in een testomgeving voor uitrol.'
        },
        'Logging & Monitoring': {
            'rood': 'Start met logging op alle kritieke systemen. Bewaar logs minimaal 6 maanden. Begin met gratis tools zoals ELK of Azure Sentinel voor monitoring.',
            'geel': 'Centraliseer je logging en begin met actieve monitoring. Stel alerts in voor verdachte activiteiten en reageer erop.',
            'groen': 'Breid monitoring uit naar 24/7 waar mogelijk. Investeer in SIEM-tools voor geavanceerde detectie en automatisering.'
        },
        'Cryptografie': {
            'rood': 'Versleutel alle data in transit met HTTPS. Zet automatische HTTPS in via Let\'s Encrypt. Het is gratis en makkelijk!',
            'geel': 'Implementeer versleuteling van data in rust (encryptie van harde schijven, databases). Gebruik AES-256 of sterker.',
            'groen': 'Evalueer je cryptografie-regime periodiek. Blijf op de hoogte van nieuwe aanbevolen standaarden en migreer waar nodig.'
        },
        'Compliance & Governance': {
            'rood': 'Maak security een vast agendapunt in het managementoverleg. Stel iemand verantwoordelijk voor security en compliance.',
            'geel': 'Voer een compliance-scan uit naar AVG en andere relevante wetgeving. Betrek juridische afdeling of externe adviseurs.',
            'groen': 'Integreer security in de governance-structuur. Laat security rapporteren in het bestuursverslag en plan jaarlijkse audits.'
        }
    }
    
    default_advice = {
        'rood': 'Deze categorie heeft significante verbetering nodig. Maak een actieplan met concrete stappen en begin met de hoogste risico\'s.',
        'geel': 'Er zijn duidelijke verbeterpunten in deze categorie. Focus op de grootste gaten en werk stap voor stap.',
        'groen': 'Deze categorie is op orde. Blijf onderhoud plegen en evalueer periodiek of het niveau behouden blijft.'
    }
    
    return advice_map.get(category, default_advice).get(level, default_advice['geel'])

def get_concrete_actions(scores):
    """Genereer een lijst van concrete, prioritaire acties"""
    actions = []
    categories = scores.get('categories', {})
    
    # Identificeer de categorieën met de laagste scores
    sorted_categories = sorted(
        categories.items(),
        key=lambda x: x[1]['percentage']
    )
    
    for category, data in sorted_categories[:5]:  # Top 5 laagste scores
        if data['percentage'] < 70:
            actions.append(f"{category} ({data['percentage']}%): {get_short_action(category)}")
    
    if not actions:
        actions.append("Alle categorieën scoren goed! Blijf vooral onderhoud plegen en blijf investeren in security-awareness.")
    
    return "\n".join(actions) if actions else "Geen urgente acties nodig, maar blijf alert!"

def get_short_action(category):
    """Geef een korte actie voor een categorie"""
    actions = {
        'Risicomanagement': 'Start een eenvoudige risico-inventarisatie',
        'Securitybeleid': 'Stel een basis securitybeleid op',
        'Toegangsbeheer': 'Implementeer minimale rechten en 2FA',
        'Bewustwording & Training': 'Organiseer een basis security-training',
        'Incidentrespons': 'Maak een incidentplan en oefen het',
        'Business Continuity': 'Zorg voor regelmatige, geteste backups',
        'Patchmanagement': 'Implementeer een gestructureerd patchproces',
        'Logging & Monitoring': 'Start met logging en basis-monitoring',
        'Cryptografie': 'Versleutel data in transit en in rust',
        'Compliance & Governance': 'Maak security onderdeel van governance'
    }
    return actions.get(category, 'Verbeter de security in deze categorie')
