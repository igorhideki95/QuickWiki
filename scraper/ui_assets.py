from __future__ import annotations


DEFAULT_THEME = {
    "bg": "#f4efe5",
    "bg_page": "#faf7f1",
    "ink": "#1c1a16",
    "muted": "#62584d",
    "accent": "#8e2f1a",
    "accent_soft": "#f4d9b4",
    "panel": "rgba(255, 252, 246, 0.92)",
    "line": "#dccfbf",
    "chip": "#efe3d4",
    "link": "#174d72",
}


BASE_CSS = """
:root {{
  --bg: {bg};
  --bg-page: {bg_page};
  --ink: {ink};
  --muted: {muted};
  --accent: {accent};
  --accent-soft: {accent_soft};
  --panel: {panel};
  --line: {line};
  --chip: {chip};
  --link: {link};
  --shadow-soft: 0 12px 28px rgba(82, 49, 21, 0.06);
  --shadow-panel: 0 18px 45px rgba(88, 52, 24, 0.08);
}}
* {{ box-sizing: border-box; }}
body {{
  margin: 0;
  color: var(--ink);
  background:
    radial-gradient(circle at top, color-mix(in srgb, var(--accent-soft) 70%, white), transparent 36%),
    linear-gradient(180deg, color-mix(in srgb, var(--bg) 30%, white) 0%, var(--bg) 100%);
  font-family: "Source Sans 3", "Segoe UI", sans-serif;
}}
a {{ color: var(--link); }}
.mirror-shell {{
  max-width: 1180px;
  margin: 0 auto;
  padding: 32px 20px 56px;
}}
.mirror-hero {{
  display: grid;
  gap: 18px;
  padding: 24px;
  border: 1px solid var(--line);
  border-radius: 22px;
  background: var(--panel);
  box-shadow: var(--shadow-panel);
}}
.mirror-eyebrow {{
  display: inline-flex;
  width: fit-content;
  padding: 6px 10px;
  border-radius: 999px;
  background: var(--accent_soft, var(--accent-soft));
  color: var(--accent);
  font-size: 0.85rem;
  font-weight: 700;
  letter-spacing: 0.04em;
  text-transform: uppercase;
}}
.mirror-title {{
  margin: 0;
  font-size: clamp(2rem, 5vw, 3.6rem);
  line-height: 0.98;
  color: var(--accent);
  font-family: "Merriweather", Georgia, serif;
}}
.mirror-summary {{
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 12px;
}}
.mirror-stat,
.mirror-meta,
.mirror-card,
.mirror-content-card,
.mirror-side-card,
.mirror-admin-card {{
  background: rgba(255, 255, 255, 0.78);
  border: 1px solid var(--line);
  box-shadow: var(--shadow-soft);
}}
.mirror-stat {{
  padding: 14px 16px;
  border-radius: 16px;
}}
.mirror-stat strong {{
  display: block;
  font-size: 1.5rem;
  color: var(--accent);
}}
.mirror-controls {{
  display: grid;
  grid-template-columns: minmax(0, 1.8fr) minmax(220px, 0.8fr);
  gap: 14px;
  margin-top: 18px;
}}
.mirror-input,
.mirror-select {{
  width: 100%;
  min-height: 48px;
  padding: 12px 14px;
  border: 1px solid var(--line);
  border-radius: 14px;
  background: #fffdfa;
  color: var(--ink);
  font-size: 1rem;
}}
.mirror-meta-line {{
  margin-top: 10px;
  color: var(--muted);
}}
.mirror-toolbar,
.mirror-links,
.mirror-chips,
.mirror-topbar {{
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}}
.mirror-toolbar {{
  align-items: center;
  justify-content: space-between;
  margin: 22px 0 14px;
}}
.mirror-result-count {{
  color: var(--muted);
  font-weight: 600;
}}
.mirror-links a,
.mirror-topbar a,
.mirror-admin-actions a {{
  color: var(--link);
  text-decoration: none;
  padding: 8px 10px;
  border: 1px solid var(--line);
  border-radius: 999px;
  background: rgba(255, 255, 255, 0.72);
}}
.mirror-results,
.mirror-admin-grid {{
  display: grid;
  gap: 12px;
}}
.mirror-admin-grid {{
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
}}
.mirror-card,
.mirror-content-card,
.mirror-side-card,
.mirror-meta,
.mirror-admin-card {{
  border-radius: 18px;
}}
.mirror-card,
.mirror-admin-card {{
  padding: 18px;
}}
.mirror-card h2,
.mirror-side-card h2,
.mirror-page-title,
.mirror-admin-card h2 {{
  margin: 0 0 8px;
  color: var(--accent);
  font-family: "Merriweather", Georgia, serif;
}}
.mirror-page-title {{
  font-size: clamp(2rem, 4vw, 3rem);
}}
.mirror-excerpt,
.mirror-empty,
.mirror-side-empty,
.mirror-link-list small,
.mirror-admin-code,
.mirror-admin-card small {{
  color: var(--muted);
}}
.mirror-chip {{
  display: inline-flex;
  align-items: center;
  padding: 5px 9px;
  border-radius: 999px;
  background: var(--chip);
  color: #54463a;
  font-size: 0.84rem;
}}
.mirror-page {{
  background: linear-gradient(180deg, color-mix(in srgb, var(--bg-page) 50%, white) 0%, var(--bg-page) 100%);
}}
.mirror-page-shell {{
  max-width: 1080px;
  margin: 0 auto;
  padding: 24px 18px 42px;
}}
.mirror-topbar {{
  align-items: center;
  justify-content: space-between;
  margin-bottom: 14px;
}}
.mirror-meta {{
  display: grid;
  gap: 8px;
  padding: 16px;
  margin-bottom: 18px;
  font-size: 0.96rem;
}}
.mirror-layout {{
  display: grid;
  grid-template-columns: minmax(0, 2.2fr) minmax(280px, 0.95fr);
  gap: 20px;
  align-items: start;
}}
.mirror-content-card {{
  padding: 18px;
}}
.mirror-sidebar {{
  display: grid;
  gap: 14px;
}}
.mirror-side-card {{
  padding: 14px;
}}
.mirror-link-list {{
  display: grid;
  gap: 8px;
  margin: 0;
  padding: 0;
  list-style: none;
}}
.mirror-link-list a {{
  text-decoration: none;
}}
.mirror-page img {{
  max-width: 100%;
  height: auto;
}}
.mirror-page table {{
  border-collapse: collapse;
  overflow-x: auto;
  display: block;
  max-width: 100%;
  background: rgba(255, 255, 255, 0.72);
}}
.mirror-page th,
.mirror-page td {{
  border: 1px solid #d6ccc0;
  padding: 6px 8px;
}}
.mirror-admin-code {{
  display: block;
  padding: 10px 12px;
  border-radius: 14px;
  background: rgba(255,255,255,0.68);
  border: 1px dashed var(--line);
  font-family: Consolas, "Courier New", monospace;
  white-space: pre-wrap;
}}
.mirror-admin-actions {{
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}}
@media (max-width: 920px) {{
  .mirror-layout,
  .mirror-controls {{
    grid-template-columns: 1fr;
  }}
  .mirror-shell,
  .mirror-page-shell {{
    padding-left: 14px;
    padding-right: 14px;
  }}
}}
""".strip()


