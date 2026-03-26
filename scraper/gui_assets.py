from __future__ import annotations


GUI_INDEX_HTML = """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>QuickWiki Studio</title>
  <link rel="stylesheet" href="/app.css">
</head>
<body>
  <div class="studio-bg"></div>
  <main class="studio-shell">
    <section class="hero">
      <div>
        <span class="eyebrow">QuickWiki Studio</span>
        <h1>GUI local para crawls mais claros e mais atraentes.</h1>
        <p class="lead">Configure, valide, acompanhe logs e abra o espelho offline em um fluxo visual unico.</p>
        <div class="hero-links">
          <a class="pill-link" href="/manual/index.html" target="_blank" rel="noreferrer">Manual</a>
          <a class="pill-link" href="/project/README.md" target="_blank" rel="noreferrer">README</a>
          <a class="pill-link" href="/project/CHANGELOG.md" target="_blank" rel="noreferrer">Changelog</a>
          <a class="pill-link" href="/project/DOCUMENTACAO_TECNICA.md" target="_blank" rel="noreferrer">Docs Tecnicas</a>
        </div>
      </div>
      <aside class="hero-side">
        <div class="status-card" id="status-card" data-state="ready">
          <small>Estado atual</small>
          <strong id="status-badge">Pronto</strong>
          <span id="status-detail">Nenhum crawl em execucao.</span>
        </div>
        <div class="summary-card">
          <small>Ultimo resumo</small>
          <div class="summary-grid">
            <div><strong id="summary-pages">0</strong><span>Paginas</span></div>
            <div><strong id="summary-assets">0</strong><span>Assets</span></div>
            <div><strong id="summary-failures">0</strong><span>Falhas</span></div>
            <div><strong id="summary-profile">-</strong><span>Perfil</span></div>
          </div>
        </div>
      </aside>
    </section>

    <section class="workflow">
      <article><span>01</span><strong>Validar perfis</strong><p>Confirme os JSONs antes da primeira rodada.</p></article>
      <article><span>02</span><strong>Testar pequeno</strong><p>Use poucas paginas para revisar o fluxo.</p></article>
      <article><span>03</span><strong>Abrir o espelho</strong><p>Use os atalhos para revisar o resultado final.</p></article>
    </section>

    <section class="workspace">
      <section class="panel">
        <div class="panel-head">
          <div><span class="eyebrow">Execucao</span><h2>Configurar novo crawl</h2></div>
          <p>Uma tela pensada para onboarding: segura o suficiente para testar, simples o suficiente para usar sem manual o tempo todo.</p>
        </div>
        <form id="run-form">
          <div class="field-grid">
            <label class="field wide"><span>Perfil</span><select id="site-profile" name="site_profile"></select></label>
            <label class="field wide"><span>Seed URL</span><input id="seed-url" name="seed_url" type="url" placeholder="https://www.tibiawiki.com.br/wiki/Home"></label>
            <label class="field"><span>Pasta de saida</span><input id="output-dir" name="output_dir" type="text" placeholder="output"></label>
            <label class="field"><span>Max. paginas</span><input id="max-pages" name="max_pages" type="number" min="1" placeholder="25"></label>
            <label class="field"><span>Workers</span><input id="workers" name="workers" type="number" min="1" value="8"></label>
            <label class="field"><span>Workers de assets</span><input id="asset-workers" name="asset_workers" type="number" min="1" value="8"></label>
            <label class="field"><span>Rate limit</span><input id="rate-limit" name="rate_limit" type="number" step="0.1" min="0.1" value="2.0"></label>
            <label class="field"><span>Timeout</span><input id="timeout" name="timeout" type="number" step="1" min="3" value="30"></label>
          </div>

          <div class="profile-card">
            <small>Perfil selecionado</small>
            <strong id="profile-title">Auto detectar</strong>
            <p id="profile-description">A GUI pode sugerir o perfil ideal a partir do dominio da seed URL.</p>
            <code id="profile-seed">-</code>
          </div>

          <details class="advanced">
            <summary>Configuracoes avancadas</summary>
            <div class="field-grid">
              <label class="field"><span>Max. retries</span><input id="max-retries" name="max_retries" type="number" min="0" value="4"></label>
              <label class="field"><span>Retry failed passes</span><input id="retry-failed-passes" name="retry_failed_passes" type="number" min="0" value="1"></label>
              <label class="field"><span>Checkpoint</span><input id="checkpoint-every" name="checkpoint_every" type="number" min="1" value="25"></label>
              <label class="field"><span>Bootstrap API</span><select id="api-bootstrap-mode" name="api_bootstrap_mode"><option value="auto">auto</option><option value="always">always</option><option value="off">off</option></select></label>
              <label class="field"><span>Nivel de log</span><select id="log-level" name="log_level"><option value="INFO">INFO</option><option value="DEBUG">DEBUG</option><option value="WARNING">WARNING</option><option value="ERROR">ERROR</option></select></label>
            </div>
            <div class="toggle-row">
              <label><input id="fresh" name="fresh" type="checkbox"> Comecar do zero (--fresh)</label>
              <label><input id="ignore-robots" name="ignore_robots" type="checkbox"> Ignorar robots.txt</label>
              <label><input id="no-source" name="no_source" type="checkbox"> Nao capturar source wiki</label>
            </div>
          </details>

          <div class="action-row">
            <button class="button primary" id="start-run" type="submit">Iniciar Crawl</button>
            <button class="button secondary" id="validate-profiles" type="button">Validar Perfis</button>
            <button class="button ghost" id="stop-run" type="button">Parar Execucao</button>
          </div>
        </form>
      </section>

      <section class="stack">
        <section class="panel">
          <div class="panel-head">
            <div><span class="eyebrow">Acompanhamento</span><h2>Status e atalhos</h2></div>
            <p id="command-line">Nenhum comando ativo.</p>
          </div>
          <div class="shortcut-grid">
            <a class="shortcut" id="mirror-link" href="/mirror/index.html" target="_blank" rel="noreferrer"><strong>Abrir espelho</strong><span>Home offline atual</span></a>
            <a class="shortcut" id="admin-link" href="/mirror/admin/index.html" target="_blank" rel="noreferrer"><strong>Abrir admin</strong><span>Painel do perfil ativo</span></a>
            <a class="shortcut" id="summary-link" href="/mirror/data/indexes/summary.json" target="_blank" rel="noreferrer"><strong>Abrir resumo</strong><span>JSON do ultimo crawl</span></a>
            <a class="shortcut" id="manual-link" href="/manual/index.html" target="_blank" rel="noreferrer"><strong>Abrir manual</strong><span>Guia visual do usuario</span></a>
          </div>
          <div class="info-grid">
            <div class="info-card"><small>PID</small><strong id="run-pid">-</strong></div>
            <div class="info-card"><small>Inicio</small><strong id="run-started">-</strong></div>
            <div class="info-card"><small>Fim</small><strong id="run-finished">-</strong></div>
            <div class="info-card"><small>Exit code</small><strong id="run-exit">-</strong></div>
          </div>
        </section>
        <section class="panel">
          <div class="panel-head">
            <div><span class="eyebrow">Logs</span><h2>Saida ao vivo</h2></div>
            <p>Atualizacao automatica a cada 2 segundos.</p>
          </div>
          <pre id="log-output">Aguardando execucao...</pre>
        </section>
      </section>
    </section>
  </main>
  <div class="toast" id="toast"></div>
  <script src="/app.js"></script>
</body>
</html>
""".strip()


