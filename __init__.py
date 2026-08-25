"""
NIS2 Cybersecurity Audit Tool
==============================

Een complete NIS2 audit tool voor het beoordelen van cybersecurity-compliance.

Versie: 2.0.0
Auteur: NIS2 Audit Tool Team
Licentie: MIT

Modules:
--------
- database: Database management en authenticatie
- scanner: Technische scan (DNS, poorten, SSL, headers)  
- questionnaire: 40 NIS2 vragen en scoring
- advies: Score-gebaseerd advies generator
- pdf_report: PDF rapport generator
- app: Flask web applicatie
"""

__version__ = "2.0.0"
__author__ = "NIS2 Audit Tool Team"
__license__ = "MIT"
__description__ = "Complete NIS2 cybersecurity audit tool"

# Importeer belangrijkste modules voor makkelijke toegang
from .database import (
    init_db,
    create_user,
    authenticate_user,
    create_audit_session,
    get_session_by_token,
    save_questionnaire_answer,
    get_questionnaire_answers,
    save_scan_result,
    get_scan_result,
    save_audit_result,
    get_audit_result,
    complete_audit_session,
    get_user_sessions,
    extend_session,
    log_audit,
    create_paid_audit,
    SESSION_EXPIRY_HOURS
)

from .scanner import (
    scan_domain,
    scan_domain_advanced,
    get_port_status_summary,
    COMMON_PORTS,
    PORT_SCANNER
)

from .questionnaire import (
    get_all_questions,
    get_questions_by_category,
    get_categories,
    calculate_scores,
    QUESTIONS
)

from .advies import (
    generate_advice,
    get_category_advice,
    get_concrete_actions
)

from .pdf_report import (
    create_pdf_report,
    generate_report_data,
    COLOR_NAVY,
    COLOR_CYAN,
    COLOR_VIOLET
)

# Package metadata
__all__ = [
    # Database
    'init_db',
    'create_user',
    'authenticate_user',
    'create_audit_session',
    'get_session_by_token',
    'save_questionnaire_answer',
    'get_questionnaire_answers',
    'save_scan_result',
    'get_scan_result',
    'save_audit_result',
    'get_audit_result',
    'complete_audit_session',
    'get_user_sessions',
    'extend_session',
    'log_audit',
    'create_paid_audit',
    'SESSION_EXPIRY_HOURS',
    
    # Scanner
    'scan_domain',
    'scan_domain_advanced',
    'get_port_status_summary',
    'COMMON_PORTS',
    'PORT_SCANNER',
    
    # Questionnaire
    'get_all_questions',
    'get_questions_by_category',
    'get_categories',
    'calculate_scores',
    'QUESTIONS',
    
    # Advies
    'generate_advice',
    'get_category_advice',
    'get_concrete_actions',
    
    # PDF
    'create_pdf_report',
    'generate_report_data',
    'COLOR_NAVY',
    'COLOR_CYAN',
    'COLOR_VIOLET',
    
    # Metadata
    '__version__',
    '__author__',
    '__license__',
    '__description__'
]

# Package informatie
print(f"""
╔══════════════════════════════════════════════════════════════╗
║  🛡️ NIS2 Cybersecurity Audit Tool v{__version__}                    ║
║  📦 Package geladen succesvol                                ║
║  📝 {__description__}                    ║
║  ⚖️ Licentie: {__license__}                                      ║
╚══════════════════════════════════════════════════════════════╝
""")

# Controleer of alle benodigde modules beschikbaar zijn
try:
    import flask
    import reportlab
    import sqlite3
    import socket
    import ssl
    print("✅ Alle dependencies zijn aanwezig")
except ImportError as e:
    print(f"⚠️ Waarschuwing: {e}")
    print("   Sommige functionaliteiten zijn mogelijk niet beschikbaar")

# Exporteer versie informatie
def get_version():
    """Geef de versie van de tool terug"""
    return {
        'version': __version__,
        'author': __author__,
        'license': __license__,
        'description': __description__
    }

def info():
    """Toon informatie over de tool"""
    print(f"""
    ═══════════════════════════════════════════════
    NIS2 Audit Tool - Informatie
    ═══════════════════════════════════════════════
    
    Versie:     {__version__}
    Auteur:     {__author__}
    Licentie:   {__license__}
    
    Beschikbare modules:
    - database:    Database en authenticatie
    - scanner:     Technische scans
    - questionnaire: NIS2 vragenlijst
    - advies:      Advies generator
    - pdf_report:  PDF rapportage
    - app:         Flask web interface
    
    Gebruik:
    from nis2_audit import *
    
    # Voor offline gebruik:
    from nis2_audit.offline import nis2_audit
    
    # Voor online gebruik:
    from nis2_audit.online import app_online
    """)

# Initialiseer bij import
if __name__ != "__main__":
    # Bij import wordt de database niet automatisch geïnitialiseerd
    # Dit voorkomt dat de database wordt aangemaakt bij import
    pass