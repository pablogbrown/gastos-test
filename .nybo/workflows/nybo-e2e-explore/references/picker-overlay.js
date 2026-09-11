// e2e-evidence element picker overlay. Injected into every page by picker.mjs.
// A floating toolbar toggles "select mode"; while it is on, hovering outlines
// elements and clicking captures a stable selector via the __e2e_pick binding
// (clicks are swallowed so picking never triggers navigation).
(() => {
  if (window.__e2e_picker_installed) return;
  window.__e2e_picker_installed = true;

  let mode = false;
  let picked = 0;
  let hovered = null;
  let bar, btn, counter;

  const HOVER = '2px dashed #38bdf8';
  const FLASH = '3px solid #22c55e';

  function cssEscape(v) { return (window.CSS && CSS.escape) ? CSS.escape(v) : v.replace(/([^a-zA-Z0-9_-])/g, '\\$1'); }

  function roleOf(el) {
    const explicit = el.getAttribute('role');
    if (explicit) return explicit;
    const tag = el.tagName.toLowerCase();
    if (tag === 'button') return 'button';
    if (tag === 'a' && el.hasAttribute('href')) return 'link';
    if (tag === 'select') return 'combobox';
    if (tag === 'textarea') return 'textbox';
    if (tag === 'input') {
      const t = (el.getAttribute('type') || 'text').toLowerCase();
      if (['submit', 'button', 'reset'].includes(t)) return 'button';
      if (t === 'checkbox') return 'checkbox';
      if (t === 'radio') return 'radio';
      if (['text', 'email', 'password', 'search', 'tel', 'url'].includes(t)) return 'textbox';
    }
    if (/^h[1-6]$/.test(tag)) return 'heading';
    return null;
  }

  function accessibleName(el) {
    const aria = el.getAttribute('aria-label');
    if (aria) return aria.trim();
    if (el.labels && el.labels.length) return el.labels[0].textContent.trim();
    const tag = el.tagName.toLowerCase();
    if (tag === 'input') return (el.getAttribute('value') || el.getAttribute('placeholder') || '').trim();
    return (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 60);
  }

  function cssPath(el) {
    const parts = [];
    let node = el;
    while (node && node.nodeType === 1 && node !== document.body && parts.length < 6) {
      let part = node.tagName.toLowerCase();
      if (node.id) { parts.unshift(`#${cssEscape(node.id)}`); break; }
      const siblings = Array.from(node.parentNode?.children || []).filter((s) => s.tagName === node.tagName);
      if (siblings.length > 1) part += `:nth-of-type(${siblings.indexOf(node) + 1})`;
      parts.unshift(part);
      node = node.parentNode;
    }
    return parts.join(' > ');
  }

  function candidates(el) {
    const out = [];
    const testid = el.getAttribute('data-testid') || el.getAttribute('data-test-id') || el.getAttribute('data-cy');
    if (testid) out.push(`[data-testid="${testid}"]`);
    if (el.id && !/^\d|\d{3,}|^(radix|headlessui|mui|aria)-/i.test(el.id)) out.push(`#${cssEscape(el.id)}`);
    const role = roleOf(el);
    const name = accessibleName(el);
    if (role && name) out.push(`role=${role}[name="${name.replace(/"/g, '\\"')}"]`);
    const nameAttr = el.getAttribute('name');
    if (nameAttr) out.push(`${el.tagName.toLowerCase()}[name="${nameAttr}"]`);
    out.push(cssPath(el));
    return out;
  }

  function describe(el) {
    const c = candidates(el);
    return {
      selector: c[0],
      candidates: c,
      tag: el.tagName.toLowerCase(),
      role: roleOf(el),
      text: (el.textContent || '').trim().replace(/\s+/g, ' ').slice(0, 120),
      attrs: {
        id: el.id || null,
        name: el.getAttribute('name'),
        type: el.getAttribute('type'),
        placeholder: el.getAttribute('placeholder'),
        testid: el.getAttribute('data-testid'),
      },
      url: location.href,
      pickedAt: new Date().toISOString(),
    };
  }

  function setMode(on) {
    mode = on;
    btn.textContent = mode ? 'Select mode: ON' : 'Select mode: OFF';
    btn.style.background = mode ? '#22c55e' : '#1f2a37';
    btn.style.color = mode ? '#052e16' : '#e5e7eb';
    document.body.style.cursor = mode ? 'crosshair' : '';
    if (!mode && hovered) { hovered.style.outline = hovered.__e2e_o || ''; hovered = null; }
  }

  function makeBar() {
    bar = document.createElement('div');
    bar.id = '__e2e_pickbar';
    Object.assign(bar.style, {
      position: 'fixed', right: '16px', bottom: '16px', zIndex: 2147483647,
      display: 'flex', alignItems: 'center', gap: '10px',
      background: '#10161d', color: '#e5e7eb', border: '1px solid #1f2a37',
      borderRadius: '12px', padding: '10px 12px',
      font: '13px system-ui, sans-serif', boxShadow: '0 8px 30px rgba(0,0,0,.45)',
    });
    btn = document.createElement('button');
    Object.assign(btn.style, { border: 'none', borderRadius: '8px', padding: '6px 12px', font: '600 12px system-ui', cursor: 'pointer' });
    btn.addEventListener('click', (e) => { e.stopPropagation(); setMode(!mode); });
    counter = document.createElement('span');
    counter.textContent = '0 picked';
    counter.style.color = '#8b98a9';
    const hint = document.createElement('span');
    hint.textContent = 'e2e·evidence — click elements, then close the browser';
    hint.style.color = '#8b98a9';
    bar.append(btn, counter, hint);
    document.body.appendChild(bar);
    setMode(true);
  }

  document.addEventListener('mouseover', (e) => {
    if (!mode || bar.contains(e.target)) return;
    hovered = e.target;
    hovered.__e2e_o = hovered.style.outline;
    hovered.style.outline = HOVER;
  }, true);

  document.addEventListener('mouseout', (e) => {
    if (e.target === hovered && hovered) { hovered.style.outline = hovered.__e2e_o || ''; hovered = null; }
  }, true);

  document.addEventListener('click', (e) => {
    if (!mode || !bar || bar.contains(e.target)) return;
    e.preventDefault();
    e.stopImmediatePropagation();
    const el = e.target;
    el.style.outline = FLASH;
    setTimeout(() => { el.style.outline = el.__e2e_o || ''; }, 350);
    picked++;
    counter.textContent = `${picked} picked`;
    window.__e2e_pick(describe(el));
  }, true);

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', makeBar);
  else makeBar();
})();
