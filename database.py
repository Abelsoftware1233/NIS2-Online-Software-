import sqlite3
import hashlib
import os
from datetime import datetime
import json

# Hoeveel uur een sessie-token geldig blijft
SESSION_EXPIRY_HOURS = 24

def get_db():
    """Database verbinding met row factory voor dict-achtige toegang"""
    conn = sqlite3.connect('nis2_audit.db')
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialiseer de database met alle benodigde tabellen"""
    conn = get_db()
    cursor = conn.cursor()
    
    # Gebruikers tabel
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        salt TEXT NOT NULL,
        bedrijfsnaam TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Audit sessies tabel
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        token TEXT UNIQUE NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        completed_at TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
    ''')
    
    # Vragenlijst antwoorden tabel
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS questionnaire_answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        question_id TEXT NOT NULL,
        answer INTEGER NOT NULL,  -- 1-5 score
        category TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES audit_sessions (id),
        UNIQUE(session_id, question_id)
    )
    ''')
    
    # Scan resultaten tabel
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS scan_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        target_domain TEXT NOT NULL,
        scan_data TEXT NOT NULL,  -- JSON
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES audit_sessions (id)
    )
    ''')
    
    # Audit resultaten tabel (eindscore en advies)
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS audit_results (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        session_id INTEGER NOT NULL,
        total_score INTEGER,
        max_score INTEGER,
        percentage INTEGER,
        advice TEXT,  -- JSON
        scores TEXT,  -- JSON: volledige scores-dict incl. categorie-breakdown
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (session_id) REFERENCES audit_sessions (id)
    )
    ''')
    
    # Migratie: voeg 'scores' kolom toe aan bestaande databases die 'm nog niet hebben
    cursor.execute("PRAGMA table_info(audit_results)")
    existing_columns = [row[1] for row in cursor.fetchall()]
    if 'scores' not in existing_columns:
        cursor.execute('ALTER TABLE audit_results ADD COLUMN scores TEXT')
    
    conn.commit()
    conn.close()

def hash_password(password, salt=None):
    """Hash een wachtwoord met PBKDF2"""
    if salt is None:
        salt = os.urandom(32).hex()
    password_hash = hashlib.pbkdf2_hmac(
        'sha256',
        password.encode('utf-8'),
        salt.encode('utf-8'),
        100000
    ).hex()
    return password_hash, salt

def create_user(email, password, bedrijfsnaam=None):
    """Maak een nieuwe gebruiker aan"""
    conn = get_db()
    cursor = conn.cursor()
    
    password_hash, salt = hash_password(password)
    
    try:
        cursor.execute(
            'INSERT INTO users (email, password_hash, salt, bedrijfsnaam) VALUES (?, ?, ?, ?)',
            (email, password_hash, salt, bedrijfsnaam)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()
        return {'success': True, 'user_id': user_id}
    except sqlite3.IntegrityError:
        conn.close()
        return {'success': False, 'error': 'Email already exists'}

def authenticate_user(email, password):
    """Authenticeer een gebruiker"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT id, password_hash, salt FROM users WHERE email = ?', (email,))
    user = cursor.fetchone()
    conn.close()
    
    if not user:
        return {'success': False, 'error': 'User not found'}
    
    password_hash, _ = hash_password(password, user['salt'])
    
    if password_hash == user['password_hash']:
        return {'success': True, 'user_id': user['id']}
    else:
        return {'success': False, 'error': 'Invalid password'}

def create_audit_session(user_id):
    """Maak een nieuwe audit sessie aan"""
    import uuid
    token = str(uuid.uuid4())
    
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO audit_sessions (user_id, token) VALUES (?, ?)',
        (user_id, token)
    )
    conn.commit()
    session_id = cursor.lastrowid
    conn.close()
    
    return {'session_id': session_id, 'token': token}

