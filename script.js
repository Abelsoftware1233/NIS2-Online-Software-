// ==================== CONFIG ====================
// Backend draait op poort 5077. Als de frontend vanaf hetzelfde adres/origin
// wordt geserveerd door Flask zelf, kun je dit gewoon op window.location.origin
// laten staan. Draai je index.html los (bv. via Live Server of een andere host),
// dan wijst dit automatisch naar http://<zelfde host>:5077.
const API_BASE = (() => {
    const { protocol, hostname, port, origin } = window.location;
    // Als de pagina al vanaf poort 5077 komt (Flask serveert zelf), gebruik origin.
    if (port === '5077') return origin;
    // Anders: praat met de backend op dezelfde hostname, maar op poort 5077.
    return `${protocol}//${hostname}:5077`;
})();

// ==================== STATE ====================
let state = {
    token: null,
    sessionId: null,
    questions: [],
    answers: {},
    categories: [],
    currentQuestionIndex: 0,
    scanResults: null,
    auditResults: null,
    domain: ''
};

// ==================== TOAST ====================
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    container.appendChild(toast);
    setTimeout(() => {
        toast.style.opacity = '0';
        toast.style.transition = 'opacity 0.5s';
        setTimeout(() => toast.remove(), 500);
    }, 4000);
}

// ==================== VIEWS ====================
function showLogin() {
    document.getElementById('loginView').classList.remove('hidden');
    document.getElementById('registerView').classList.add('hidden');
    document.getElementById('dashboardView').classList.add('hidden');
    document.getElementById('resultsView').classList.add('hidden');
}

function showRegister() {
    document.getElementById('loginView').classList.add('hidden');
    document.getElementById('registerView').classList.remove('hidden');
    document.getElementById('dashboardView').classList.add('hidden');
    document.getElementById('resultsView').classList.add('hidden');
}

function showDashboard() {
    document.getElementById('loginView').classList.add('hidden');
    document.getElementById('registerView').classList.add('hidden');
    document.getElementById('dashboardView').classList.remove('hidden');
    document.getElementById('resultsView').classList.add('hidden');
    renderQuestions();
}

function showResults() {
    document.getElementById('loginView').classList.add('hidden');
    document.getElementById('registerView').classList.add('hidden');
    document.getElementById('dashboardView').classList.add('hidden');
    document.getElementById('resultsView').classList.remove('hidden');
    renderResults();
}

function updateStatus(text, isOnline = true) {
    const badge = document.getElementById('statusBadge');
    badge.textContent = isOnline ? `● ${text}` : `● Offline`;
    badge.style.color = isOnline ? 'var(--cyan)' : 'var(--red)';
}