def build_mirror_css(theme: dict[str, str] | None = None) -> str:
    merged = dict(DEFAULT_THEME)
    if theme:
        merged.update({key: value for key, value in theme.items() if value})
    return BASE_CSS.format(**merged)


MIRROR_INDEX_JS = """
window.QuickWikiApp = {
  bootIndex() {
    const rawEntries = Array.isArray(window.__QUICKWIKI_SEARCH_INDEX__)
      ? window.__QUICKWIKI_SEARCH_INDEX__
      : (Array.isArray(window.__TIBIA_WIKI_SEARCH_INDEX__) ? window.__TIBIA_WIKI_SEARCH_INDEX__ : []);
    const searchInput = document.getElementById('search');
    const categorySelect = document.getElementById('category');
    const resultsNode = document.getElementById('results');
    const countNode = document.getElementById('result-count');
    if (!searchInput || !categorySelect || !resultsNode || !countNode) return;

    const categoryCounts = new Map();
    for (const entry of rawEntries) {
      for (const category of entry.categories || []) {
        categoryCounts.set(category, (categoryCounts.get(category) || 0) + 1);
      }
    }

    for (const category of [...categoryCounts.keys()].sort((a, b) => a.localeCompare(b))) {
      const option = document.createElement('option');
      option.value = category;
      option.textContent = `${category} (${categoryCounts.get(category)})`;
      categorySelect.append(option);
    }

    function score(entry, needle) {
      if (!needle) return 0;
      const haystack = [
        entry.title,
        entry.excerpt,
        ...(entry.categories || []),
        ...(entry.headings || []),
        ...(entry.source_templates || []),
        entry.site_profile || '',
      ].join(' ').toLowerCase();
      if (entry.title.toLowerCase().includes(needle)) return 4;
      if ((entry.categories || []).some((category) => category.toLowerCase().includes(needle))) return 3;
      if ((entry.source_templates || []).some((name) => name.toLowerCase().includes(needle))) return 2;
      return haystack.includes(needle) ? 1 : -1;
    }

    function render() {
      const needle = searchInput.value.trim().toLowerCase();
      const selectedCategory = categorySelect.value;
      let filtered = rawEntries.filter((entry) => {
        if (selectedCategory && !(entry.categories || []).includes(selectedCategory)) {
          return false;
        }
        if (!needle) return true;
        return score(entry, needle) >= 0;
      });

      filtered = filtered
        .map((entry) => [entry, score(entry, needle)])
        .sort((left, right) => {
          if (right[1] !== left[1]) return right[1] - left[1];
          return left[0].title.localeCompare(right[0].title);
        })
        .map(([entry]) => entry);

      const visible = needle || selectedCategory ? filtered.slice(0, 250) : filtered.slice(0, 120);
      countNode.textContent = `${filtered.length} resultado(s)${visible.length < filtered.length ? ` · exibindo os primeiros ${visible.length}` : ''}`;

      if (!visible.length) {
        resultsNode.innerHTML = '<div class="mirror-empty">Nenhuma página corresponde aos filtros atuais.</div>';
        return;
      }

      resultsNode.innerHTML = visible.map((entry) => {
        const chips = [
          entry.site_profile || 'site',
          `${entry.word_count || 0} palavras`,
          `${entry.reading_time_minutes || 0} min`,
          `${entry.images_count || 0} imagens`,
          `${entry.wikitext_characters || 0} chars source`,
          `${entry.fetch_source || 'unknown'}`,
          ...(entry.categories || []).slice(0, 3),
          ...(entry.source_templates || []).slice(0, 2),
        ].map((value) => `<span class="mirror-chip">${value}</span>`).join('');

        return `
          <article class="mirror-card">
            <h2><a href="${entry.html_path}">${entry.title}</a></h2>
            <p class="mirror-excerpt">${entry.excerpt || 'Sem resumo disponível.'}</p>
            <div class="mirror-chips">${chips}</div>
          </article>
        `;
      }).join('');
    }

    searchInput.addEventListener('input', render);
    categorySelect.addEventListener('change', render);
    render();
  },
};
window.TibiaMirrorApp = window.QuickWikiApp;
""".strip()