def get_session_by_token(token):
    """Haal een sessie op via token"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM audit_sessions WHERE token = ?', (token,))
    session = cursor.fetchone()
    conn.close()
    
    return dict(session) if session else None

def save_questionnaire_answer(session_id, question_id, answer, category):
    """Sla een vragenlijst antwoord op"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        '''INSERT OR REPLACE INTO questionnaire_answers 
           (session_id, question_id, answer, category) 
           VALUES (?, ?, ?, ?)''',
        (session_id, question_id, answer, category)
    )
    conn.commit()
    conn.close()

def get_questionnaire_answers(session_id):
    """Haal alle antwoorden voor een sessie op"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM questionnaire_answers WHERE session_id = ?',
        (session_id,)
    )
    answers = cursor.fetchall()
    conn.close()
    
    return [dict(a) for a in answers]

def save_scan_result(session_id, target_domain, scan_data):
    """Sla scan resultaten op"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'INSERT INTO scan_results (session_id, target_domain, scan_data) VALUES (?, ?, ?)',
        (session_id, target_domain, json.dumps(scan_data))
    )
    conn.commit()
    conn.close()

def get_scan_result(session_id):
    """Haal scan resultaten op"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM scan_results WHERE session_id = ? ORDER BY created_at DESC LIMIT 1',
        (session_id,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result:
        data = dict(result)
        data['scan_data'] = json.loads(data['scan_data'])
        return data
    return None

def save_audit_result(session_id, total_score, max_score, percentage, advice, scores=None):
    """Sla audit resultaten op.
    'scores' is optioneel: de volledige scores-dict (incl. categorie-breakdown)
    zoals geproduceerd door calculate_scores(). Als deze niet wordt meegegeven,
    wordt er teruggevallen op de losse total_score/max_score/percentage velden."""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        '''INSERT INTO audit_results 
           (session_id, total_score, max_score, percentage, advice, scores) 
           VALUES (?, ?, ?, ?, ?, ?)''',
        (session_id, total_score, max_score, percentage, json.dumps(advice),
         json.dumps(scores) if scores is not None else None)
    )
    conn.commit()
    conn.close()

def get_audit_result(session_id):
    """Haal audit resultaten op"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM audit_results WHERE session_id = ? ORDER BY created_at DESC LIMIT 1',
        (session_id,)
    )
    result = cursor.fetchone()
    conn.close()
    
    if result:
        data = dict(result)
        data['advice'] = json.loads(data['advice'])
        if data.get('scores'):
            data['scores'] = json.loads(data['scores'])
        else:
            # Oudere records (of records zonder scores) vallen terug op de losse velden
            data['scores'] = {
                'total_score': data.get('total_score', 0),
                'max_score': data.get('max_score', 0),
                'percentage': data.get('percentage', 0),
                'categories': {}
            }
        return data
    return None

def complete_audit_session(session_id):
    """Markeer een sessie als voltooid"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'UPDATE audit_sessions SET completed_at = CURRENT_TIMESTAMP WHERE id = ?',
        (session_id,)
    )
    conn.commit()
    conn.close()

def get_user_sessions(user_id):
    """Haal alle sessies van een gebruiker op"""
    conn = get_db()
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM audit_sessions WHERE user_id = ? ORDER BY created_at DESC',
        (user_id,)
    )
    sessions = cursor.fetchall()
    conn.close()
    
    return [dict(s) for s in sessions]

def extend_session(token):
    """Verleng de levensduur van een sessie door 'created_at' te verversen.
    Wordt gebruikt om actieve sessies niet te laten verlopen tijdens gebruik."""
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute(
        'UPDATE audit_sessions SET created_at = CURRENT_TIMESTAMP WHERE token = ?',
        (token,)
    )
    conn.commit()
    updated = cursor.rowcount
    conn.close()

    return updated > 0

def log_audit(session_id, action, details=None):
    """Simpele audit-log helper. Schrijft naar audit_results als er nog geen
    entry bestaat, anders is dit een no-op-achtige logging naar console.
    Losse audit_log tabel bestaat niet in dit schema; dit is een lichte
    logging-hook zodat andere modules 'm veilig kunnen aanroepen."""
    try:
        print(f"[AUDIT LOG] session={session_id} action={action} details={details}")
    except Exception:
        pass

def create_paid_audit(user_id, amount=None, payment_reference=None):
    """Maak een audit-sessie aan die als 'betaald' gemarkeerd is.
    Hergebruikt create_audit_session; betaalstatus wordt puur informatief
    teruggegeven omdat er nog geen aparte betaaltabel is."""
    session = create_audit_session(user_id)
    session['paid'] = True
    session['amount'] = amount
    session['payment_reference'] = payment_reference
    return session