// ==================== AUTH ====================
async function handleLogin(e) {
    e.preventDefault();
    const email = document.getElementById('loginEmail').value;
    const password = document.getElementById('loginPassword').value;

    try {
        const res = await fetch(`${API_BASE}/api/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (res.ok) {
            state.token = data.token;
            state.sessionId = data.session_id;
            localStorage.setItem('nis2_token', data.token);
            localStorage.setItem('nis2_session', data.session_id);
            showToast('Login succesvol!', 'success');
            await loadQuestions();
            showDashboard();
        } else {
            showToast(data.error || 'Login mislukt', 'error');
        }
    } catch (err) {
        showToast('Network error: ' + err.message, 'error');
        updateStatus('Offline', false);
    }
}

async function handleRegister(e) {
    e.preventDefault();
    const email = document.getElementById('regEmail').value;
    const password = document.getElementById('regPassword').value;
    const bedrijfsnaam = document.getElementById('regBedrijf').value;

    try {
        const res = await fetch(`${API_BASE}/api/register`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password, bedrijfsnaam })
        });
        const data = await res.json();
        if (res.ok) {
            showToast('Registratie succesvol! Log nu in.', 'success');
            showLogin();
            document.getElementById('loginEmail').value = email;
        } else {
            showToast(data.error || 'Registratie mislukt', 'error');
        }
    } catch (err) {
        showToast('Network error: ' + err.message, 'error');
        updateStatus('Offline', false);
    }
}

function handleLogout() {
    state.token = null;
    state.sessionId = null;
    localStorage.removeItem('nis2_token');
    localStorage.removeItem('nis2_session');
    showLogin();
    showToast('Uitgelogd', 'info');
}

// ==================== QUESTIONS ====================
async function loadQuestions() {
    try {
        const res = await fetch(`${API_BASE}/api/questions`);
        const data = await res.json();
        if (res.ok) {
            state.questions = data.questions;
            state.categories = data.categories;
            // Load saved answers
            await loadAnswers();
            renderQuestions();
        } else {
            showToast('Fout bij laden vragen', 'error');
        }
    } catch (err) {
        showToast('Network error: ' + err.message, 'error');
        updateStatus('Offline', false);
    }
}

async function loadAnswers() {
    try {
        const res = await fetch(`${API_BASE}/api/answers?token=${state.token}`);
        const data = await res.json();
        if (res.ok) {
            data.answers.forEach(a => {
                state.answers[a.question_id] = a.answer;
            });
        }
    } catch (err) {
        // Silent fail - answers are optional
    }
}

async function saveAnswer(questionId, category, value) {
    try {
        const res = await fetch(`${API_BASE}/api/answer`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                token: state.token,
                question_id: questionId,
                answer: value,
                category: category
            })
        });
        if (res.ok) {
            state.answers[questionId] = value;
            updateProgress();
        } else {
            const data = await res.json();
            showToast(data.error || 'Fout bij opslaan', 'error');
        }
    } catch (err) {
        showToast('Network error: ' + err.message, 'error');
    }
}

function renderQuestions() {
    const container = document.getElementById('questionsContainer');
    if (!state.questions.length) {
        container.innerHTML = '<p style="color: var(--gray);">Laden...</p>';
        return;
    }

    let html = '';
    let answered = 0;

    state.questions.forEach((q, idx) => {
        const answer = state.answers[q.id] || 0;
        if (answer > 0) answered++;

        html += `
            <div class="question-item" data-id="${q.id}">
                <div class="q-category">${q.category} • Vraag ${idx + 1}/40</div>
                <div class="q-text">${q.question}</div>
                <div class="q-desc">${q.description}</div>
                <div class="rating-buttons">
                    ${[1,2,3,4,5].map(v => `
                        <button class="rating-btn ${answer === v ? 'active' : ''}" 
                                onclick="saveAnswer('${q.id}', '${q.category}', ${v})">
                            ${v}
                        </button>
                    `).join('')}
                    <span style="font-size: 11px; color: var(--gray); margin-left: 8px;">
                        (1=Helemaal niet • 5=Helemaal wel)
                    </span>
                </div>
            </div>
        `;
    });

    container.innerHTML = html;
    updateProgress();
}

function updateProgress() {
    const total = state.questions.length || 40;
    const answered = Object.values(state.answers).filter(v => v > 0).length;
    const pct = Math.round((answered / total) * 100);

    document.getElementById('progressText').textContent = `${answered}/${total}`;
    document.getElementById('progressPercent').textContent = `${pct}%`;
    document.getElementById('progressFill').style.width = `${pct}%`;
}

// ==================== SCAN ====================
async function runScan() {
    const domain = document.getElementById('domainInput').value.trim();
    if (!domain) {
        showToast('Voer een domein in', 'error');
        return;
    }

    const btn = document.getElementById('scanBtn');
    btn.disabled = true;
    btn.textContent = '⏳ Scannen...';
    document.getElementById('scanStatus').textContent = 'Bezig met scannen...';

    try {
        const res = await fetch(`${API_BASE}/api/scan`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: state.token, domain })
        });
        const data = await res.json();

        if (res.ok) {
            state.scanResults = data.results;
            state.domain = domain;
            showToast(`Scan van ${domain} voltooid!`, 'success');
            document.getElementById('scanStatus').textContent = `✅ Scan voltooid voor ${domain}`;
        } else {
            showToast(data.error || 'Scan mislukt', 'error');
            document.getElementById('scanStatus').textContent = `❌ ${data.error || 'Scan mislukt'}`;
        }
    } catch (err) {
        showToast('Network error: ' + err.message, 'error');
    }

    btn.disabled = false;
    btn.textContent = '🔍 Scan';
}

// ==================== COMPLETE ====================
async function completeAudit() {
    const answered = Object.values(state.answers).filter(v => v > 0).length;
    if (answered < 40) {
        showToast(`Beantwoord eerst alle 40 vragen (${answered}/40)`, 'error');
        return;
    }

    const btn = document.getElementById('completeBtn');
    btn.disabled = true;
    btn.textContent = '⏳ Verwerken...';

    try {
        const res = await fetch(`${API_BASE}/api/complete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ token: state.token })
        });
        const data = await res.json();

        if (res.ok) {
            state.auditResults = data;
            document.getElementById('reportBtn').disabled = false;
            showToast('Audit voltooid! Bekijk de resultaten.', 'success');
            showResults();
        } else {
            showToast(data.error || 'Fout bij voltooien', 'error');
        }
    } catch (err) {
        showToast('Network error: ' + err.message, 'error');
    }

    btn.disabled = false;
    btn.textContent = '📊 Voltooi Audit';
}

