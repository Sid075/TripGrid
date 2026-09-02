// app.js

const API_BASE = "http://localhost:8000/api";
let pollInterval = null;

// Session Management
function getSessionId() {
    let sid = localStorage.getItem('pd_session_id');
    if (!sid) {
        sid = 'sess_' + Math.random().toString(36).substr(2, 9);
        localStorage.setItem('pd_session_id', sid);
    }
    return sid;
}

function getGroupCode() {
    return localStorage.getItem('pd_group_code');
}

function setGroupCode(code) {
    localStorage.setItem('pd_group_code', code);
}

function getUserName() {
    return localStorage.getItem('pd_user_name') || 'Guest';
}

function setUserName(name) {
    localStorage.setItem('pd_user_name', name || 'Guest');
}

// Router & View Management
function renderView(viewId) {
    const container = document.getElementById('app-container');
    const template = document.getElementById(viewId);
    container.innerHTML = template.innerHTML;
    
    // Setup listeners for the new view
    if (viewId === 'view-landing') {
        setupLanding();
    } else if (viewId === 'view-dashboard') {
        setupDashboard();
    }
    
    // Update Nav
    const navInfo = document.getElementById('nav-user-info');
    if (getGroupCode()) {
        navInfo.innerHTML = `<span>${getUserName()}</span> | <button onclick="logout()" class="text-brand-textMuted hover:text-white transition">Exit Group</button>`;
    } else {
        navInfo.innerHTML = '';
    }
}

function logout() {
    localStorage.removeItem('pd_group_code');
    if(pollInterval) clearInterval(pollInterval);
    renderView('view-landing');
}

// Views Setup
function setupLanding() {
    document.getElementById('user-name').value = getUserName() !== 'Guest' ? getUserName() : '';
    
    document.getElementById('btn-create-group').onclick = async () => {
        const name = document.getElementById('user-name').value;
        setUserName(name);
        
        try {
            const res = await fetch(`${API_BASE}/group/create`, { 
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ session_id: getSessionId() })
            });
            const data = await res.json();
            console.log('Group created, code:', data.group_code);
            await joinGroup(data.group_code);
        } catch (e) { alert("Error creating group"); }
    };
    
    document.getElementById('btn-join-group').onclick = async () => {
        const name = document.getElementById('user-name').value;
        const code = document.getElementById('group-code-input').value.toUpperCase();
        setUserName(name);
        if(code) await joinGroup(code);
    };
}

async function joinGroup(code) {
    try {
        const res = await fetch(`${API_BASE}/group/join`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                session_id: getSessionId(),
                name: getUserName(),
                group_code: code
            })
        });
        if(res.ok) {
            setGroupCode(code);
            renderView('view-dashboard');
        } else {
            alert("Invalid Group Code");
        }
    } catch(e) { console.error(e); }
}

function setupDashboard() {
    document.getElementById('display-group-code').innerText = getGroupCode();
    
    document.getElementById('btn-save-pref').onclick = async () => {
        const type = document.getElementById('pref-type').value;
        const budget = parseFloat(document.getElementById('pref-budget').value);
        
        const resp = await fetch(`${API_BASE}/group/preferences`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                session_id: getSessionId(),
                destination_type: type,
                budget: budget
            })
        });
        if (!resp.ok) {
            const err = await resp.json();
            console.error('Preference save error:', err);
        } else {
            console.log('Preferences saved');
        }
        pollState(); // Force immediate update
    };
    
    document.getElementById('btn-generate').onclick = async () => {
        const btn = document.getElementById('btn-generate');
        btn.innerHTML = `<span class="animate-pulse">Generating Recommendations...</span>`;
        btn.disabled = true;
        
        try {
            const res = await fetch(`${API_BASE}/group/${getGroupCode()}/generate`, {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ session_id: getSessionId() })
            });
            if(!res.ok) {
                const data = await res.json();
                alert(data.detail || "Error generating");
                btn.innerHTML = `<span>Generate Group Recommendations</span>`;
                btn.disabled = false;
            } else {
                pollState(); // Trigger update
            }
        } catch(e) {
            btn.innerHTML = `<span>Generate Group Recommendations</span>`;
            btn.disabled = false;
        }
    };
    
    // Start Polling
    pollState();
    pollInterval = setInterval(pollState, 3000);
}

