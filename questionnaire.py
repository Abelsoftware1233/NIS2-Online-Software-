# 40 vragen gebaseerd op NIS2-maatregelen, verdeeld over 10 categorieën
# Elke vraag: {id, category, question, description}
# Antwoorden op schaal 1-5: 1=Helemaal niet, 5=Helemaal wel

QUESTIONS = [
    # Categorie 1: Risicomanagement (4 vragen)
    {
        'id': 'RM1',
        'category': 'Risicomanagement',
        'question': 'Heeft uw organisatie een actueel risicoregister waarin cybersecurity-risico\'s zijn geïdentificeerd?',
        'description': 'Een risicoregister helpt om inzicht te krijgen in de belangrijkste digitale risico\'s voor uw organisatie.'
    },
    {
        'id': 'RM2',
        'category': 'Risicomanagement',
        'question': 'Worden cybersecurity-risico\'s periodiek (minimaal jaarlijks) geëvalueerd en bijgewerkt?',
        'description': 'Risico\'s veranderen voortdurend, daarom is periodieke evaluatie essentieel.'
    },
    {
        'id': 'RM3',
        'category': 'Risicomanagement',
        'question': 'Worden risico\'s uit de toeleveringsketen (leveranciers, partners) meegenomen in het risicomanagement?',
        'description': 'NIS2 vereist dat ook risico\'s van derden worden beheerd.'
    },
    {
        'id': 'RM4',
        'category': 'Risicomanagement',
        'question': 'Worden risicoanalyses uitgevoerd bij nieuwe projecten of grote veranderingen in de IT-omgeving?',
        'description': 'Nieuwe technologieën brengen nieuwe risico\'s met zich mee.'
    },
    
    # Categorie 2: Securitybeleid (4 vragen)
    {
        'id': 'SB1',
        'category': 'Securitybeleid',
        'question': 'Is er een formeel, vastgesteld informatiebeveiligingsbeleid binnen uw organisatie?',
        'description': 'Een duidelijk beleid vormt de basis voor alle security-maatregelen.'
    },
    {
        'id': 'SB2',
        'category': 'Securitybeleid',
        'question': 'Zijn de security-regels en -richtlijnen voor alle medewerkers beschikbaar en begrijpelijk?',
        'description': 'Beleid is alleen effectief als iedereen het kent en begrijpt.'
    },
    {
        'id': 'SB3',
        'category': 'Securitybeleid',
        'question': 'Wordt het securitybeleid minimaal jaarlijks herzien en aangepast aan nieuwe dreigingen?',
        'description': 'Het dreigingslandschap verandert snel, beleid moet mee-evolueren.'
    },
    {
        'id': 'SB4',
        'category': 'Securitybeleid',
        'question': 'Zijn er duidelijke procedures voor het melden van security-incidenten?',
        'description': 'Snelle melding is cruciaal voor effectieve incidentrespons.'
    },
    
    # Categorie 3: Toegangsbeheer (4 vragen)
    {
        'id': 'TB1',
        'category': 'Toegangsbeheer',
        'question': 'Wordt het principe van "minimale rechten" toegepast (medewerkers krijgen alleen toegang tot wat ze nodig hebben)?',
        'description': 'Minimale rechten beperken de schade bij een inbreuk.'
    },
    {
        'id': 'TB2',
        'category': 'Toegangsbeheer',
        'question': 'Is er een beveiligde procedure voor het in- en uitschrijven van medewerkers?',
        'description': 'Toegang moet direct worden ingetrokken bij uitdiensttreding.'
    },
    {
        'id': 'TB3',
        'category': 'Toegangsbeheer',
        'question': 'Wordt tweefactorauthenticatie (2FA) gebruikt voor toegang tot kritieke systemen?',
        'description': '2FA biedt een extra beveiligingslaag tegen gestolen wachtwoorden.'
    },
    {
        'id': 'TB4',
        'category': 'Toegangsbeheer',
        'question': 'Worden wachtwoorden veilig opgeslagen en worden sterke wachtwoorden afgedwongen?',
        'description': 'Veilige wachtwoordopslag is essentieel voor de beveiliging.'
    },
    
    # Categorie 4: Bewustwording & Training (4 vragen)
    {
        'id': 'BT1',
        'category': 'Bewustwording & Training',
        'question': 'Volgen alle medewerkers een basis cybersecurity-awareness training?',
        'description': 'Medewerkers zijn de eerste verdedigingslinie tegen cyberaanvallen.'
    },
    {
        'id': 'BT2',
        'category': 'Bewustwording & Training',
        'question': 'Wordt er regelmatig (minimaal jaarlijks) phishing-simulatie getraind?',
        'description': 'Phishing blijft een van de grootste bedreigingen.'
    },
    {
        'id': 'BT3',
        'category': 'Bewustwording & Training',
        'question': 'Krijgen IT-medewerkers specialistische security-training?',
        'description': 'IT-medewerkers hebben extra kennis nodig om systemen te beveiligen.'
    },
    {
        'id': 'BT4',
        'category': 'Bewustwording & Training',
        'question': 'Wordt de effectiviteit van security-training gemeten en geëvalueerd?',
        'description': 'Meten is weten: evalueer of training daadwerkelijk bijdraagt aan veiliger gedrag.'
    },
    
    # Categorie 5: Incidentrespons (4 vragen)
    {
        'id': 'IR1',
        'category': 'Incidentrespons',
        'question': 'Is er een actueel incidentresponsplan dat de stappen bij een cyberincident beschrijft?',
        'description': 'Een plan zorgt voor gestructureerd en snel handelen bij incidenten.'
    },
    {
        'id': 'IR2',
        'category': 'Incidentrespons',
        'question': 'Wordt het incidentresponsplan regelmatig geoefend (bijv. via een tafeloefening)?',
        'description': 'Oefening baart kunst: test het plan in een veilige omgeving.'
    },
    {
        'id': 'IR3',
        'category': 'Incidentrespons',
        'question': 'Zijn er contactpersonen en communicatiekanalen vastgelegd voor incidenten?',
        'description': 'Snel schakelen is essentieel; weet wie je moet bellen.'
    },
    {
        'id': 'IR4',
        'category': 'Incidentrespons',
        'question': 'Zijn er procedures om na een incident te leren en verbeteringen door te voeren?',
        'description': 'Leren van incidenten voorkomt herhaling.'
    },
    
    # Categorie 6: Business Continuity (4 vragen)
    {
        'id': 'BC1',
        'category': 'Business Continuity',
        'question': 'Is er een business continuity plan (BCP) voor het geval kritieke systemen uitvallen?',
        'description': 'BCP zorgt dat de organisatie kan blijven draaien bij uitval.'
    },
    {
        'id': 'BC2',
        'category': 'Business Continuity',
        'question': 'Worden er regelmatig backups gemaakt van kritieke data en systemen?',
        'description': 'Backups zijn de laatste redding bij ransomware of dataverlies.'
    },
    {
        'id': 'BC3',
        'category': 'Business Continuity',
        'question': 'Worden backups periodiek getest op herstelbaarheid?',
        'description': 'Een backup die niet werkt is geen backup. Test regelmatig of herstellen lukt.'
    },
    {
        'id': 'BC4',
        'category': 'Business Continuity',
        'question': 'Zijn kritieke systemen redundant uitgevoerd (failover) om uitval te voorkomen?',
        'description': 'Redundantie minimaliseert downtime bij storingen.'
    },
    
    # Categorie 7: Patchmanagement (4 vragen)
    {
        'id': 'PM1',
        'category': 'Patchmanagement',
        'question': 'Is er een gestructureerd proces voor het beheren van security-updates?',
        'description': 'Ongepatchte systemen zijn een van de grootste kwetsbaarheden.'
    },
    {
        'id': 'PM2',
        'category': 'Patchmanagement',
        'question': 'Worden kritieke security-patches binnen 7 dagen geïnstalleerd?',
        'description': 'Snel patchen is essentieel voor kritieke kwetsbaarheden.'
    },
    {
        'id': 'PM3',
        'category': 'Patchmanagement',
        'question': 'Worden systemen regelmatig gescand op ontbrekende patches?',
        'description': 'Proactief scannen helpt om kwetsbaarheden op te sporen.'
    },
    {
        'id': 'PM4',
        'category': 'Patchmanagement',
        'question': 'Is er een procedure voor het testen van patches voordat ze worden uitgerold?',
        'description': 'Testen voorkomt dat patches problemen veroorzaken in de productieomgeving.'
    },
    
    # Categorie 8: Logging & Monitoring (4 vragen)
    {
        'id': 'LM1',
        'category': 'Logging & Monitoring',
        'question': 'Worden er logs bijgehouden van alle kritieke systemen?',
        'description': 'Logs zijn essentieel voor het detecteren en onderzoeken van incidenten.'
    },
    {
        'id': 'LM2',
        'category': 'Logging & Monitoring',
        'question': 'Worden logs centraal verzameld en geanalyseerd?',
        'description': 'Centrale loganalyse maakt correlatie en detectie mogelijk.'
    },
    {
        'id': 'LM3',
        'category': 'Logging & Monitoring',
        'question': 'Worden logs minimaal 6 maanden bewaard voor forensisch onderzoek?',
        'description': 'Langdurige opslag is nodig voor onderzoek en wettelijke vereisten.'
    },
    {
        'id': 'LM4',
        'category': 'Logging & Monitoring',
        'question': 'Worden logs actief gemonitord op verdachte activiteiten (24/7 of tijdens kantooruren)?',
        'description': 'Actieve monitoring maakt snelle detectie van aanvallen mogelijk.'
    },
    
    # Categorie 9: Cryptografie (4 vragen)
    {
        'id': 'CR1',
        'category': 'Cryptografie',
        'question': 'Wordt data in rust (opgeslagen data) versleuteld, zoals harde schijven en databases?',
        'description': 'Versleuteling beschermt data bij diefstal of verlies van hardware.'
    },
    {
        'id': 'CR2',
        'category': 'Cryptografie',
        'question': 'Wordt data in transit (tijdens verzending) versleuteld met moderne protocollen zoals TLS?',
        'description': 'Versleuteling tijdens transport beschermt tegen afluisteren.'
    },
    {
        'id': 'CR3',
        'category': 'Cryptografie',
        'question': 'Worden sterke encryptie-algoritmen gebruikt (AES-256, TLS 1.3, etc.)?',
        'description': 'Verouderde encryptie is makkelijk te kraken. Gebruik moderne standaarden.'
    },
    {
        'id': 'CR4',
        'category': 'Cryptografie',
        'question': 'Worden wachtwoorden en sleutels veilig opgeslagen in een password manager of HSM?',
        'description': 'Veilige opslag voorkomt dat sleutels in verkeerde handen vallen.'
    },
    
    # Categorie 10: Compliance & Governance (4 vragen)
    {
        'id': 'CG1',
        'category': 'Compliance & Governance',
        'question': 'Worden wettelijke en regelgevende vereisten (zoals AVG) nageleefd?',
        'description': 'Naleving van wet- en regelgeving is verplicht en voorkomt boetes.'
    },
    {
        'id': 'CG2',
        'category': 'Compliance & Governance',
        'question': 'Is er een functionaris gegevensbescherming (FG) of security officer aangesteld?',
        'description': 'Een verantwoordelijke zorgt voor continuïteit en focus op security.'
    },
    {
        'id': 'CG3',
        'category': 'Compliance & Governance',
        'question': 'Worden derde partijen en leveranciers beoordeeld op hun security-maatregelen?',
        'description': 'Leveranciers kunnen een zwakke schakel zijn; beoordeel hun security.'
    },
    {
        'id': 'CG4',
        'category': 'Compliance & Governance',
        'question': 'Is security onderdeel van de governance-structuur (bijv. in het bestuursverslag)?',
        'description': 'Security moet bestuurlijke aandacht krijgen op het hoogste niveau.'
    }
]