// ==================== RESULTS ====================
function renderResults() {
    if (!state.auditResults) return;

    const scores = state.auditResults.scores || {};
    const advice = state.auditResults.advice || [];
    const pct = scores.percentage || 0;

    // Score
    document.getElementById('resultScore').textContent = pct + '%';
    const circle = document.getElementById('resultScore');
    circle.style.borderColor = pct >= 70 ? 'var(--green)' : pct >= 40 ? 'var(--yellow)' : 'var(--red)';

    // Category scores
    const catContainer = document.getElementById('categoryScores');
    let catHtml = '';
    for (const [cat, data] of Object.entries(scores.categories || {})) {
        const p = data.percentage || 0;
        const color = p >= 70 ? 'var(--green)' : p >= 40 ? 'var(--yellow)' : 'var(--red)';
        catHtml += `
            <div style="display: flex; justify-content: space-between; padding: 6px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                <span style="font-size: 13px;">${cat}</span>
                <span style="font-size: 13px; color: ${color}; font-weight: 700;">${p}%</span>
            </div>
        `;
    }
    catContainer.innerHTML = catHtml || '<p style="color: var(--gray);">Geen categorie data</p>';

    // Advice
    const advContainer = document.getElementById('adviceContainer');
    let advHtml = '';
    advice.forEach(item => {
        const priority = item.priority || 'geel';
        advHtml += `
            <div class="advice-item ${priority}">
                <div class="advice-title">${item.title || ''}</div>
                <div class="advice-action">${(item.action || '').replace(/\n/g, '<br>')}</div>
            </div>
        `;
    });
    advContainer.innerHTML = advHtml || '<p style="color: var(--gray);">Geen advies beschikbaar</p>';
}

// ==================== REPORT ====================
async function downloadReport() {
    try {
        const res = await fetch(`${API_BASE}/api/report?token=${state.token}`);
        if (res.ok) {
            const blob = await res.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'nis2_audit_report.pdf';
            document.body.appendChild(a);
            a.click();
            a.remove();
            window.URL.revokeObjectURL(url);
            showToast('Rapport gedownload!', 'success');
        } else {
            const data = await res.json();
            showToast(data.error || 'Fout bij genereren rapport', 'error');
        }
    } catch (err) {
        showToast('Network error: ' + err.message, 'error');
    }
}

// ==================== INIT ====================
async function init() {
    // Check of de backend bereikbaar is
    try {
        const res = await fetch(`${API_BASE}/`);
        if (res.ok) {
            updateStatus('Verbonden');
        } else {
            updateStatus('Offline', false);
        }
    } catch (err) {
        updateStatus('Offline', false);
        showToast(`Kan backend niet bereiken op ${API_BASE}`, 'error');
    }

    // Check for existing session
    const token = localStorage.getItem('nis2_token');
    const session = localStorage.getItem('nis2_session');

    if (token && session) {
        state.token = token;
        state.sessionId = session;
        try {
            await loadQuestions();
            showDashboard();
            return;
        } catch (err) {
            // Session expired, fall through to login
        }
    }

    showLogin();
}

// Start the app
init();
