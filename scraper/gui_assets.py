from __future__ import annotations


GUI_INDEX_HTML = """
<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>QuickWiki Studio</title>
    <link rel="stylesheet" href="/app.css">
  </head>
  <body>
    <main class="studio-shell">
      <section class="studio-hero">
        <div>
          <span class="studio-eyebrow">QuickWiki Studio</span>
          <h1>Monte um espelho offline sem misterio.</h1>
          <p class="studio-lead">
            Escolha uma wiki, faca um teste pequeno e acompanhe tudo em um painel local feito
            para ficar claro do inicio ao fim.
          </p>
        </div>
        <div class="studio-hero-meta">
          <div class="studio-stat">
            <strong id="product-version">-</strong>
            <span>Versao publica</span>
          </div>
          <div class="studio-stat">
            <strong id="platform-label">-</strong>
            <span>Plataforma principal</span>
          </div>
          <div class="studio-stat">
            <strong id="support-scope">-</strong>
            <span>Escopo de perfis</span>
          </div>
        </div>
      </section>

      <section class="studio-grid">
        <section class="studio-card">
          <header class="studio-card-head">
            <div>
              <h2>Comece por aqui</h2>
              <p>Preencha o essencial e deixe o resto no padrao para um primeiro teste seguro.</p>
            </div>
            <span class="studio-badge neutral" id="status-badge">Parado</span>
          </header>

          <div class="studio-field-grid">
            <label class="studio-field">
              <span>Perfil da wiki</span>
              <select id="site-profile"></select>
            </label>
            <label class="studio-field">
              <span>Link inicial</span>
              <input id="seed-url" type="url" placeholder="https://exemplo.com/wiki/Pagina_Inicial">
            </label>
            <label class="studio-field">
              <span>Pasta onde salvar</span>
              <input id="output-dir" type="text" placeholder="output">
            </label>
            <label class="studio-field">
              <span>Limite de paginas</span>
              <input id="max-pages" type="number" min="1" placeholder="25">
            </label>
            <label class="studio-field">
              <span>Processamento paralelo</span>
              <input id="workers" type="number" min="1" value="8">
            </label>
            <label class="studio-field">
              <span>Downloads por pagina</span>
              <input id="asset-workers" type="number" min="1" value="8">
            </label>
            <label class="studio-field">
              <span>Ritmo de acesso</span>
              <input id="rate-limit" type="number" min="0.1" step="0.1" value="2.0">
            </label>
            <label class="studio-field">
              <span>Tempo limite</span>
              <input id="timeout" type="number" min="3" step="1" value="30">
            </label>
          </div>

          <details class="studio-advanced">
            <summary>Mais opcoes</summary>
            <div class="studio-field-grid advanced-grid">
              <label class="studio-field">
                <span>Novas tentativas</span>
                <input id="max-retries" type="number" min="0" value="4">
              </label>
              <label class="studio-field">
                <span>Rodadas extras</span>
                <input id="retry-failed-passes" type="number" min="0" value="1">
              </label>
              <label class="studio-field">
                <span>Salvar progresso a cada</span>
                <input id="checkpoint-every" type="number" min="1" value="25">
              </label>
              <label class="studio-field">
                <span>Descoberta inicial</span>
                <select id="api-bootstrap-mode">
                  <option value="auto">Automatica</option>
                  <option value="always">Sempre tentar</option>
                  <option value="off">Desligada</option>
                </select>
              </label>
              <label class="studio-field">
                <span>Detalhe das mensagens</span>
                <select id="log-level">
                  <option value="INFO">INFO</option>
                  <option value="DEBUG">DEBUG</option>
                  <option value="WARNING">WARNING</option>
                  <option value="ERROR">ERROR</option>
                </select>
              </label>
            </div>
            <div class="studio-switches">
              <label><input id="fresh" type="checkbox"> Comecar do zero</label>
              <label><input id="ignore-robots" type="checkbox"> Ignorar robots.txt</label>
              <label><input id="no-source" type="checkbox"> Nao salvar o codigo-fonte da wiki</label>
            </div>
          </details>

          <div class="studio-actions">
            <button id="start-run" class="primary">Iniciar espelho</button>
            <button id="validate-profiles">Revisar perfis</button>
            <button id="stop-run" class="danger">Parar agora</button>
          </div>

          <div class="studio-subtle" id="status-detail">Aguardando a primeira execucao.</div>
          <code class="studio-command" id="command-line">O comando aparece aqui quando uma rodada comeca.</code>
        </section>

        <section class="studio-card">
          <header class="studio-card-head">
            <div>
              <h2>Perfil escolhido</h2>
              <p>Use este painel para confirmar rapidamente se voce esta apontando para a wiki certa.</p>
            </div>
          </header>
          <div class="studio-profile-box">
            <h3 id="profile-title">Escolha um perfil</h3>
            <p id="profile-description">As orientacoes do perfil aparecem aqui.</p>
            <div class="studio-inline-pair">
              <span class="studio-inline-label">Pagina inicial sugerida</span>
              <code id="profile-seed">-</code>
            </div>
            <div class="studio-inline-pair">
              <span class="studio-inline-label">Entrypoint principal</span>
              <code id="entrypoint-main">quickwiki</code>
            </div>
            <div class="studio-inline-pair">
              <span class="studio-inline-label">Saida padrao</span>
              <code id="default-output">output</code>
            </div>
          </div>
          <div class="studio-link-grid">
            <a id="mirror-link" href="#" target="_blank" rel="noreferrer">Abrir espelho</a>
            <a id="admin-link" href="#" target="_blank" rel="noreferrer">Area tecnica</a>
            <a id="summary-link" href="#" target="_blank" rel="noreferrer">Resumo da execucao</a>
            <a id="report-link" href="#" target="_blank" rel="noreferrer">Detalhes da execucao</a>
            <a id="runtime-link" href="#" target="_blank" rel="noreferrer">Status da execucao</a>
            <a id="manual-link" href="#" target="_blank" rel="noreferrer">Manual do usuario</a>
          </div>
        </section>

        <section class="studio-card">
          <header class="studio-card-head">
            <div>
              <h2>Resumo rapido</h2>
              <p>Numeros principais da ultima rodada salva nesta pasta.</p>
            </div>
          </header>
          <div class="studio-mini-grid">
            <div class="studio-metric"><strong id="summary-pages">0</strong><span>Paginas salvas</span></div>
            <div class="studio-metric"><strong id="summary-assets">0</strong><span>Arquivos salvos</span></div>
            <div class="studio-metric"><strong id="summary-failures">0</strong><span>Pendencias</span></div>
            <div class="studio-metric"><strong id="summary-profile">-</strong><span>Perfil em uso</span></div>
            <div class="studio-metric"><strong id="summary-health">-</strong><span>Saude da rodada</span></div>
          </div>
          <div class="studio-run-grid">
            <div><span class="studio-inline-label">PID</span><strong id="run-pid">-</strong></div>
            <div><span class="studio-inline-label">Inicio</span><strong id="run-started">-</strong></div>
            <div><span class="studio-inline-label">Fim</span><strong id="run-finished">-</strong></div>
            <div><span class="studio-inline-label">Resultado</span><strong id="run-exit">-</strong></div>
          </div>
        </section>
      </section>

      <section class="studio-grid lower">
        <section class="studio-card">
          <header class="studio-card-head">
            <div>
              <h2 id="runtime-headline">Aguardando atividade</h2>
              <p id="runtime-message">Quando o espelho rodar, esta area mostra a fase atual e os sinais mais importantes.</p>
            </div>
          </header>
          <div class="studio-mini-grid">
            <div class="studio-metric"><strong id="runtime-phase">Parado</strong><span>Fase atual</span></div>
            <div class="studio-metric"><strong id="runtime-pages-saved">0</strong><span>Paginas salvas</span></div>
            <div class="studio-metric"><strong id="runtime-pages-attempted">0</strong><span>Paginas tentadas</span></div>
            <div class="studio-metric"><strong id="runtime-pending">0</strong><span>Aguardando</span></div>
            <div class="studio-metric"><strong id="runtime-failures">0</strong><span>Falhas</span></div>
            <div class="studio-metric"><strong id="runtime-sources">0</strong><span>Paginas com codigo-fonte</span></div>
            <div class="studio-metric"><strong id="runtime-rate">0</strong><span>Ritmo configurado</span></div>
            <div class="studio-metric"><strong id="runtime-updated">-</strong><span>Ultima atualizacao</span></div>
          </div>
          <div class="studio-note-box">
            <strong>Observacoes</strong>
            <p id="runtime-notes">Sem observacoes por enquanto.</p>
          </div>
        </section>

        <section class="studio-card">
          <header class="studio-card-head">
            <div>
              <h2>Painel ao vivo</h2>
              <p>Atualizacao automatica a cada 2 segundos, com niveis destacados por cor.</p>
            </div>
          </header>
          <div class="log-output" id="log-output">
            <div class="log-empty">As mensagens da execucao aparecerao aqui.</div>
          </div>
        </section>
      </section>
    </main>

    <div class="toast" id="toast" hidden></div>
    <script src="/app.js"></script>
  </body>
</html>
""".strip()