GUI_CSS = """
:root{--bg:#f5ede2;--ink:#201814;--muted:#6d6258;--line:rgba(82,54,33,.12);--panel:rgba(255,251,245,.84);--accent:#ac4a29;--accent-deep:#6d2c17;--teal:#255f61;--ok:#1f6b45;--warn:#8f5811;--shadow:0 22px 50px rgba(75,48,24,.1)}*{box-sizing:border-box}html,body{margin:0;min-height:100%}body{color:var(--ink);background:radial-gradient(circle at top left,rgba(249,214,182,.96),transparent 34%),radial-gradient(circle at top right,rgba(205,232,227,.9),transparent 28%),linear-gradient(180deg,#f7f1e8 0%,var(--bg) 100%);font-family:"Trebuchet MS","Lucida Sans Unicode",sans-serif}.studio-bg{position:fixed;inset:0;background:repeating-linear-gradient(135deg,rgba(92,54,31,.016) 0,rgba(92,54,31,.016) 2px,transparent 2px,transparent 18px);pointer-events:none}.studio-shell{position:relative;max-width:1280px;margin:0 auto;padding:28px 20px 48px}.hero,.workflow article,.panel,.status-card,.summary-card,.shortcut,.info-card,.profile-card,.toast{backdrop-filter:blur(12px);-webkit-backdrop-filter:blur(12px)}.hero{display:grid;grid-template-columns:minmax(0,1.4fr) minmax(320px,.85fr);gap:22px;padding:28px;border:1px solid var(--line);border-radius:28px;background:linear-gradient(180deg,rgba(255,252,247,.92),rgba(249,241,230,.8));box-shadow:var(--shadow)}.hero h1,.panel h2,.workflow strong{font-family:"Palatino Linotype","Book Antiqua",Georgia,serif}.hero h1{margin:12px 0;max-width:11ch;font-size:clamp(2.8rem,5.5vw,4.8rem);line-height:.96;color:var(--accent-deep)}.lead,.panel-head p,.workflow p,.profile-card p,.shortcut span,small{color:var(--muted)}.lead{max-width:62ch;margin:0;line-height:1.72;font-size:1.05rem}.eyebrow{display:inline-flex;align-items:center;padding:7px 11px;border-radius:999px;background:rgba(172,74,41,.1);color:var(--accent);font-size:.78rem;font-weight:800;letter-spacing:.08em;text-transform:uppercase}.hero-links{display:flex;flex-wrap:wrap;gap:10px;margin-top:22px}.pill-link,.shortcut{text-decoration:none}.pill-link{display:inline-flex;align-items:center;min-height:40px;padding:8px 12px;border-radius:12px;border:1px solid rgba(82,54,33,.12);background:rgba(255,249,240,.84);color:var(--accent-deep);font-weight:700}.hero-side{display:grid;gap:14px}.status-card,.summary-card,.panel,.workflow article,.shortcut,.info-card,.profile-card{border:1px solid var(--line);border-radius:22px;background:var(--panel);box-shadow:var(--shadow)}.status-card,.summary-card{padding:18px}.status-card strong,.summary-grid strong,.info-card strong,.profile-card strong,.shortcut strong{display:block;color:var(--accent-deep)}.status-card strong{margin:8px 0 6px;font-size:1.18rem}.status-card[data-state="running"]{border-color:rgba(37,95,97,.24)}.status-card[data-state="running"] strong{color:var(--teal)}.status-card[data-state="success"]{border-color:rgba(31,107,69,.24)}.status-card[data-state="success"] strong{color:var(--ok)}.status-card[data-state="warning"]{border-color:rgba(143,88,17,.24)}.status-card[data-state="warning"] strong{color:var(--warn)}.summary-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:12px;margin-top:12px}.summary-grid strong{font-size:1.25rem}.workflow{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:14px;margin-top:18px}.workflow article{padding:18px}.workflow span{display:inline-flex;width:40px;height:40px;align-items:center;justify-content:center;border-radius:14px;background:rgba(255,248,239,.92);border:1px solid rgba(82,54,33,.12);color:var(--accent);font-weight:900}.workflow strong{display:block;margin:14px 0 8px;font-size:1.25rem;color:var(--accent-deep)}.workflow p{margin:0;line-height:1.58}.workspace{display:grid;grid-template-columns:minmax(0,1.1fr) minmax(360px,.9fr);gap:18px;margin-top:18px}.stack{display:grid;gap:18px}.panel{padding:22px}.panel-head{display:flex;align-items:start;justify-content:space-between;gap:14px;margin-bottom:18px}.panel-head h2{margin:10px 0 0;color:var(--accent-deep);font-size:1.9rem}.panel-head p{margin:6px 0 0;max-width:30ch;line-height:1.6}.field-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:14px}.wide{grid-column:span 2}.field{display:grid;gap:8px}.field span{color:var(--accent-deep);font-weight:700}.field input,.field select{width:100%;min-height:48px;padding:12px 14px;border:1px solid rgba(82,54,33,.12);border-radius:14px;background:rgba(255,253,250,.94);color:var(--ink);font-size:.98rem}.profile-card{display:grid;gap:8px;margin-top:16px;padding:16px 18px;background:linear-gradient(180deg,rgba(255,249,241,.96),rgba(252,245,236,.88))}.profile-card p{margin:0;line-height:1.58}.profile-card code{width:fit-content;padding:6px 10px;border-radius:999px;background:rgba(255,255,255,.76);border:1px solid rgba(82,54,33,.1);color:var(--accent-deep);font-family:Consolas,"Courier New",monospace}.advanced{margin-top:18px;padding:16px;border-radius:18px;border:1px dashed rgba(82,54,33,.18);background:rgba(255,250,243,.58)}.advanced summary{cursor:pointer;color:var(--accent-deep);font-weight:800}.toggle-row{display:grid;gap:12px;margin-top:16px;color:#3e3128}.toggle-row label{display:flex;gap:10px;align-items:center}.action-row{display:flex;flex-wrap:wrap;gap:12px;margin-top:20px}.button{display:inline-flex;align-items:center;justify-content:center;min-height:48px;padding:10px 16px;border:0;border-radius:14px;cursor:pointer;font-weight:800}.button:disabled{opacity:.58;cursor:not-allowed}.primary{background:linear-gradient(135deg,var(--accent) 0%,#c7633d 100%);color:#fff8f3}.secondary{background:linear-gradient(135deg,var(--teal) 0%,#3d7b7d 100%);color:#f3fffe}.ghost{background:rgba(255,248,240,.84);color:var(--accent-deep);border:1px solid rgba(82,54,33,.12)}.shortcut-grid,.info-grid{display:grid;gap:12px}.shortcut-grid{grid-template-columns:repeat(2,minmax(0,1fr))}.shortcut,.info-card{padding:16px}.shortcut span,.info-card small{display:block;margin-top:6px}.info-grid{grid-template-columns:repeat(2,minmax(0,1fr));margin-top:14px}pre{max-height:500px;margin:0;overflow:auto;padding:18px;border-radius:18px;background:linear-gradient(180deg,rgba(35,31,28,.98),rgba(48,38,32,.96));color:#f7efe5;font-family:Consolas,"Courier New",monospace;font-size:.92rem;line-height:1.6}.toast{position:fixed;right:20px;bottom:20px;min-width:260px;max-width:420px;padding:14px 16px;border-radius:16px;border:1px solid rgba(82,54,33,.12);background:rgba(255,252,247,.94);box-shadow:var(--shadow);color:var(--accent-deep);opacity:0;transform:translateY(10px);pointer-events:none;transition:opacity .2s ease,transform .2s ease}.toast.is-visible{opacity:1;transform:translateY(0)}@media (max-width:1040px){.hero,.workspace,.workflow{grid-template-columns:1fr}}@media (max-width:720px){.studio-shell{padding:16px 12px 28px}.hero,.panel,.status-card,.summary-card,.shortcut,.info-card,.profile-card,.workflow article{border-radius:18px}.field-grid,.shortcut-grid,.info-grid{grid-template-columns:1fr}.wide{grid-column:auto}.panel-head{flex-direction:column}.hero h1{font-size:2.7rem}}
""".strip()