// Polling & Render Logic
async function pollState() {
    const code = getGroupCode();
    if(!code) return;
    
    try {
        const res = await fetch(`${API_BASE}/group/${code}/state?session_id=${getSessionId()}`);
        if(!res.ok) {
            if(res.status === 404) logout();
            return;
        }
        const state = await res.json();
        console.log('Poll state:', state);
        
        // Update Budget
        document.getElementById('display-budget').innerText = state.pooled_budget.toLocaleString();
        
        // Update Members
        const membersHtml = state.users.map(u => `
            <div class="flex justify-between items-center bg-black/30 p-3 rounded-lg border border-white/5">
                <div class="flex items-center gap-3">
                    <div class="w-8 h-8 rounded-full bg-brand-gold/20 flex items-center justify-center text-brand-gold font-bold">${u.name.charAt(0).toUpperCase()}</div>
                    <span class="font-medium">${u.name}</span>
                </div>
                <div class="text-xs text-brand-textMuted flex gap-2">
                    ${u.has_pref ? '<span class="text-green-400">Pref Set</span>' : '<span>Waiting</span>'}
                    ${u.has_voted ? '<span class="text-brand-gold">Voted</span>' : ''}
                </div>
            </div>
        `).join('');
        document.getElementById('members-list').innerHTML = membersHtml;
        
        // ADK Insights
        const adkDiv = document.getElementById('adk-insights');
        if(state.adk_insights) {
            adkDiv.classList.remove('hidden');
            document.getElementById('adk-text').innerText = state.adk_insights;
        }
        
        // Host Actions
        const hostActions = document.getElementById('host-actions');
        if(state.is_host && !state.recommendations_generated) {
            hostActions.classList.remove('hidden');
        } else {
            hostActions.classList.add('hidden');
        }

        // Recommendations
        const recsGrid = document.getElementById('recommendations-grid');
        if(state.recommendations.length > 0) {
            recsGrid.innerHTML = state.recommendations.map(rec => `
                <div class="destination-card h-80 relative rounded-xl" onclick="voteFor('${rec.destination}', ${state.recommendations_generated})">
                    <img src="${rec.image}" class="absolute inset-0 w-full h-full object-cover">
                    <div class="absolute inset-0 overlay"></div>
                    <div class="absolute bottom-0 left-0 p-6 w-full z-10">
                        <div class="flex justify-between items-end mb-2">
                            <h4 class="font-display text-2xl font-bold">${rec.destination}</h4>
                            <span class="text-brand-gold font-bold">${rec.score}% Match</span>
                        </div>
                        <p class="text-sm text-white/80 line-clamp-2 mb-2">${rec.description}</p>
                        <div class="flex gap-4 text-xs font-semibold uppercase tracking-widest text-brand-textMuted">
                            <span>$${rec.cost.toLocaleString()}</span>
                            <span>⭐ ${rec.rating}</span>
                        </div>
                    </div>
                    ${state.recommendations_generated ? `<div class="absolute top-4 right-4 bg-brand-gold text-black text-xs font-bold px-3 py-1 rounded-full opacity-0 hover-show transition-opacity">VOTE</div>` : ''}
                </div>
            `).join('');
        } else {
            recsGrid.innerHTML = `<p class="text-brand-textMuted italic col-span-2">Waiting for host to generate recommendations...</p>`;
        }
        
        // Voting
        const voteSection = document.getElementById('voting-section');
        if(Object.keys(state.votes).length > 0) {
            const totalVotes = state.users.filter(u => u.has_voted).length;
            voteSection.innerHTML = Object.entries(state.votes).map(([dest, count]) => `
                <div class="mb-4">
                    <div class="flex justify-between text-sm font-medium mb-1">
                        <span>${dest}</span>
                        <span class="text-brand-gold">${count} Vote${count>1?'s':''}</span>
                    </div>
                    <div class="vote-bar">
                        <div class="vote-fill" style="width: ${(count/Math.max(totalVotes, 1))*100}%"></div>
                    </div>
                </div>
            `).join('');
        } else {
            voteSection.innerHTML = `<p class="text-brand-textMuted italic">Click a destination card to cast your vote.</p>`;
        }
        
    } catch(e) { console.error("Polling error", e); }
}

async function voteFor(destName, isGenerated) {
    if (!isGenerated) return;
    
    await fetch(`${API_BASE}/group/vote`, {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            session_id: getSessionId(),
            destination_name: destName
        })
    });
    pollState();
}

// Init
if(getGroupCode()) {
    renderView('view-dashboard');
} else {
    renderView('view-landing');
}
