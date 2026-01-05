<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>DOCU-GEN 333+1 | Plateforme de Scénarisation</title>
    <!-- Lucide Icons & Chart.js -->
    <script src="https://unpkg.com/lucide@latest"></script>
    <style>
        :root {
            --primary: #2C3E50;    /* Bleu Ardoise (Local Scouting) */
            --accent: #E67E22;     /* Orange Brique (Local Scouting) */
            --danger: #e50914;     /* Rouge (Action IA) */
            --bg: #f3f4f6;         /* Fond gris clair */
            --panel: #ffffff;      /* Blanc pur pour les cartes */
            --text: #2d3748;
            --dark-panel: #1a202c; /* Panel sombre pour le chatbot */
        }

        body { 
            margin: 0; 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            background: var(--bg); 
            color: var(--text); 
            height: 100vh; 
            display: flex; 
            flex-direction: column; 
            overflow: hidden; 
        }

        /* HEADER HARMONISÉ */
        header { 
            background: linear-gradient(135deg, var(--primary) 0%, #34495e 100%); 
            padding: 15px 25px; 
            border-bottom: 3px solid var(--accent); 
            display: flex; 
            justify-content: space-between; 
            align-items: center; 
            box-shadow: 0 4px 12px rgba(0,0,0,0.1);
            color: white;
            z-index: 100;
        }
        .logo { font-weight: 800; letter-spacing: 1px; font-size: 1.4rem; display: flex; align-items: center; gap: 10px; }
        .status-bar { display: flex; gap: 20px; font-size: 0.8rem; font-weight: 600; }
        .status-badge { padding: 4px 12px; border-radius: 20px; background: rgba(255,255,255,0.1); border: 1px solid rgba(255,255,255,0.2); }
        .active-dot { color: #2ecc71; margin-right: 5px; }

        /* WORKSPACE */
        .workspace { display: flex; flex: 1; overflow: hidden; }

        /* PANEL GAUCHE : FORMULAIRE PRO */
        .panel-left { width: 360px; background: var(--panel); border-right: 1px solid #e2e8f0; padding: 25px; overflow-y: auto; box-shadow: 2px 0 10px rgba(0,0,0,0.05); }
        .input-group { margin-bottom: 20px; }
        label { display: block; font-size: 0.75rem; color: #64748b; text-transform: uppercase; margin-bottom: 8px; font-weight: 700; letter-spacing: 0.5px; }
        input, textarea { 
            width: 100%; background: #f8fafc; border: 2px solid #e2e8f0; color: var(--text); 
            padding: 12px; border-radius: 8px; box-sizing: border-box; font-size: 0.95rem; transition: 0.2s;
        }
        input:focus, textarea:focus { border-color: var(--accent); outline: none; background: white; }
        textarea { height: 100px; resize: none; }
        h3 { font-size: 0.9rem; color: var(--primary); border-bottom: 2px solid #f1f5f9; padding-bottom: 8px; margin-top: 30px; display: flex; align-items: center; gap: 8px; }

        /* BOUTONS HARMONISÉS */
        .btn { padding: 12px 20px; border: none; border-radius: 8px; cursor: pointer; font-weight: 700; transition: all 0.2s; display: flex; align-items: center; justify-content: center; gap: 8px; width: 100%; }
        .btn-import { background: var(--primary); color: white; margin-bottom: 25px; }
        .btn-import:hover { background: #34495e; transform: translateY(-2px); }
        .btn-gen { background: linear-gradient(135deg, var(--danger) 0%, #b9060f 100%); color: white; font-size: 1rem; margin-top: 20px; box-shadow: 0 4px 15px rgba(229, 9, 20, 0.3); }
        .btn-gen:hover { transform: scale(1.02); box-shadow: 0 6px 20px rgba(229, 9, 20, 0.4); }

        /* PANEL CENTRAL : L'ÉDITEUR PAPIER */
        .panel-center { flex: 1; background: #cbd5e0; padding: 40px; overflow-y: auto; display: flex; flex-direction: column; align-items: center; }
        .paper { 
            background: white; color: #1a202c; width: 21cm; min-height: 29.7cm; padding: 2.5cm; 
            font-family: 'Courier New', Courier, monospace; font-size: 11pt; line-height: 1.3;
            box-shadow: 0 15px 45px rgba(0,0,0,0.2); white-space: pre-wrap; outline: none; margin-bottom: 60px;
        }
        .editor-toolbar { 
            position: sticky; top: -20px; background: white; padding: 10px 25px; border-radius: 50px; 
            border: 2px solid var(--primary); display: flex; gap: 20px; margin-bottom: 30px; z-index: 50; 
            box-shadow: 0 8px 20px rgba(0,0,0,0.1);
        }

        /* PANEL DROIT : CHATBOT */
        .panel-right { width: 320px; background: var(--dark-panel); color: white; border-left: 1px solid #000; display: flex; flex-direction: column; }
        .chat-history { flex: 1; padding: 20px; overflow-y: auto; font-size: 0.9rem; }
        .msg { padding: 12px; border-radius: 10px; margin-bottom: 15px; line-height: 1.5; }
        .msg.ai { background: #2d3748; color: #e2e8f0; border-left: 4px solid var(--accent); }
        .msg.user { background: var(--accent); color: white; margin-left: 20px; text-align: right; }
        .chat-input-zone { padding: 20px; background: #1a202c; border-top: 1px solid #2d3748; }
        .btn-brain { background: #4a5568; color: white; margin-top: 10px; font-size: 0.75rem; }

        /* MODALS */
        .modal { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.85); z-index: 1000; justify-content: center; align-items: center; backdrop-filter: blur(5px); }
        .modal-box { background: white; padding: 30px; border-radius: 16px; width: 600px; max-height: 85vh; overflow-y: auto; color: var(--text); }
        .angle-card { border: 2px solid #e2e8f0; border-radius: 12px; padding: 20px; margin-bottom: 15px; cursor: pointer; transition: 0.3s; }
        .angle-card:hover { border-color: var(--accent); background: #fffaf0; transform: scale(1.02); }
        .angle-card h2 { color: var(--accent); margin: 0 0 10px 0; font-size: 1.2rem; }

        /* LOADING */
        #loader { display: none; position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(44, 62, 80, 0.9); z-index: 2000; flex-direction: column; justify-content: center; align-items: center; color: white; }
        .spinner { width: 50px; height: 50px; border: 5px solid rgba(255,255,255,0.2); border-top: 5px solid var(--accent); border-radius: 50%; animation: spin 1s linear infinite; margin-bottom: 20px; }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
    </style>
</head>
<body>

<div id="loader">
    <div class="spinner"></div>
    <div style="font-weight: 800; letter-spacing: 2px; text-transform: uppercase;" id="loader-text">Analyse des données...</div>
</div>

<header>
    <div class="logo"><i data-lucide="brain-circuit"></i> DOCU-GEN 333+1</div>
    <div class="status-bar">
        <div class="status-badge"><span class="active-dot">●</span> BRIDGE OPÉRATIONNEL</div>
        <div class="status-badge">V6.5 PRO</div>
    </div>
</header>

<div class="workspace">
    <!-- GAUCHE : DONNÉES -->
    <div class="panel-left">
        <button class="btn btn-import" onclick="openImportModal()">
            <i data-lucide="download-cloud"></i> CHARGER UN IMPORT TERRAIN
        </button>

        <div class="input-group">
            <label>🌍 Contexte / Région</label>
            <input type="text" id="ctx" placeholder="Pays, Province, Saison...">
        </div>

        <h3><i data-lucide="users"></i> LES 3 GARDIENS</h3>
        <div class="input-group">
            <label>Gardien 1 (MATIÈRE)</label>
            <textarea id="g1" placeholder="Nom, Geste, Typologie..."></textarea>
        </div>
        <div class="input-group">
            <label>Gardien 2 (TECHNIQUE)</label>
            <textarea id="g2"></textarea>
        </div>
        <div class="input-group">
            <label>Gardien 3 (LIEN)</label>
            <textarea id="g3"></textarea>
        </div>

        <h3><i data-lucide="sparkles"></i> CONVERGENCE</h3>
        <div class="input-group">
            <label>La Fête / Rituel (+1)</label>
            <textarea id="evt" placeholder="Décrivez l'événement final..."></textarea>
        </div>

        <button class="btn btn-gen" onclick="analyzeAngles()">
            <i data-lucide="wand-2"></i> 1. ANALYSER LES ANGLES
        </button>
    </div>

    <!-- CENTRE : SCÉNARIO -->
   <!-- PANEL CENTRAL : L'ÉDITEUR AVEC HISTORIQUE -->
<div class="panel-center" style="display: flex; flex-direction: column; align-items: center;">
    
    <!-- BANDEAU D'IDENTIFICATION STUDIO (DYNAMIQUE) -->
    <div id="project-header" style="width: 21cm; margin-bottom: 25px; display: none; background: white; border-radius: 12px; padding: 15px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); border-left: 6px solid var(--accent); align-items: center; justify-content: space-between;">
        <div style="display: flex; align-items: center; gap: 20px;">
            <!-- Vignette Région -->
            <img id="display-vignette" src="" style="width: 80px; height: 80px; border-radius: 8px; object-fit: cover; background: #ddd; border: 2px solid #eee;">
            <div>
                <div id="display-region" style="font-size: 0.7rem; color: var(--accent); font-weight: 800; text-transform: uppercase; letter-spacing: 2px;">RÉGION</div>
                <h2 id="display-title" style="margin: 2px 0; color: var(--primary); font-size: 1.4rem; font-weight: 800;">Titre du Scénario</h2>
                <div style="font-size: 0.85rem; color: #64748b;">
                    <i data-lucide="user" style="width:14px; vertical-align:middle;"></i> 
                    Correspondant : <span id="display-fixer" style="font-weight: 600; color: var(--primary);">...</span>
                </div>
            </div>
        </div>
        <div style="text-align: right;">
            <div id="display-version-tag" style="font-size: 0.7rem; background: var(--primary); color: white; padding: 4px 12px; border-radius: 20px; font-weight: 800;">VERSION : EN COURS</div>
            <div id="display-angle" style="font-size: 0.8rem; color: var(--accent); font-weight: 700; margin-top: 8px; text-transform: uppercase;">Angle : Non défini</div>
            <div id="display-date" style="font-size: 0.65rem; color: #a0aec0; margin-top: 5px;">Importé le --/--/----</div>
        </div>
    </div>

    <!-- ZONE DE TRAVAIL : HISTORIQUE + PAPIER -->
    <div style="display: flex; gap: 30px; align-items: flex-start; width: 100%; justify-content: center;">
        
        <!-- COLONNE HISTORIQUE (TIME MACHINE) -->
        <div id="version-timeline" style="width: 180px; position: sticky; top: 10px; display: none;">
            <h4 style="font-size: 0.7rem; color: var(--primary); text-transform: uppercase; letter-spacing: 1px; margin-bottom: 15px; border-bottom: 1px solid #cbd5e0; padding-bottom: 5px;">
                <i data-lucide="history" style="width:12px;"></i> Historique
            </h4>
            <div id="version-list" style="display: flex; flex-direction: column; gap: 10px;">
                <!-- Les versions V1, V2 s'afficheront ici -->
            </div>
            
            <!-- PRÉPARATION BUDGET (CACHE POUR L'INSTANT) -->
            <div id="budget-preview" style="margin-top: 30px; padding: 10px; background: #edf2f7; border-radius: 8px; border: 1px dashed #cbd5e0; opacity: 0.6;">
                <div style="font-size: 0.6rem; font-weight: bold; color: #4a5568;">ESTIMATION BUDGET</div>
                <div style="font-size: 1rem; color: var(--primary); font-weight: 800;">-- €</div>
            </div>
        </div>

        <!-- BLOC ÉDITEUR -->
        <div style="display: flex; flex-direction: column; align-items: center;">
            <div class="editor-toolbar">
                <button class="tool-btn" onclick="document.execCommand('bold')">B</button>
                <button class="tool-btn" onclick="document.execCommand('italic')">I</button>
                <div style="width:1px; background:#e2e8f0; height: 20px;"></div>
                <button class="tool-btn" style="color:var(--accent)" onclick="saveNewVersion()">💾 SAUVEGARDER V2</button>
            </div>

            <div id="paper" class="paper" contenteditable="true">
                <!-- Texte IA -->
            </div>
        </div>
    </div>
</div>

    <!-- DROITE : CHATBOT -->
    <div class="panel-right">
        <div class="chat-history" id="chatHist">
            <div class="msg ai">Système DOC-OS prêt. Veuillez importer un repérage ou remplir manuellement les informations à gauche pour débuter la scénarisation.</div>
        </div>
        <div class="chat-input-zone">
            <textarea id="chatInput" style="background:#2d3748; color:white; height:60px;" placeholder="Modifier une scène..."></textarea>
            <button class="btn btn-gen" style="margin-top:10px; padding:10px;" onclick="refine()">MODIFIER LE SCRIPT</button>
            <button class="btn btn-brain" onclick="saveToBrain()">🔐 MÉMORISER CETTE RÈGLE</button>
        </div>
    </div>
</div>

<!-- MODAL IMPORT -->
<div id="importModal" class="modal">
    <div class="modal-box">
        <h2 style="color:var(--primary); margin-top:0;">Dossiers Importés (Bridge)</h2>
        <p style="font-size:0.85rem; color:#64748b; margin-bottom:20px;">Sélectionnez une région transmise par vos correspondants terrain :</p>
        <div id="import-list">
            <!-- Liste dynamique -->
        </div>
        <button onclick="document.getElementById('importModal').style.display='none'" class="btn" style="background:#edf2f7; color:var(--primary); margin-top:20px;">FERMER</button>
    </div>
</div>

<!-- MODAL TRIPTYQUE -->
<div id="triptyqueModal" class="modal">
    <div style="display:flex; gap:20px;" id="angles-container">
        <!-- Cartes d'angles générées par l'IA -->
    </div>
</div>

<script>
    lucide.createIcons();

    function showLoader(txt) { document.getElementById('loader-text').innerText = txt; document.getElementById('loader').style.display = 'flex'; }
    function hideLoader() { document.getElementById('loader').style.display = 'none'; }
    
    function addChatMsg(role, txt) {
        const div = document.createElement('div'); div.className = `msg ${role}`; div.innerText = txt;
        const hist = document.getElementById('chatHist'); hist.appendChild(div);
        hist.scrollTop = hist.scrollHeight;
    }

    // --- BRIDGE : CHARGEMENT DES DONNÉES ---
    async function openImportModal() {
        document.getElementById('importModal').style.display = 'flex';
        const res = await fetch('/api/projects');
        const projects = await res.json();
        const list = document.getElementById('import-list');
        list.innerHTML = "";
        
        if(projects.length === 0) { list.innerHTML = "<p style='text-align:center; padding:20px;'>Aucun import détecté.</p>"; return; }

        projects.forEach(p => {
            list.innerHTML += `
                <div class="angle-card" onclick="loadImportedData(${p.id})">
                    <div style="font-size:0.7rem; color:var(--accent); font-weight:bold;">${p.date}</div>
                    <h2>${p.title}</h2>
                    <div style="font-size:0.85rem;">Région : ${p.region}</div>
                </div>`;
        });
    }

   async function loadImportedData(id) {
    document.getElementById('importModal').style.display = 'none';
    showLoader("Synchronisation du dossier...");
    
    try {
        const res = await fetch(`/api/projects/${id}`);
        const data = await res.json();
        const raw = data.form_data;

        // 1. MISE À JOUR DU BANDEAU STUDIO
        document.getElementById('project-header').style.display = 'flex';
        document.getElementById('version-timeline').style.display = 'block';
        
        document.getElementById('display-region').innerText = raw.region || "Région inconnue";
        document.getElementById('display-title').innerText = `SCÉNARIO : ${raw.region}`;
        document.getElementById('display-fixer').innerText = `${raw.fixer_prenom || ''} ${raw.fixer_nom || 'Anonyme'}`;
        document.getElementById('display-date').innerText = `Reçu le ${data.date}`;
        
        // Gestion de l'image de la région
        const vignette = document.getElementById('display-vignette');
        vignette.src = raw.image_region || "https://via.placeholder.com/150?text=No+Image";

        // 2. REMPLISSAGE DU FORMULAIRE TECHNIQUE (GAUCHE)
        document.getElementById('ctx').value = `${raw.pays}, ${raw.region}`;
        
        if(raw.gardiens) {
            raw.gardiens.forEach((g, i) => {
                const target = document.getElementById(`g${i+1}`);
                if(target) {
                    target.value = `NOM: ${g.nom}\nMETIER: ${g.fonction}\nTYPOLOGIE: (À analyser)\nSAVOIR: ${g.savoir_transmis || ''}`;
                }
            });
        }
        
        if(raw.episode_data) document.getElementById('evt').value = raw.episode_data.fete || "";

        // 3. INITIALISATION DE LA TIMELINE (V1 par défaut)
        updateTimeline([{id: 1, name: "V1 - Import Original", date: data.date}]);

        addChatMsg('ai', `Projet "${raw.region}" chargé. L'historique des versions est prêt.`);
        lucide.createIcons();
    } catch (e) {
        console.error(e);
        alert("Erreur lors du chargement du dossier.");
    }
    hideLoader();
}

// Fonction pour afficher les versions dans la colonne de gauche
function updateTimeline(versions) {
    const list = document.getElementById('version-list');
    list.innerHTML = "";
    versions.forEach(v => {
        list.innerHTML += `
            <div onclick="restoreVersion(${v.id})" style="padding: 10px; background: white; border: 1px solid #e2e8f0; border-radius: 6px; cursor: pointer; transition: 0.2s; box-shadow: 0 2px 5px rgba(0,0,0,0.05);" onmouseover="this.style.borderColor='var(--accent)'" onmouseout="this.style.borderColor='#e2e8f0'">
                <div style="font-weight: 800; font-size: 0.75rem; color: var(--primary);">V${v.id}</div>
                <div style="font-size: 0.6rem; color: #64748b;">${v.name}</div>
            </div>
        `;
    });
}

    // --- ANALYSE DES 3 ANGLES (TRIPTYQUE) ---
    async function analyzeAngles() {
        showLoader("Analyse des 3 trajectoires...");
        // Simulation d'analyse (À lier à votre route d'IA)
        setTimeout(() => {
            const container = document.getElementById('angles-container');
            container.innerHTML = `
                <div class="modal-box angle-card" onclick="selectAngle('HARMONIE')">
                    <div style="color:var(--accent); font-weight:bold; font-size:0.7rem;">ANGLE A</div>
                    <h2>L'HARMONIE</h2>
                    <p style="font-size:0.85rem; color:#64748b;">Focus Homme vs Nature. Ambiance contemplative, ASMR et respiration.</p>
                    <button class="btn btn-gen" style="font-size:0.8rem;">CHOISIR CETTE VISION</button>
                </div>
                <div class="modal-box angle-card" onclick="selectAngle('RUPTURE')">
                    <div style="color:var(--accent); font-weight:bold; font-size:0.7rem;">ANGLE B</div>
                    <h2>LA RUPTURE</h2>
                    <p style="font-size:0.85rem; color:#64748b;">Focus Homme vs Temps. Urgence, déclin et transmission fragile.</p>
                    <button class="btn btn-gen" style="font-size:0.8rem;">CHOISIR CETTE VISION</button>
                </div>
                <div class="modal-box angle-card" onclick="selectAngle('LIEN')">
                    <div style="color:var(--accent); font-weight:bold; font-size:0.7rem;">ANGLE C</div>
                    <h2>LE LIEN</h2>
                    <p style="font-size:0.85rem; color:#64748b;">Focus Homme vs Société. Parole, marché et identité collective.</p>
                    <button class="btn btn-gen" style="font-size:0.8rem;">CHOISIR CETTE VISION</button>
                </div>
            `;
            document.getElementById('triptyqueModal').style.display = 'flex';
            hideLoader();
        }, 1500);
    }

    async function selectAngle(type) {
        document.getElementById('triptyqueModal').style.display = 'none';
        showLoader(`Rédaction du script : ${type}...`);
        
        const fd = new FormData();
        fd.append('ctx', document.getElementById('ctx').value);
        fd.append('g1', document.getElementById('g1').value);
        fd.append('g2', document.getElementById('g2').value);
        fd.append('g3', document.getElementById('g3').value);
        fd.append('evt', document.getElementById('evt').value);

        const res = await fetch('/api/generate_full', { method: 'POST', body: fd });
        const data = await res.json();
        
        document.getElementById('paper').innerText = data.script.replace(/\*\*/g, '');
        addChatMsg('ai', `Le scénario 52' (Angle ${type}) est prêt.`);
        hideLoader();
    }

    // --- CHATBOT & MÉMOIRE ---
    async function refine() {
        const instr = document.getElementById('chatInput').value;
        if(!instr) return;
        addChatMsg('user', instr);
        showLoader("Le Co-pilote réécrit...");
        const res = await fetch('/api/refine', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ current_script: document.getElementById('paper').innerText, instruction: instr })
        });
        const data = await res.json();
        document.getElementById('paper').innerText = data.script.replace(/\*\*/g, '');
        document.getElementById('chatInput').value = "";
        hideLoader();
    }

    async function saveToBrain() {
        const instr = document.getElementById('chatInput').value;
        await fetch('/api/memorize', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({ rule: instr })
        });
        addChatMsg('ai', "🔐 Règle mémorisée dans le prompt maître.");
    }
</script>
</body>
</html>