GUI_CSS = """
:root {
  --bg: #f4eee4;
  --bg-soft: #fbf8f2;
  --panel: rgba(255, 252, 248, 0.94);
  --line: rgba(116, 77, 56, 0.16);
  --ink: #2f221b;
  --muted: #6a584d;
  --accent: #8e2f1a;
  --accent-soft: #f2d2bb;
  --link: #174d72;
  --good: #1f7a5c;
  --warn: #a56609;
  --bad: #a12d2d;
  --shadow: 0 18px 42px rgba(79, 53, 37, 0.1);
}
* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at top, rgba(255, 255, 255, 0.85), transparent 42%),
    linear-gradient(180deg, #f7f0e6 0%, #eef3f1 100%);
  color: var(--ink);
  font: 16px/1.55 "Segoe UI", "Source Sans 3", sans-serif;
}
a { color: var(--link); }
button, input, select {
  font: inherit;
}
.studio-shell {
  max-width: 1360px;
  margin: 0 auto;
  padding: 28px 20px 56px;
}
.studio-hero,
.studio-card {
  background: var(--panel);
  border: 1px solid var(--line);
  border-radius: 24px;
  box-shadow: var(--shadow);
}
.studio-hero {
  display: grid;
  grid-template-columns: minmax(0, 2fr) minmax(260px, 1fr);
  gap: 18px;
  padding: 26px;
}
.studio-eyebrow {
  display: inline-flex;
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--accent-soft);
  color: var(--accent);
  font-size: 0.82rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}
.studio-hero h1 {
  margin: 10px 0 12px;
  font: 700 clamp(2rem, 5vw, 3.8rem)/0.98 Georgia, serif;
  color: var(--accent);
}
.studio-lead,
.studio-card-head p,
.studio-subtle,
.studio-note-box p {
  color: var(--muted);
}
.studio-hero-meta,
.studio-mini-grid,
.studio-field-grid,
.studio-run-grid,
.studio-link-grid {
  display: grid;
  gap: 12px;
}
.studio-hero-meta {
  align-content: start;
}
.studio-grid {
  display: grid;
  grid-template-columns: 1.55fr 1fr 0.95fr;
  gap: 16px;
  margin-top: 18px;
}
.studio-grid.lower {
  grid-template-columns: 1.15fr 1fr;
}
.studio-card {
  padding: 20px;
}
.studio-card-head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 16px;
  margin-bottom: 16px;
}
.studio-card h2,
.studio-profile-box h3 {
  margin: 0 0 8px;
  color: var(--accent);
  font-family: Georgia, serif;
}
.studio-badge,
.log-badge {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  min-width: 86px;
  padding: 6px 10px;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 700;
  letter-spacing: 0.02em;
  text-transform: uppercase;
}
.studio-badge.neutral,
.log-badge.info {
  background: rgba(23, 77, 114, 0.12);
  color: var(--link);
}
.studio-badge.success,
.log-badge.success {
  background: rgba(31, 122, 92, 0.14);
  color: var(--good);
}
.studio-badge.warning,
.log-badge.warning {
  background: rgba(165, 102, 9, 0.15);
  color: var(--warn);
}
.studio-badge.error,
.log-badge.error {
  background: rgba(161, 45, 45, 0.14);
  color: var(--bad);
}
.studio-stat,
.studio-metric,
.studio-profile-box,
.studio-note-box,
.log-line {
  background: rgba(255, 255, 255, 0.74);
  border: 1px solid var(--line);
  border-radius: 18px;
}
.studio-stat,
.studio-metric {
  padding: 14px 16px;
}
.studio-stat strong,
.studio-metric strong {
  display: block;
  font-size: 1.3rem;
  color: var(--accent);
}
.studio-field-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
}
.studio-field {
  display: grid;
  gap: 6px;
}
.studio-field span,
.studio-inline-label {
  color: var(--muted);
  font-size: 0.92rem;
  font-weight: 600;
}
.studio-field input,
.studio-field select {
  min-height: 48px;
  width: 100%;
  padding: 12px 14px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: var(--bg-soft);
  color: var(--ink);
}
.studio-advanced {
  margin-top: 16px;
  padding-top: 14px;
  border-top: 1px dashed var(--line);
}
.studio-advanced summary {
  cursor: pointer;
  font-weight: 700;
  color: var(--accent);
}
.advanced-grid {
  margin-top: 14px;
}
.studio-switches {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 16px;
  color: var(--muted);
}
.studio-actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  margin: 18px 0 12px;
}
.studio-actions button {
  min-height: 46px;
  padding: 0 16px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: rgba(255, 255, 255, 0.88);
  color: var(--ink);
  cursor: pointer;
}
.studio-actions .primary {
  background: var(--accent);
  color: #fff7f2;
  border-color: rgba(0, 0, 0, 0.04);
}
.studio-actions .danger {
  background: rgba(161, 45, 45, 0.12);
  color: var(--bad);
}
.studio-command {
  display: block;
  padding: 12px 14px;
  border-radius: 14px;
  border: 1px dashed var(--line);
  background: rgba(255, 255, 255, 0.66);
  color: var(--muted);
  white-space: pre-wrap;
  word-break: break-word;
}
.studio-profile-box,
.studio-note-box {
  padding: 16px;
}
.studio-inline-pair {
  display: grid;
  gap: 4px;
  margin-top: 12px;
}
.studio-inline-pair code {
  overflow-wrap: anywhere;
}
.studio-link-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 14px;
}
.studio-link-grid a {
  display: block;
  padding: 11px 12px;
  border-radius: 14px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.7);
  text-decoration: none;
}
.studio-run-grid {
  grid-template-columns: repeat(2, minmax(0, 1fr));
  margin-top: 16px;
}
.studio-run-grid > div {
  padding: 12px 14px;
  border-radius: 16px;
  border: 1px solid var(--line);
  background: rgba(255, 255, 255, 0.7);
}
.log-output {
  display: grid;
  gap: 10px;
  max-height: 680px;
  overflow: auto;
}
.log-line {
  display: grid;
  grid-template-columns: auto auto 1fr;
  gap: 10px;
  padding: 12px 14px;
  align-items: start;
}
.log-time {
  color: var(--muted);
  font-weight: 600;
  white-space: nowrap;
}
.log-text {
  min-width: 0;
  overflow-wrap: anywhere;
}
.log-empty {
  padding: 18px;
  border-radius: 18px;
  border: 1px dashed var(--line);
  color: var(--muted);
  background: rgba(255, 255, 255, 0.58);
}
.toast {
  position: fixed;
  right: 18px;
  bottom: 18px;
  max-width: 420px;
  padding: 14px 16px;
  border-radius: 18px;
  border: 1px solid var(--line);
  background: rgba(255, 252, 248, 0.98);
  box-shadow: 0 18px 40px rgba(79, 53, 37, 0.2);
  color: var(--ink);
}
.toast.success { border-color: rgba(31, 122, 92, 0.24); }
.toast.warning { border-color: rgba(165, 102, 9, 0.28); }
.toast.error { border-color: rgba(161, 45, 45, 0.28); }
.toast strong { display: block; margin-bottom: 4px; }
.toast small { display: block; color: var(--muted); margin-top: 6px; }
@media (max-width: 1120px) {
  .studio-grid,
  .studio-grid.lower,
  .studio-hero {
    grid-template-columns: 1fr;
  }
}
@media (max-width: 760px) {
  .studio-shell {
    padding-left: 14px;
    padding-right: 14px;
  }
  .studio-field-grid,
  .studio-link-grid,
  .studio-run-grid {
    grid-template-columns: 1fr;
  }
  .log-line {
    grid-template-columns: 1fr;
  }
}
""".strip()


