#!/usr/bin/env python3
"""
NIS2 ONLINE AUDIT TOOL
Web-based versie met volledige online scanning
"""

from flask import Flask, request, jsonify, send_file, render_template_string
from flask_cors import CORS
import socket
import ssl
import subprocess
import json
from datetime import datetime
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError
import ipaddress
from concurrent.futures import ThreadPoolExecutor, as_completed
import sqlite3
import hashlib
import secrets
from functools import wraps
import os

app = Flask(__name__)
CORS(app)

# ==================== DATABASE ====================
def init_db():
    conn = sqlite3.connect('nis2_online.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS scans (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            domain TEXT NOT NULL,
            results TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    conn.commit()
    conn.close()

# ==================== SCANNER ENGINE ====================
class OnlineScanner:
    def __init__(self):
        self.open_ports = {}
        self.dns_records = {}
        self.ssl_info = {}
        self.headers = {}
        
    def resolve_domain(self, domain):
        """DNS resolutie"""
        try:
            ip = socket.gethostbyname(domain)
            return {'success': True, 'ip': ip}
        except:
            return {'success': False, 'error': 'DNS resolution failed'}
    
    def get_all_dns_records(self, domain):
        """Alle DNS records ophalen"""
        records = {'A': [], 'MX': [], 'NS': [], 'TXT': [], 'CNAME': []}
        
        # A records
        try:
            ips = socket.gethostbyname_ex(domain)[2]
            records['A'] = ips
        except:
            pass
        
        # MX records
        try:
            result = subprocess.check_output(
                ['nslookup', '-type=MX', domain],
                stderr=subprocess.STDOUT,
                text=True,
                timeout=5
            )
            for line in result.split('\n'):
                if 'mail exchanger' in line.lower():
                    parts = line.split('=')
                    if len(parts) >= 2:
                        mx = parts[-1].strip()
                        if mx and not mx.startswith('#'):
                            records['MX'].append(mx)
        except:
            pass
        
        # NS records
        try:
            result = subprocess.check_output(
                ['nslookup', '-type=NS', domain],
                stderr=subprocess.STDOUT,
                text=True,
                timeout=5
            )
            for line in result.split('\n'):
                if 'nameserver' in line.lower():
                    parts = line.split('=')
                    if len(parts) >= 2:
                        ns = parts[-1].strip()
                        if ns:
                            records['NS'].append(ns)
        except:
            pass
        
        # TXT records
        try:
            result = subprocess.check_output(
                ['nslookup', '-type=TXT', domain],
                stderr=subprocess.STDOUT,
                text=True,
                timeout=5
            )
            for line in result.split('\n'):
                if 'text =' in line.lower():
                    parts = line.split('=')
                    if len(parts) >= 2:
                        txt = parts[-1].strip().strip('"')
                        if txt:
                            records['TXT'].append(txt)
        except:
            pass
        
        return records
    
    def scan_port(self, ip, port, timeout=2):
        """Scan een poort"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex((ip, port))
            sock.close()
            return port, result == 0
        except:
            return port, False
    
    def scan_ports(self, domain, max_ports=1000):
        """Scan poorten met threading"""
        # DNS resolutie
        dns = self.resolve_domain(domain)
        if not dns['success']:
            return {'error': dns['error']}
        
        ip = dns['ip']
        
        # Check of het publiek IP is
        try:
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback:
                return {'error': 'Private IP addresses are not allowed'}
        except:
            pass
        
        # Poortenlijst (1000+ poorten)
        ports = []
        # System ports
        ports.extend([21, 22, 23, 25, 53, 80, 110, 143, 443, 445, 465, 587, 993, 995])
        # Database poorten
        ports.extend([1433, 1521, 3306, 5432, 6379, 27017])
        # Web poorten
        ports.extend([8080, 8443, 8888, 9000, 9090])
        # Mail poorten
        ports.extend([25, 110, 143, 465, 587, 993, 995])
        # Overige populaire poorten
        ports.extend([3389, 5900, 8080, 8443, 8888, 9000])
        
        # Voeg tot 1000 poorten toe
        if max_ports > len(ports):
            additional = list(range(1024, 1024 + (max_ports - len(ports))))
            ports.extend(additional)
        
        ports = ports[:max_ports]
        
        print(f"🔄 Scannen van {domain} ({ip}) - {len(ports)} poorten")
        
        results = {}
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = {executor.submit(self.scan_port, ip, port): port for port in ports}
            for future in as_completed(futures):
                port, is_open = future.result()
                if is_open:
                    service = self.get_service_name(port)
                    results[port] = {'open': True, 'service': service}
        
        return {
            'ip': ip,
            'open_ports': results,
            'open_count': len(results),
            'total_scanned': len(ports)
        }
    
    def get_service_name(self, port):
        """Geef service naam voor poort"""
        services = {
            21: 'FTP', 22: 'SSH', 23: 'Telnet', 25: 'SMTP',
            53: 'DNS', 80: 'HTTP', 110: 'POP3', 143: 'IMAP',
            443: 'HTTPS', 445: 'SMB', 465: 'SMTPS', 587: 'SMTP',
            993: 'IMAPS', 995: 'POP3S', 1433: 'MSSQL',
            1521: 'Oracle', 3306: 'MySQL', 5432: 'PostgreSQL',
            6379: 'Redis', 27017: 'MongoDB', 3389: 'RDP',
            5900: 'VNC', 8080: 'HTTP-Alt', 8443: 'HTTPS-Alt'
        }
        return services.get(port, f'Port-{port}')
    
    def get_ssl_info(self, domain):
        """SSL/TLS informatie"""
        try:
            context = ssl.create_default_context()
            with socket.create_connection((domain, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    return {
                        'success': True,
                        'subject': dict(cert.get('subject', [{}])[0]) if cert.get('subject') else {},
                        'issuer': dict(cert.get('issuer', [{}])[0]) if cert.get('issuer') else {},
                        'notAfter': cert.get('notAfter', 'Unknown'),
                        'notBefore': cert.get('notBefore', 'Unknown'),
                        'protocol': ssock.version(),
                        'cipher': ssock.cipher()
                    }
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_http_headers(self, domain):
        """HTTP headers ophalen"""
        results = {}
        
        # HTTPS
        try:
            req = Request(f'https://{domain}')
            req.add_header('User-Agent', 'NIS2-Online-Scanner/1.0')
            response = urlopen(req, timeout=5)
            results['https'] = {
                'success': True,
                'status': response.getcode(),
                'server': response.headers.get('Server', 'Unknown'),
                'headers': dict(response.headers)
            }
        except:
            results['https'] = {'success': False, 'error': 'HTTPS failed'}
        
        # HTTP
        try:
            req = Request(f'http://{domain}')
            req.add_header('User-Agent', 'NIS2-Online-Scanner/1.0')
            response = urlopen(req, timeout=5)
            results['http'] = {
                'success': True,
                'status': response.getcode(),
                'server': response.headers.get('Server', 'Unknown'),
                'headers': dict(response.headers)
            }
        except:
            results['http'] = {'success': False, 'error': 'HTTP failed'}
        
        return results
    
    def scan_domain(self, domain, max_ports=1000):
        """Volledige domein scan"""
        print(f"🌐 Online scan gestart voor: {domain}")
        
        # DNS records
        dns_records = self.get_all_dns_records(domain)
        
        # Poorten
        ports = self.scan_ports(domain, max_ports)
        if 'error' in ports:
            return {'success': False, 'error': ports['error']}
        
        # SSL info (als 443 open is)
        ssl_info = None
        if 443 in ports.get('open_ports', {}):
            ssl_info = self.get_ssl_info(domain)
        
        # HTTP headers
        headers = self.get_http_headers(domain)
        
        return {
            'success': True,
            'domain': domain,
            'timestamp': datetime.now().isoformat(),
            'dns': dns_records,
            'ip': ports.get('ip'),
            'ports': ports.get('open_ports', {}),
            'open_port_count': ports.get('open_count', 0),
            'total_ports_scanned': ports.get('total_scanned', 0),
            'ssl': ssl_info,
            'headers': headers
        }

# ==================== FLASK ROUTES ====================

@app.route('/')
def index():
    """Web interface"""
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/scan', methods=['POST'])
def scan_domain():
    """API endpoint voor scannen"""
    try:
        data = request.get_json()
        domain = data.get('domain', '').strip()
        max_ports = data.get('max_ports', 1000)
        
        if not domain:
            return jsonify({'error': 'Domein is verplicht'}), 400
        
        # Valideer domein
        if len(domain) < 2:
            return jsonify({'error': 'Ongeldig domein'}), 400
        
        # Check of het een private IP is
        try:
            ip = socket.gethostbyname(domain)
            ip_obj = ipaddress.ip_address(ip)
            if ip_obj.is_private or ip_obj.is_loopback:
                return jsonify({'error': 'Private IPs zijn niet toegestaan'}), 400
        except:
            pass
        
        # Voer scan uit
        scanner = OnlineScanner()
        results = scanner.scan_domain(domain, max_ports)
        
        if results.get('success'):
            return jsonify({
                'success': True,
                'results': results,
                'message': f'Scan van {domain} voltooid'
            }), 200
        else:
            return jsonify({'error': results.get('error', 'Scan mislukt')}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/check', methods=['POST'])
def check_domain():
    """Snelle check zonder volledige scan"""
    try:
        data = request.get_json()
        domain = data.get('domain', '').strip()
        
        if not domain:
            return jsonify({'error': 'Domein is verplicht'}), 400
        
        # Basic checks
        results = {
            'domain': domain,
            'timestamp': datetime.now().isoformat(),
            'dns': {},
            'webserver': {},
            'mail': {}
        }
        
        # DNS check
        try:
            ip = socket.gethostbyname(domain)
            results['dns'] = {'ip': ip, 'success': True}
        except:
            results['dns'] = {'success': False, 'error': 'DNS failed'}
        
        # HTTP check
        try:
            req = Request(f'https://{domain}')
            req.add_header('User-Agent', 'NIS2-Check/1.0')
            response = urlopen(req, timeout=3)
            results['webserver'] = {
                'success': True,
                'status': response.getcode(),
                'server': response.headers.get('Server', 'Unknown')
            }
        except:
            try:
                req = Request(f'http://{domain}')
                req.add_header('User-Agent', 'NIS2-Check/1.0')
                response = urlopen(req, timeout=3)
                results['webserver'] = {
                    'success': True,
                    'status': response.getcode(),
                    'server': response.headers.get('Server', 'Unknown')
                }
            except:
                results['webserver'] = {'success': False, 'error': 'No webserver found'}
        
        # MX check
        try:
            result = subprocess.check_output(
                ['nslookup', '-type=MX', domain],
                stderr=subprocess.STDOUT,
                text=True,
                timeout=3
            )
            mx_records = []
            for line in result.split('\n'):
                if 'mail exchanger' in line.lower():
                    parts = line.split('=')
                    if len(parts) >= 2:
                        mx = parts[-1].strip()
                        if mx and not mx.startswith('#'):
                            mx_records.append(mx)
            results['mail']['mx_records'] = mx_records
        except:
            results['mail']['mx_records'] = []
        
        return jsonify(results), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/pricing', methods=['GET'])
def get_pricing():
    """Pricing informatie"""
    return jsonify({
        'pricing': [
            {
                'type': 'free',
                'name': 'Gratis Scan',
                'price': 0,
                'features': ['DNS check', 'HTTP check', 'Poort scan (100 poorten)']
            },
            {
                'type': 'pro',
                'name': 'Professioneel',
                'price': 49,
                'features': ['1000+ poorten', 'SSL/TLS analyse', 'Uitgebreid rapport']
            },
            {
                'type': 'enterprise',
                'name': 'Enterprise',
                'price': 199,
                'features': ['Onbeperkt scans', 'API toegang', 'Prioriteit support']
            }
        ]
    })

@app.route('/api/legal', methods=['GET'])
def legal():
    """Juridische disclaimer"""
    return jsonify({
        'disclaimer': """
        Deze tool is voor educatieve doeleinden en eigen gebruik.
        Scannen van systemen zonder toestemming is illegaal.
        Gebruik alleen met expliciete toestemming van de eigenaar.
        De ontwikkelaar is niet aansprakelijk voor misbruik.
        """
    })

# ==================== HTML TEMPLATE ====================
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="nl">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>NIS2 Online Scanner</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: #0A0E1A;
            color: #F0F4FF;
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            text-align: center;
            padding: 40px 0;
            border-bottom: 1px solid rgba(0, 212, 255, 0.1);
            margin-bottom: 30px;
        }
        .header h1 {
            font-size: 48px;
            background: linear-gradient(135deg, #00D4FF, #7C3AED);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            margin-bottom: 10px;
        }
        .header p {
            color: #8899BB;
            font-size: 18px;
        }
        .card {
            background: rgba(13, 19, 32, 0.8);
            border: 1px solid rgba(0, 212, 255, 0.1);
            border-radius: 12px;
            padding: 24px;
            margin-bottom: 20px;
            backdrop-filter: blur(10px);
        }
        .card:hover {
            border-color: rgba(0, 212, 255, 0.3);
        }
        .input-group {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }
        .input-group input {
            flex: 1;
            padding: 14px 20px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 8px;
            color: #F0F4FF;
            font-size: 16px;
            min-width: 200px;
        }
        .input-group input:focus {
            outline: none;
            border-color: #00D4FF;
            box-shadow: 0 0 20px rgba(0, 212, 255, 0.1);
        }
        .input-group select {
            padding: 14px 20px;
            background: rgba(255, 255, 255, 0.05);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 8px;
            color: #F0F4FF;
            font-size: 16px;
        }
        .btn {
            padding: 14px 32px;
            background: linear-gradient(135deg, #00D4FF, #7C3AED);
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(0, 212, 255, 0.3);
        }
        .btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        .result-section {
            margin-top: 20px;
        }
        .result-item {
            padding: 16px;
            margin-bottom: 12px;
            background: rgba(255, 255, 255, 0.03);
            border-radius: 8px;
            border-left: 4px solid #7C3AED;
        }
        .result-item.success {
            border-left-color: #00FF88;
        }
        .result-item.warning {
            border-left-color: #FFB800;
        }
        .result-item.danger {
            border-left-color: #FF3355;
        }
        .result-item .label {
            font-size: 12px;
            color: #8899BB;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        .result-item .value {
            font-size: 16px;
            margin-top: 4px;
        }
        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }
        .spinner {
            border: 4px solid rgba(255, 255, 255, 0.1);
            border-top: 4px solid #00D4FF;
            border-radius: 50%;
            width: 50px;
            height: 50px;
            animation: spin 0.8s linear infinite;
            margin: 20px auto;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
        .port-list {
            display: flex;
            flex-wrap: wrap;
            gap: 8px;
            margin-top: 8px;
        }
        .port-tag {
            padding: 4px 12px;
            background: rgba(0, 212, 255, 0.1);
            border: 1px solid rgba(0, 212, 255, 0.2);
            border-radius: 4px;
            font-size: 12px;
            font-family: monospace;
        }
        .port-tag.open {
            border-color: #00FF88;
            background: rgba(0, 255, 136, 0.1);
            color: #00FF88;
        }
        .grid-2 {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }
        @media (max-width: 768px) {
            .grid-2 {
                grid-template-columns: 1fr;
            }
            .header h1 {
                font-size: 32px;
            }
        }
        .disclaimer {
            font-size: 12px;
            color: #556688;
            text-align: center;
            margin-top: 40px;
            padding: 20px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }
        .status-badge {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 12px;
            font-size: 12px;
            font-weight: 600;
        }
        .status-badge.success {
            background: rgba(0, 255, 136, 0.2);
            color: #00FF88;
        }
        .status-badge.danger {
            background: rgba(255, 51, 85, 0.2);
            color: #FF3355;
        }
        .status-badge.warning {
            background: rgba(255, 184, 0, 0.2);
            color: #FFB800;
        }
        .status-badge.info {
            background: rgba(0, 212, 255, 0.2);
            color: #00D4FF;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛡️ NIS2 Online Scanner</h1>
            <p>Scan elk domein wereldwijd - Gratis en professioneel</p>
        </div>

        <div class="card">
            <h3 style="margin-bottom: 16px;">🎯 Scan een domein</h3>
            <div class="input-group">
                <input type="text" id="domainInput" placeholder="voorbeeld.nl" value="google.com">
                <select id="scanType">
                    <option value="quick">Snelle check (gratis)</option>
                    <option value="full" selected>Volledige scan (gratis)</option>
                    <option value="pro">Professional scan (1000+ poorten)</option>
                </select>
                <button class="btn" onclick="startScan()">🔍 Scan</button>
            </div>
            <div style="margin-top: 12px; font-size: 12px; color: #556688;">
                ⚠️ Alleen gebruiken met toestemming van de eigenaar
            </div>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p style="color: #8899BB;">Bezig met scannen... Dit kan even duren</p>
        </div>

        <div id="results"></div>

        <div class="disclaimer">
            <strong>🔒 Privacy & Security:</strong> Deze tool gebruikt alleen publiekelijk beschikbare informatie.<br>
            Scannen zonder toestemming is illegaal. Gebruik alleen voor eigen systemen of met toestemming.<br>
            <span style="color: #334455;">Versie 2.0.0 - Online Scanner</span>
        </div>
    </div>

    <script>
        async function startScan() {
            const domain = document.getElementById('domainInput').value.trim();
            const scanType = document.getElementById('scanType').value;
            
            if (!domain) {
                alert('Voer een geldig domein in');
                return;
            }
            
            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('results').innerHTML = '';
            
            // Determine max ports based on scan type
            let maxPorts = 100;
            if (scanType === 'full') maxPorts = 500;
            if (scanType === 'pro') maxPorts = 1000;
            
            try {
                const response = await fetch('/api/scan', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ 
                        domain: domain,
                        max_ports: maxPorts
                    })
                });
                
                const data = await response.json();
                
                if (response.ok && data.success) {
                    displayResults(data.results);
                } else {
                    displayError(data.error || 'Scan mislukt');
                }
            } catch (error) {
                displayError('Netwerk fout: ' + error.message);
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }
        
        function displayResults(results) {
            const container = document.getElementById('results');
            
            let html = `
                <div class="card result-section">
                    <h3 style="margin-bottom: 16px;">📊 Scan Resultaten</h3>
                    <div class="grid-2">
                        <div class="result-item success">
                            <div class="label">Domein</div>
                            <div class="value"><strong>${results.domain}</strong></div>
                        </div>
                        <div class="result-item ${results.ip ? 'success' : 'danger'}">
                            <div class="label">IP Adres</div>
                            <div class="value">${results.ip || 'Niet gevonden'}</div>
                        </div>
                        <div class="result-item success">
                            <div class="label">Open Poorten</div>
                            <div class="value"><strong>${results.open_port_count || 0}</strong> van ${results.total_ports_scanned || 0}</div>
                        </div>
                        <div class="result-item ${results.open_port_count > 0 ? 'warning' : 'success'}">
                            <div class="label">Status</div>
                            <div class="value">
                                <span class="status-badge ${results.open_port_count > 0 ? 'warning' : 'success'}">
                                    ${results.open_port_count > 0 ? '⚠️ Poorten open' : '✅ Veilig'}
                                </span>
                            </div>
                        </div>
                    </div>
            `;
            
            // Poorten
            if (results.ports && Object.keys(results.ports).length > 0) {
                html += `
                    <div class="result-item">
                        <div class="label">🔌 Open Poorten</div>
                        <div class="port-list">
                `;
                for (const [port, data] of Object.entries(results.ports)) {
                    html += `<span class="port-tag open">${port} (${data.service})</span>`;
                }
                html += `</div></div>`;
            }
            
            // DNS records
            if (results.dns) {
                html += `
                    <div class="result-item">
                        <div class="label">🌐 DNS Records</div>
                        <div style="margin-top: 8px; font-size: 14px;">
                `;
                for (const [type, records] of Object.entries(results.dns)) {
                    if (records && records.length > 0) {
                        html += `<div><strong>${type}:</strong> ${Array.isArray(records) ? records.join(', ') : records}</div>`;
                    }
                }
                html += `</div></div>`;
            }
            
            // SSL info
            if (results.ssl && results.ssl.success) {
                html += `
                    <div class="result-item success">
                        <div class="label">🔒 SSL/TLS</div>
                        <div style="margin-top: 8px; font-size: 14px;">
                            <div><strong>Protocol:</strong> ${results.ssl.protocol || 'Unknown'}</div>
                            <div><strong>Geldig tot:</strong> ${results.ssl.notAfter || 'Unknown'}</div>
                            <div><strong>Uitgever:</strong> ${results.ssl.issuer?.commonName || 'Unknown'}</div>
                        </div>
                    </div>
                `;
            }
            
            // Headers
            if (results.headers) {
                for (const [protocol, data] of Object.entries(results.headers)) {
                    if (data.success) {
                        html += `
                            <div class="result-item success">
                                <div class="label">🌍 ${protocol.toUpperCase()} Headers</div>
                                <div style="margin-top: 8px; font-size: 14px;">
                                    <div><strong>Status:</strong> ${data.status}</div>
                                    <div><strong>Server:</strong> ${data.server}</div>
                                </div>
                            </div>
                        `;
                    }
                }
            }
            
            html += `
                    <div style="margin-top: 16px; padding: 16px; background: rgba(255, 212, 0, 0.05); border-radius: 8px; border-left: 4px solid #FFB800;">
                        <div style="font-size: 12px; color: #8899BB;">
                            ⚖️ <strong>Juridische disclaimer:</strong> Deze scan is uitgevoerd met publiekelijk beschikbare informatie.
                            Gebruik de resultaten alleen voor legitieme doeleinden.
                        </div>
                    </div>
                </div>
            `;
            
            container.innerHTML = html;
        }
        
        function displayError(error) {
            const container = document.getElementById('results');
            container.innerHTML = `
                <div class="card" style="border-color: #FF3355;">
                    <h3 style="color: #FF3355;">❌ Fout</h3>
                    <p style="color: #8899BB; margin-top: 8px;">${error}</p>
                    <div style="margin-top: 16px; padding: 16px; background: rgba(255, 51, 85, 0.05); border-radius: 8px; border-left: 4px solid #FF3355;">
                        <div style="font-size: 12px; color: #8899BB;">
                            💡 Tips:
                            <ul style="margin-top: 4px; padding-left: 20px;">
                                <li>Controleer of het domein correct is</li>
                                <li>Probeer een andere domeinnaam</li>
                                <li>Zorg dat je toestemming hebt om te scannen</li>
                            </ul>
                        </div>
                    </div>
                </div>
            `;
        }
        
        // Enter to scan
        document.getElementById('domainInput').addEventListener('keypress', function(e) {
            if (e.key === 'Enter') startScan();
        });
    </script>
</body>
</html>
"""

# ==================== MAIN ====================
if __name__ == '__main__':
    init_db()
    port = int(os.environ.get('PORT', 5077))
    print(f"🛡️  NIS2 Online Scanner gestart op poort {port}")
    app.run(host='0.0.0.0', port=port, debug=False)