from flask import Flask, request, jsonify, send_file
import json
import os
import tempfile
from datetime import datetime
import traceback

# Importeer de modules
from .database import (
    init_db, create_user, authenticate_user, create_audit_session,
    get_session_by_token, save_questionnaire_answer, get_questionnaire_answers,
    save_scan_result, get_scan_result, save_audit_result, get_audit_result,
    complete_audit_session, get_user_sessions
)
from .questionnaire import get_all_questions, get_categories, calculate_scores
from .scanner import scan_domain
from .advies import generate_advice
from .pdf_report import create_pdf_report

app = Flask(__name__)

# CORS headers - handmatig zonder dependencies
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With')
    response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
    return response

# Initialiseer de database
init_db()

# ==================== ROUTES ====================

@app.route('/', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'ok',
        'message': 'NIS2 Audit Tool API is running',
        'version': '1.0.0',
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/register', methods=['POST'])
def register():
    """Registreer een nieuwe gebruiker"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        bedrijfsnaam = data.get('bedrijfsnaam')
        
        if not email or not password:
            return jsonify({'error': 'Email en wachtwoord zijn verplicht'}), 400
        
        result = create_user(email, password, bedrijfsnaam)
        
        if result['success']:
            return jsonify({'message': 'Gebruiker succesvol geregistreerd', 'user_id': result['user_id']}), 201
        else:
            return jsonify({'error': result['error']}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/login', methods=['POST'])
def login():
    """Login een gebruiker en maak een sessie aan"""
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'error': 'Email en wachtwoord zijn verplicht'}), 400
        
        auth_result = authenticate_user(email, password)
        
        if auth_result['success']:
            session = create_audit_session(auth_result['user_id'])
            return jsonify({
                'message': 'Login succesvol',
                'token': session['token'],
                'session_id': session['session_id']
            }), 200
        else:
            return jsonify({'error': auth_result['error']}), 401
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/questions', methods=['GET'])
def get_questions():
    """Haal alle vragen op"""
    try:
        questions = get_all_questions()
        categories = get_categories()
        return jsonify({
            'questions': questions,
            'categories': categories,
            'total': len(questions)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/answer', methods=['POST'])
def save_answer():
    """Sla een antwoord op"""
    try:
        data = request.get_json()
        token = data.get('token')
        question_id = data.get('question_id')
        answer = data.get('answer')
        category = data.get('category')
        
        if not all([token, question_id, answer, category]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Valideer antwoord (1-5)
        try:
            answer = int(answer)
            if answer < 1 or answer > 5:
                return jsonify({'error': 'Answer must be between 1 and 5'}), 400
        except ValueError:
            return jsonify({'error': 'Answer must be an integer'}), 400
        
        # Check sessie
        session = get_session_by_token(token)
        if not session:
            return jsonify({'error': 'Invalid session'}), 401
        
        # Sla antwoord op
        save_questionnaire_answer(session['id'], question_id, answer, category)
        
        return jsonify({'message': 'Answer saved successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/answers', methods=['GET'])
def get_answers():
    """Haal alle antwoorden voor een sessie op"""
    try:
        token = request.args.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        session = get_session_by_token(token)
        if not session:
            return jsonify({'error': 'Invalid session'}), 401
        
        answers = get_questionnaire_answers(session['id'])
        
        return jsonify({
            'answers': answers,
            'count': len(answers)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/scan', methods=['POST'])
def run_scan():
    """Voer een technische scan uit"""
    try:
        data = request.get_json()
        token = data.get('token')
        domain = data.get('domain', '').strip()
        
        if not token or not domain:
            return jsonify({'error': 'Token en domein zijn verplicht'}), 400
        
        # Validate domain format
        if not domain or len(domain) < 2:
            return jsonify({'error': 'Ongeldig domein'}), 400
        
        # Check session
        session = get_session_by_token(token)
        if not session:
            return jsonify({'error': 'Invalid session'}), 401
        
        # Run scan
        scan_result = scan_domain(domain)
        
        if scan_result.get('success'):
            # Save scan result
            save_scan_result(session['id'], domain, scan_result['results'])
            return jsonify({
                'message': 'Scan completed',
                'results': scan_result['results']
            }), 200
        else:
            return jsonify({'error': scan_result.get('error', 'Scan failed')}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/complete', methods=['POST'])
def complete_audit():
    """Voltooi de audit en genereer score en advies"""
    try:
        data = request.get_json()
        token = data.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        session = get_session_by_token(token)
        if not session:
            return jsonify({'error': 'Invalid session'}), 401
        
        # Haal antwoorden op
        answers = get_questionnaire_answers(session['id'])
        if len(answers) < 40:
            return jsonify({
                'error': f'Niet alle vragen zijn beantwoord ({len(answers)}/40)'
            }), 400
        
        # Bereken scores
        scores = calculate_scores(answers)
        
        # Genereer advies
        advice = generate_advice(scores)
        
        # Sla resultaten op (inclusief volledige categorie-breakdown in 'scores')
        save_audit_result(
            session['id'],
            scores['total_score'],
            scores['max_score'],
            scores['percentage'],
            advice,
            scores
        )
        
        # Markeer sessie als voltooid
        complete_audit_session(session['id'])
        
        return jsonify({
            'message': 'Audit completed',
            'scores': scores,
            'advice': advice
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/report', methods=['GET'])
def generate_report():
    """Genereer een PDF rapport"""
    try:
        token = request.args.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        session = get_session_by_token(token)
        if not session:
            return jsonify({'error': 'Invalid session'}), 401
        
        # Haal alle data op
        answers = get_questionnaire_answers(session['id'])
        scan_data = get_scan_result(session['id'])
        audit_data = get_audit_result(session['id'])
        questions = get_all_questions()
        
        if not audit_data:
            return jsonify({'error': 'Audit not completed yet. Run /api/complete first.'}), 400
        
        # Bouw rapport data
        # get_audit_result() geeft altijd een bruikbare 'scores' dict terug
        # (met categorie-breakdown wanneer beschikbaar, anders een fallback).
        report_data = {
            'session_id': session['id'],
            'questions': questions,
            'answers': answers,
            'scores': audit_data.get('scores', {}),
            'scan_results': scan_data.get('scan_data', {}) if scan_data else {},
            'advice': audit_data.get('advice', [])
        }
        
        # Genereer PDF (absoluut pad in de systeem-tempdir, zodat dit
        # onafhankelijk is van de working directory waarin Flask draait)
        filename = os.path.join(
            tempfile.gettempdir(),
            f"nis2_report_{session['id']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        )
        create_pdf_report(report_data, filename)
        
        # Stuur bestand en ruim het tijdelijke bestand daarna op
        response = send_file(filename, as_attachment=True, download_name='nis2_audit_report.pdf')
        
        @response.call_on_close
        def _cleanup():
            try:
                os.remove(filename)
            except OSError:
                pass
        
        return response
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    """Haal alle sessies van een gebruiker op"""
    try:
        token = request.args.get('token')
        
        if not token:
            return jsonify({'error': 'Token is required'}), 400
        
        session = get_session_by_token(token)
        if not session:
            return jsonify({'error': 'Invalid session'}), 401
        
        sessions = get_user_sessions(session['user_id'])
        
        return jsonify({
            'sessions': sessions,
            'count': len(sessions)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5077, debug=True)
