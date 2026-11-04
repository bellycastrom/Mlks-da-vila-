'use strict';
(() => {
  const toggle = document.querySelector('.nav-toggle');
  const sidebar = document.getElementById('sidebar');
  const overlay = document.getElementById('menu-overlay');
  const closeNav = () => {
    document.body.classList.remove('menu-open');
    toggle?.setAttribute('aria-expanded', 'false');
  };
  toggle?.addEventListener('click', () => {
    const active = document.body.classList.toggle('menu-open');
    toggle.setAttribute('aria-expanded', String(active));
  });
  overlay?.addEventListener('click', closeNav);
  sidebar?.querySelectorAll('a').forEach(a => a.addEventListener('click', closeNav));
  document.addEventListener('keydown', e => { if(e.key === 'Escape') closeNav(); });

  const form = document.querySelector('form[data-presenca-form]');
  if (form) {
    const checks = [...form.querySelectorAll('input[name="presentes"]')];
    const count = document.getElementById('presence-counter');
    const update = () => {
      const present = checks.filter(el => el.checked).length;
      if (count) count.textContent = `${present} de ${checks.length} participantes presentes`;
      for (const box of checks) {
        const state = box.closest('tr')?.querySelector('.state-label');
        if (!state) continue;
        state.textContent = box.checked ? 'Presente' : 'Ausente';
        state.classList.toggle('state-present', box.checked);
        state.classList.toggle('state-absent', !box.checked);
      }
    };
    checks.forEach(c => c.addEventListener('change', update));
    update();
    const cancel = form.querySelector('[data-cancel-form]');
    cancel?.addEventListener('click', e => {
      const name = form.querySelector('[name="titulo"]');
      const description = form.querySelector('[name="descricao"]');
      const chosen = checks.some(c => c.checked);
      if ((name?.value.trim() || description?.value.trim() || chosen) && !window.confirm('Cancelar o cadastro? As informações não salvas serão perdidas.')) {
        e.preventDefault();
      }
    });
    form.addEventListener('submit', e => {
      if (!form.reportValidity()) { e.preventDefault(); return; }
      const submit = form.querySelector('button[type="submit"]');
      if (submit) {
        // Não muda o name/value dos checkboxes; só evita o segundo clique.
        submit.disabled = true;
        submit.textContent = 'Salvando...';
      }
    });
  }
  document.querySelectorAll('form[data-confirm]').forEach(form => {
    form.addEventListener('submit', e => {
      if (!window.confirm(form.dataset.confirm || 'Confirma esta operação?')) e.preventDefault();
    });
  });
})();