GUI_JS = """
(() => {
  const state = {
    profiles: [],
    selectedProfile: 'auto',
    timer: null,
  };

  const ids = [
    'site-profile', 'seed-url', 'output-dir', 'max-pages', 'workers', 'asset-workers',
    'rate-limit', 'timeout', 'max-retries', 'retry-failed-passes', 'checkpoint-every',
    'api-bootstrap-mode', 'log-level', 'fresh', 'ignore-robots', 'no-source', 'start-run',
    'validate-profiles', 'stop-run', 'status-badge', 'status-detail', 'command-line',
    'summary-pages', 'summary-assets', 'summary-failures', 'summary-profile', 'summary-health',
    'run-pid', 'run-started', 'run-finished', 'run-exit', 'mirror-link', 'admin-link',
    'summary-link', 'report-link', 'runtime-link', 'manual-link', 'profile-title',
    'profile-description', 'profile-seed', 'runtime-headline', 'runtime-phase',
    'runtime-pages-saved', 'runtime-pages-attempted', 'runtime-pending', 'runtime-failures',
    'runtime-sources', 'runtime-rate', 'runtime-updated', 'runtime-message', 'runtime-notes',
    'toast', 'product-version', 'support-scope', 'entrypoint-main', 'platform-label',
    'default-output', 'log-output'
  ];

  const ui = Object.fromEntries(ids.map((id) => [id, document.getElementById(id)]));

  function escapeHtml(value) {
    return String(value ?? '')
      .replaceAll('&', '&amp;')
      .replaceAll('<', '&lt;')
      .replaceAll('>', '&gt;')
      .replaceAll('"', '&quot;');
  }

  function text(id, value, fallback = '-') {
    if (ui[id]) ui[id].textContent = value === undefined || value === null || value === '' ? fallback : String(value);
  }

  function href(id, value) {
    if (!ui[id]) return;
    const disabled = !value;
    ui[id].href = disabled ? '#' : value;
    ui[id].ariaDisabled = disabled ? 'true' : 'false';
    ui[id].tabIndex = disabled ? -1 : 0;
    ui[id].style.opacity = disabled ? '0.45' : '1';
    ui[id].style.pointerEvents = disabled ? 'none' : 'auto';
  }

  function humanizePhase(value) {
    const map = {
      starting: 'Preparando',
      bootstrapping: 'Descoberta inicial',
      crawling: 'Copiando paginas',
      retrying: 'Tentando novamente',
      finalizing: 'Organizando a saida',
      completed: 'Concluido',
      failed: 'Interrompido',
      idle: 'Parado',
    };
    return map[String(value || '').toLowerCase()] || (value || 'Parado');
  }

  function humanizeHealth(value) {
    const map = {
      ok: 'Tudo certo',
      warning: 'Atencao',
      error: 'Precisa de revisao',
    };
    return map[String(value || '').toLowerCase()] || (value || '-');
  }

  function toastClass(level) {
    const normalized = String(level || 'info').toLowerCase();
    if (normalized === 'success') return 'success';
    if (normalized === 'warning') return 'warning';
    if (normalized === 'error') return 'error';
    return 'neutral';
  }

  function showToast(payload) {
    if (!ui.toast) return;
    const message = typeof payload === 'string' ? payload : (payload?.message || payload?.error || 'Atualizacao concluida.');
    const hint = typeof payload === 'object' ? (payload?.hint || '') : '';
    const details = typeof payload === 'object' ? (payload?.details || '') : '';
    ui.toast.className = `toast ${toastClass(payload?.level)}`;
    ui.toast.innerHTML = `<strong>${escapeHtml(message)}</strong>${hint ? `<div>${escapeHtml(hint)}</div>` : ''}${details ? `<small>${escapeHtml(details)}</small>` : ''}`;
    ui.toast.hidden = false;
    window.clearTimeout(ui.toastTimer);
    ui.toastTimer = window.setTimeout(() => { ui.toast.hidden = true; }, 5000);
  }

  function selectedProfileObject() {
    return state.profiles.find((profile) => profile.key === ui['site-profile']?.value) || state.profiles[0] || null;
  }

  function fillProfiles(profiles, keepSelection = true) {
    if (!ui['site-profile']) return;
    const previous = keepSelection ? ui['site-profile'].value : '';
    ui['site-profile'].innerHTML = '';
    for (const profile of profiles) {
      const option = document.createElement('option');
      option.value = profile.key;
      option.textContent = `${profile.label} (${profile.key})`;
      ui['site-profile'].append(option);
    }
    const nextValue = profiles.some((profile) => profile.key === previous) ? previous : (profiles[0]?.key || 'auto');
    ui['site-profile'].value = nextValue;
    state.selectedProfile = nextValue;
    updateProfilePanel();
  }

  function updateProfilePanel() {
    const profile = selectedProfileObject();
    if (!profile) {
      text('profile-title', 'Escolha um perfil');
      text('profile-description', 'As orientacoes do perfil aparecem aqui.');
      text('profile-seed', '-');
      return;
    }

    text('profile-title', profile.label);
    text('profile-description', profile.description || 'Sem descricao adicional.');
    text('profile-seed', profile.default_seed_url || '-');
    if (ui['seed-url'] && !ui['seed-url'].value && profile.default_seed_url) {
      ui['seed-url'].value = profile.default_seed_url;
    }
  }

  function collectPayload() {
    return {
      site_profile: ui['site-profile']?.value || 'auto',
      seed_url: ui['seed-url']?.value || '',
      output_dir: ui['output-dir']?.value || 'output',
      max_pages: ui['max-pages']?.value || '',
      workers: ui['workers']?.value || '8',
      asset_workers: ui['asset-workers']?.value || '8',
      rate_limit: ui['rate-limit']?.value || '2.0',
      timeout: ui['timeout']?.value || '30',
      max_retries: ui['max-retries']?.value || '4',
      retry_failed_passes: ui['retry-failed-passes']?.value || '1',
      checkpoint_every: ui['checkpoint-every']?.value || '25',
      api_bootstrap_mode: ui['api-bootstrap-mode']?.value || 'auto',
      log_level: ui['log-level']?.value || 'INFO',
      fresh: !!ui['fresh']?.checked,
      ignore_robots: !!ui['ignore-robots']?.checked,
      no_source: !!ui['no-source']?.checked,
    };
  }

  async function postJson(url, payload = {}) {
    const response = await fetch(url, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });
    const data = await response.json().catch(() => ({}));
    if (!response.ok) {
      throw data;
    }
    return data;
  }

  function renderRun(run) {
    const running = !!run?.running;
    const badge = ui['status-badge'];
    if (badge) {
      badge.textContent = running ? 'Em andamento' : 'Parado';
      badge.className = `studio-badge ${running ? 'success' : 'neutral'}`;
    }
    text('status-detail', running
      ? 'Execucao iniciada. As mensagens ja estao aparecendo abaixo.'
      : 'Execucao encerrada. Agora vale revisar o resumo e os detalhes da rodada.');
    text('command-line', run?.command_preview || 'O comando aparece aqui quando uma rodada comeca.');
    text('run-pid', run?.pid || '-');
    text('run-started', run?.started_at || '-');
    text('run-finished', run?.finished_at || '-');
    text('run-exit', run?.last_exit_code ?? '-');
  }

  function renderSummary(summary, report) {
    text('summary-pages', summary?.pages_saved ?? 0, '0');
    text('summary-assets', summary?.assets_saved ?? 0, '0');
    text('summary-failures', summary?.failed_pages ?? 0, '0');
    text('summary-profile', summary?.site_label || summary?.site_profile || '-', '-');
    text('summary-health', humanizeHealth(report?.health?.status || ''), '-');
  }

  function renderRuntime(runtime) {
    const stats = runtime?.stats || {};
    const queue = runtime?.queue || {};
    const notes = runtime?.health?.notes || runtime?.health?.warnings || [];
    const running = !!runtime?.running;
    text('runtime-headline', running ? 'Execucao em andamento' : 'Ultima atividade conhecida');
    text('runtime-phase', humanizePhase(runtime?.phase || 'idle'));
    text('runtime-pages-saved', stats?.pages_saved ?? 0, '0');
    text('runtime-pages-attempted', stats?.pages_attempted ?? 0, '0');
    text('runtime-pending', queue?.pending ?? 0, '0');
    text('runtime-failures', stats?.pages_failed ?? 0, '0');
    text('runtime-sources', stats?.source_pages_captured ?? 0, '0');
    text('runtime-rate', runtime?.run_config?.rate_limit_per_sec ?? '-', '-');
    text('runtime-updated', runtime?.updated_at || runtime?.generated_at || '-');
    text('runtime-message', running
      ? 'O QuickWiki esta atualizando esta area automaticamente.'
      : 'Quando o espelho rodar, esta area mostra a fase atual e os sinais mais importantes.');
    text('runtime-notes', Array.isArray(notes) && notes.length ? notes.join(' | ') : 'Sem observacoes por enquanto.');
  }

  function levelClass(level) {
    const normalized = String(level || '').toLowerCase();
    if (normalized === 'warning') return 'warning';
    if (normalized === 'error' || normalized === 'critical') return 'error';
    if (normalized === 'success') return 'success';
    return 'info';
  }

  function renderLogs(entries, rawLines) {
    const node = ui['log-output'];
    if (!node) return;
    const safeEntries = Array.isArray(entries) && entries.length
      ? entries
      : (Array.isArray(rawLines) ? rawLines.map((line) => ({ time: '', level: '', label: 'Texto', message: line })) : []);

    if (!safeEntries.length) {
      node.innerHTML = '<div class="log-empty">As mensagens da execucao aparecerao aqui.</div>';
      return;
    }

    node.innerHTML = safeEntries.slice(-80).reverse().map((entry) => {
      const level = String(entry.level || entry.label || 'INFO').toUpperCase();
      const badgeClass = levelClass(level);
      const time = entry.time || '--:--:--';
      const label = entry.label || level;
      const message = entry.message || entry.raw || 'Sem mensagem adicional.';
      return `
        <article class="log-line">
          <div class="log-time">${escapeHtml(time)}</div>
          <div class="log-badge ${badgeClass}">${escapeHtml(label)}</div>
          <div class="log-text">${escapeHtml(message)}</div>
        </article>
      `;
    }).join('');
  }

  function renderLinks(links) {
    href('mirror-link', links?.mirror || '');
    href('admin-link', links?.admin || '');
    href('summary-link', links?.summary || '');
    href('report-link', links?.report || '');
    href('runtime-link', links?.runtime || '');
    href('manual-link', links?.manual || '');
  }

  function renderProduct(product, defaults) {
    text('product-version', product?.version || '-');
    text('platform-label', product?.primary_operator_platform || '-');
    text('support-scope', product?.supported_profile_keys?.length || 0, '0');
    text('entrypoint-main', product?.canonical_entrypoint || 'quickwiki');
    text('default-output', defaults?.output_dir || 'output');
    if (ui['output-dir'] && !ui['output-dir'].value && defaults?.output_dir) {
      ui['output-dir'].value = defaults.output_dir;
    }
  }

  function renderState(payload) {
    state.profiles = Array.isArray(payload?.profiles) ? payload.profiles : [];
    if (state.profiles.length) fillProfiles(state.profiles, true);
    renderProduct(payload?.product || {}, payload?.defaults || {});
    renderRun(payload?.run || {});
    renderSummary(payload?.summary || {}, payload?.report || {});
    renderRuntime(payload?.runtime || {});
    renderLinks(payload?.links || {});
    renderLogs(payload?.log_entries || [], payload?.logs || []);
  }

  async function refreshState() {
    const response = await fetch('/api/state');
    const payload = await response.json();
    renderState(payload);
  }

  async function validateProfiles() {
    try {
      const payload = await postJson('/api/validate-profiles');
      showToast(payload);
      if (Array.isArray(payload?.profiles)) {
        state.profiles = payload.profiles;
        fillProfiles(payload.profiles, true);
      }
      await refreshState();
    } catch (errorPayload) {
      showToast(errorPayload);
    }
  }

  async function startRun() {
    try {
      const payload = await postJson('/api/start-run', collectPayload());
      showToast(payload);
      await refreshState();
    } catch (errorPayload) {
      showToast(errorPayload);
    }
  }

  async function stopRun() {
    try {
      const payload = await postJson('/api/stop-run');
      showToast(payload);
      await refreshState();
    } catch (errorPayload) {
      showToast(errorPayload);
    }
  }

  ui['site-profile']?.addEventListener('change', () => {
    state.selectedProfile = ui['site-profile'].value;
    updateProfilePanel();
  });
  ui['validate-profiles']?.addEventListener('click', validateProfiles);
  ui['start-run']?.addEventListener('click', startRun);
  ui['stop-run']?.addEventListener('click', stopRun);

  refreshState().catch((error) => {
    showToast({
      level: 'error',
      message: 'Nao foi possivel carregar o painel agora.',
      details: error instanceof Error ? error.message : String(error),
      hint: 'Atualize a pagina e tente novamente.',
    });
  });

  state.timer = window.setInterval(() => {
    refreshState().catch(() => {});
  }, 2000);
})();
""".strip()