def get_all_questions():
    """Haal alle vragen op"""
    return QUESTIONS

def get_questions_by_category(category):
    """Haal vragen op per categorie"""
    return [q for q in QUESTIONS if q['category'] == category]

def get_categories():
    """Haal alle unieke categorieën op"""
    categories = list(set(q['category'] for q in QUESTIONS))
    # Sorteer in de juiste volgorde
    order = [
        'Risicomanagement',
        'Securitybeleid',
        'Toegangsbeheer',
        'Bewustwording & Training',
        'Incidentrespons',
        'Business Continuity',
        'Patchmanagement',
        'Logging & Monitoring',
        'Cryptografie',
        'Compliance & Governance'
    ]
    return [c for c in order if c in categories]

def calculate_scores(answers):
    """Bereken scores per categorie en totaal"""
    category_scores = {}
    category_max = {}
    category_counts = {}
    
    # Agregeer per categorie
    for answer in answers:
        category = answer['category']
        score = answer['answer']
        
        if category not in category_scores:
            category_scores[category] = 0
            category_max[category] = 0
            category_counts[category] = 0
        
        category_scores[category] += score
        category_max[category] += 5  # Max score per vraag is 5
        category_counts[category] += 1
    
    # Bereken percentages
    result = {
        'categories': {},
        'total_score': 0,
        'max_score': 0,
        'percentage': 0,
        'category_count': len(category_scores)
    }
    
    total_score = 0
    total_max = 0
    
    for category in category_scores:
        score = category_scores[category]
        max_score = category_max[category]
        percentage = round((score / max_score) * 100)
        
        result['categories'][category] = {
            'score': score,
            'max_score': max_score,
            'percentage': percentage,
            'question_count': category_counts[category]
        }
        
        total_score += score
        total_max += max_score
    
    result['total_score'] = total_score
    result['max_score'] = total_max
    result['percentage'] = round((total_score / total_max) * 100) if total_max > 0 else 0
    
    return result