GUI_JS = """
const state={refreshTimer:null,lastRunningState:null,profiles:new Map(),lastSeedSuggestion:''};
const els={form:document.getElementById('run-form'),profileSelect:document.getElementById('site-profile'),seedUrl:document.getElementById('seed-url'),outputDir:document.getElementById('output-dir'),maxPages:document.getElementById('max-pages'),workers:document.getElementById('workers'),assetWorkers:document.getElementById('asset-workers'),rateLimit:document.getElementById('rate-limit'),timeout:document.getElementById('timeout'),maxRetries:document.getElementById('max-retries'),retryFailedPasses:document.getElementById('retry-failed-passes'),checkpointEvery:document.getElementById('checkpoint-every'),apiBootstrapMode:document.getElementById('api-bootstrap-mode'),logLevel:document.getElementById('log-level'),fresh:document.getElementById('fresh'),ignoreRobots:document.getElementById('ignore-robots'),noSource:document.getElementById('no-source'),startRun:document.getElementById('start-run'),validateProfiles:document.getElementById('validate-profiles'),stopRun:document.getElementById('stop-run'),logOutput:document.getElementById('log-output'),statusCard:document.getElementById('status-card'),statusBadge:document.getElementById('status-badge'),statusDetail:document.getElementById('status-detail'),commandLine:document.getElementById('command-line'),summaryPages:document.getElementById('summary-pages'),summaryAssets:document.getElementById('summary-assets'),summaryFailures:document.getElementById('summary-failures'),summaryProfile:document.getElementById('summary-profile'),runPid:document.getElementById('run-pid'),runStarted:document.getElementById('run-started'),runFinished:document.getElementById('run-finished'),runExit:document.getElementById('run-exit'),mirrorLink:document.getElementById('mirror-link'),adminLink:document.getElementById('admin-link'),summaryLink:document.getElementById('summary-link'),manualLink:document.getElementById('manual-link'),profileTitle:document.getElementById('profile-title'),profileDescription:document.getElementById('profile-description'),profileSeed:document.getElementById('profile-seed'),toast:document.getElementById('toast')};
function showToast(message){els.toast.textContent=message;els.toast.classList.add('is-visible');clearTimeout(showToast._timer);showToast._timer=setTimeout(()=>els.toast.classList.remove('is-visible'),3200)}
function setProfileOptions(profiles){const current=els.profileSelect.value||'auto';els.profileSelect.innerHTML='';state.profiles.clear();for(const profile of profiles||[]){const option=document.createElement('option');option.value=profile.key;option.textContent=`${profile.label} (${profile.key})`;els.profileSelect.append(option);state.profiles.set(profile.key,{label:profile.label||profile.key,description:profile.description||'',defaultSeedUrl:profile.default_seed_url||''})}els.profileSelect.value=state.profiles.has(current)?current:'auto';syncProfileCard()}
function syncProfileCard(){const profile=state.profiles.get(els.profileSelect.value)||{label:'Auto detectar',description:'A GUI pode sugerir o perfil ideal a partir do dominio da seed URL.',defaultSeedUrl:''};els.profileTitle.textContent=profile.label;els.profileDescription.textContent=profile.description||'Sem descricao adicional para este perfil.';els.profileSeed.textContent=profile.defaultSeedUrl||'-';const currentSeed=els.seedUrl.value.trim();if(profile.defaultSeedUrl&&(!currentSeed||currentSeed===state.lastSeedSuggestion)){els.seedUrl.value=profile.defaultSeedUrl;state.lastSeedSuggestion=profile.defaultSeedUrl}}
function formatDate(value){if(!value)return'-';try{return new Date(value).toLocaleString('pt-BR')}catch{return value}}
function renderLogs(lines){const pre=els.logOutput;const nearBottom=pre.scrollHeight-pre.scrollTop-pre.clientHeight<24;pre.textContent=Array.isArray(lines)&&lines.length?lines.join('\\n'):'Aguardando execucao...';if(nearBottom||pre.scrollTop===0)pre.scrollTop=pre.scrollHeight}
function renderState(payload){setProfileOptions(payload.profiles);if(!els.outputDir.value)els.outputDir.value=payload.defaults.output_dir||'output';if(!els.seedUrl.value){const profile=state.profiles.get(els.profileSelect.value);if(profile?.defaultSeedUrl){els.seedUrl.value=profile.defaultSeedUrl;state.lastSeedSuggestion=profile.defaultSeedUrl}}const run=payload.run||{};const running=Boolean(run.running);const stateName=running?'running':(run.last_exit_code===0?'success':(run.last_exit_code!=null?'warning':'ready'));const label=running?'Em execucao':(run.last_exit_code===0?'Concluido':(run.last_exit_code!=null?'Encerrado com alerta':'Pronto'));const detail=running?'O QuickWiki esta processando um crawl em segundo plano.':(run.last_exit_code!=null?'A ultima execucao terminou. Revise logs e resumo ao lado.':'Nenhum crawl em execucao.');els.statusCard.dataset.state=stateName;els.statusBadge.textContent=label;els.statusDetail.textContent=detail;els.commandLine.textContent=run.command_preview||'Nenhum comando ativo.';els.runPid.textContent=run.pid||'-';els.runStarted.textContent=formatDate(run.started_at);els.runFinished.textContent=formatDate(run.finished_at);els.runExit.textContent=run.last_exit_code??'-';els.startRun.disabled=running;els.stopRun.disabled=!running;const summary=payload.summary||{};els.summaryPages.textContent=summary.pages_saved??0;els.summaryAssets.textContent=summary.assets_saved??0;els.summaryFailures.textContent=summary.failed_pages??0;els.summaryProfile.textContent=summary.site_label||summary.site_profile||'-';const links=payload.links||{};els.mirrorLink.href=links.mirror;els.adminLink.href=links.admin;els.summaryLink.href=links.summary;els.manualLink.href=links.manual;renderLogs(payload.logs);if(state.lastRunningState!==null&&state.lastRunningState!==running)showToast(running?'Execucao iniciada com sucesso.':'Execucao finalizada. Confira o resumo e os logs.');state.lastRunningState=running}
async function fetchState(){const response=await fetch('/api/state',{cache:'no-store'});if(!response.ok)throw new Error('Nao foi possivel carregar o estado da GUI.');renderState(await response.json())}
function getFormPayload(){return{site_profile:els.profileSelect.value,seed_url:els.seedUrl.value.trim(),output_dir:els.outputDir.value.trim(),max_pages:els.maxPages.value.trim(),workers:els.workers.value,asset_workers:els.assetWorkers.value,rate_limit:els.rateLimit.value,timeout:els.timeout.value,max_retries:els.maxRetries.value,retry_failed_passes:els.retryFailedPasses.value,checkpoint_every:els.checkpointEvery.value,api_bootstrap_mode:els.apiBootstrapMode.value,log_level:els.logLevel.value,fresh:els.fresh.checked,ignore_robots:els.ignoreRobots.checked,no_source:els.noSource.checked}}
async function postJson(url,payload){const response=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload||{})});const data=await response.json().catch(()=>({}));if(!response.ok)throw new Error(data.error||'A operacao falhou.');return data}
els.profileSelect.addEventListener('change',()=>syncProfileCard());
els.form.addEventListener('submit',async(event)=>{event.preventDefault();try{const result=await postJson('/api/start-run',getFormPayload());showToast(result.message||'Execucao iniciada.');await fetchState()}catch(error){showToast(error.message)}});
els.validateProfiles.addEventListener('click',async()=>{try{const result=await postJson('/api/validate-profiles',{});showToast(result.message||'Perfis validados.');await fetchState()}catch(error){showToast(error.message)}});
els.stopRun.addEventListener('click',async()=>{try{const result=await postJson('/api/stop-run',{});showToast(result.message||'Sinal de parada enviado.');await fetchState()}catch(error){showToast(error.message)}});
async function boot(){try{await fetchState()}catch(error){showToast(error.message)}clearInterval(state.refreshTimer);state.refreshTimer=setInterval(()=>{fetchState().catch((error)=>showToast(error.message))},2000)}
boot();
""".strip()
