"""Mlks da Vila — MVP de atividades, presenças e biblioteca.

Iniciar: python app.py
Sem dependências externas; Python 3.10+. Abra http://127.0.0.1:8000.
Visual inspirado nas três telas de referência fornecidas pelo usuário.
"""
from __future__ import annotations

import html
import os
import re
import secrets
import sqlite3
from contextlib import contextmanager
from datetime import date, datetime
from hmac import compare_digest
from http import HTTPStatus
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

ROOT = Path(__file__).resolve().parent
DB_FILE = Path(os.environ.get("MLKS_DATABASE", str(ROOT / "dados" / "mlks_da_vila.db")))
HOST = os.environ.get("MLKS_HOST", "127.0.0.1")
PORT = int(os.environ.get("MLKS_PORT", "8000"))

# Fallback incorporado em versões de arquivo único; em ZIP, os arquivos CSS/JS
# ficam separados e podem ser editados sem mexer no backend Python.
CSS_EMBEDDED = r''':root {
  color-scheme: light;
  --sidebar:#112b4d;
  --sidebar-deep:#102743;
  --sidebar-active:#284e7f;
  --blue:#064cae;
  --blue-hover:#003f9b;
  --green:#00643e;
  --text:#0b1e3f;
  --muted:#60708b;
  --line:#e2e9f2;
  --surface:#fff;
  --bg:#f4f8fc;
  --shadow:0 8px 24px rgba(30,60,105,.065);
}
* { box-sizing:border-box; }
html { scroll-behavior:smooth; }
body { margin:0; min-width:320px; background:var(--bg); color:var(--text); font-family:Inter,"Segoe UI",Arial,system-ui,sans-serif; font-size:14px; -webkit-font-smoothing:antialiased; }
button,input,textarea,select { font:inherit; }
a { color:var(--blue); text-decoration:none; }
a:hover { text-decoration:none; }
button { cursor:pointer; }
.icon { display:inline-block; flex:none; vertical-align:middle; }
.app-shell { min-height:100vh; }
.sidebar { position:fixed; z-index:30; inset:0 auto 0 0; width:248px; color:#fff; overflow-y:auto; background:linear-gradient(165deg,#11294a 0%,#18365c 68%,#112744 100%); box-shadow:2px 0 15px rgba(10,26,55,.08); }
.brand { min-height:105px; display:flex; align-items:center; gap:9px; padding:18px 12px 17px 16px; color:white; border-bottom:1px solid rgba(255,255,255,.1); }
.brand:hover { color:white; }
.brand svg { height:50px; width:50px; }
.brand strong { display:block; font-size:19px; font-weight:750; letter-spacing:-.6px; white-space:nowrap; margin-bottom:2px; }
.brand small { font-size:10px; color:#f0f6ff; line-height:1.32; display:block; font-weight:400; }
.sidebar-nav { display:flex; flex-direction:column; padding:12px 10px; gap:3px; }
.nav-item { position:relative; min-height:44px; border-radius:6px; display:flex; align-items:center; gap:14px; padding:10px 13px; color:#f2f6ff; font-size:13px; font-weight:550; white-space:nowrap; }
.nav-item .icon { width:19px;height:19px; }
.nav-item.active { background:var(--sidebar-active); color:#fff; font-weight:700; }
.nav-item:hover { background:rgba(255,255,255,.1); color:#fff; }
.nav-item.active:before { position:absolute; top:7px; bottom:7px; left:-10px; width:3px; border-radius:0 4px 4px 0; background:#80b6ff; content:""; }
.nav-item.nav-separator { margin-top:12px; padding-top:18px; border-top:1px solid rgba(255,255,255,.24); border-radius:0; }
.nav-item.nav-separator:hover { border-radius:6px; }
.app-side { margin-left:248px; display:flex; flex-direction:column; min-height:100vh; }
.topbar { height:56px; background:#f5f8fc; border-bottom:1px solid #e6ebf3; display:flex; align-items:center; padding:0 35px; }
.top-spacer { flex:1; }
.avatar { width:32px; height:32px; display:grid; place-items:center; border:1px solid #dbe4ef; background:#e9eff7; color:#163763; border-radius:50%; }
.mobile-title,.nav-toggle { display:none; }
.main-container { width:100%; max-width:1350px; padding:24px 36px 24px; margin:0 auto; flex:1; }
.footer { height:64px; flex:none; display:flex; align-items:center; justify-content:center; gap:11px; color:#66738b; font-size:12px; border-top:1px solid #e5eaf1; background:#f5f8fc; }
.footer .icon { color:#133a78; }
.breadcrumbs { display:flex; align-items:center; gap:9px; min-height:20px; font-size:12px; color:#687991; margin:1px 0 26px; }
.breadcrumbs a { color:var(--blue); }
.breadcrumbs a:hover { text-decoration:underline; }
.crumb-arrow { color:#9caabd; font-size:19px; line-height:10px; }
h1,h2,h3,p { margin-top:0; }
h1 { letter-spacing:-.9px; }
/* Tela 1 — Entrada principal */
.welcome { padding-top:0; max-width:1020px; }
.welcome>h1 { font-size:36px; line-height:1.23; font-weight:760; margin:0 0 4px; color:#0c1d3e; }
.welcome>p { font-size:17px; margin:0 0 33px; color:#2f3f59; }
.entry-cards { display:flex; align-items:stretch; gap:24px; max-width:830px; }
.entry-card { width:50%; min-height:390px; padding:32px 24px 26px; background:#fff; box-shadow:var(--shadow); border:1px solid #dfe7f0; border-radius:9px; text-align:center; display:flex; flex-direction:column; align-items:center; }
.entry-icon { width:144px; height:144px; border-radius:50%; display:grid; place-items:center; margin:0 auto 18px; }
.entry-icon-blue { background:#e0efff; color:#0042a1; }
.entry-icon-green { background:#e2f6e9; color:#016340; }
.entry-icon .icon { stroke-width:1.9; filter:drop-shadow(0 4px 3px rgba(0,25,60,.08)); }
.entry-card h2 { font-size:21px; letter-spacing:-.5px; margin:0 0 9px; font-weight:760; }
.entry-card p { font-size:15px; line-height:1.5; color:#485c7c; margin:0 auto 23px; max-width:265px; }
.btn { border:1px solid transparent; border-radius:5px; min-height:38px; display:inline-flex; align-items:center; justify-content:center; gap:10px; padding:9px 17px; font-size:13px; line-height:1.15; font-weight:650; white-space:nowrap; text-align:center; box-shadow:none; transition:background-color .15s,box-shadow .15s,transform .15s; }
.btn:hover { text-decoration:none; }
.btn:disabled { opacity:.5; cursor:not-allowed; }
.btn-blue { background:var(--blue); color:#fff; box-shadow:0 4px 9px rgba(0,59,144,.12); }
.btn-blue:hover:not(:disabled) { background:var(--blue-hover); color:#fff; }
.btn-green { background:var(--green); color:#fff; box-shadow:0 4px 9px rgba(0,95,50,.12); }
.btn-green:hover:not(:disabled) { background:#004e33; color:#fff; }
.btn-neutral { color:#33465e; background:#e9eef4; }
.btn-neutral:hover { background:#dce4ef; color:#162f51; }
.btn-outline { background:#fff; color:#064eae; border:1px solid #91b7ee; }
.btn-outline:hover { background:#eff6ff; color:#034491; }
.entry-btn { margin-top:auto; height:46px; width:100%; max-width:310px; justify-content:space-between; font-size:15px; padding:9px 18px; }
.entry-btn .icon { margin-left:auto; }
/* Shared interior pages */
.section-heading { display:flex; justify-content:space-between; align-items:flex-start; gap:24px; margin:0 0 20px; }
.section-heading h1 { font-size:24px; line-height:1.25; margin:0 0 6px; letter-spacing:-.55px; }
.section-heading p { color:#64718a; font-size:13px; margin:0; line-height:1.4; }
.section-heading>.btn { flex:none; min-height:35px; margin-top:0; }
.panel { border-radius:7px; border:1px solid #e0e7ef; background:#fff; box-shadow:0 3px 14px rgba(38,68,110,.035); padding:18px 20px; }
.panel h2 { font-size:16px; margin:0 0 14px; font-weight:750; letter-spacing:-.25px; }
.activity-form .panel + .panel { margin-top:15px; }
.entry-section { padding-bottom:17px; }
.field-grid { display:grid; grid-template-columns:1fr 1fr; gap:23px; margin-bottom:15px; }
.field { display:flex; flex-direction:column; gap:6px; width:100%; color:#1a2841; font-size:12px; font-weight:560; }
.field .required { color:#dc493d; font-weight:700; }
.field input,.field textarea,.field select { width:100%; padding:10px 13px; border:1px solid #d9e2ef; color:#142541; font-size:13px; font-weight:420; background:#fff; border-radius:5px; min-height:39px; outline:none; }
.field textarea { min-height:76px; resize:vertical; line-height:1.55; }
.field input::placeholder,.field textarea::placeholder { color:#9aa8b8; }
.field input:focus,.field textarea:focus,.field select:focus { border-color:#1765c3; box-shadow:0 0 0 3px rgba(13,88,181,.12); }
.panel-heading { display:flex; justify-content:space-between; align-items:center; gap:16px; margin-bottom:16px; }
.panel-heading h2 { margin:0 0 2px; }
.panel-heading p { color:#65748b; font-size:12px; margin:0; }
.count-badge { background:#e4f6ea; color:#09673e; border-radius:5px; padding:9px 12px; display:inline-flex; align-items:center; gap:8px; font-size:12px; font-weight:680; white-space:nowrap; }
.table-scroll { width:100%; overflow-x:auto; }
.data-table { border-collapse:collapse; width:100%; table-layout:auto; font-size:13px; }
.data-table thead { background:#edf1f6; }
.data-table th { font-weight:650; color:#43516a; text-align:left; padding:10px 14px; }
.data-table thead th:first-child { border-top-left-radius:5px; }
.data-table thead th:last-child { border-top-right-radius:5px; }
.data-table td { padding:10px 14px; border-bottom:1px solid #ecf0f5; color:#1f2e49; vertical-align:middle; }
.data-table tbody tr:last-child td { border-bottom:0; }
.data-table tbody tr:hover { background:#f9fbff; }
.data-table .center { text-align:center; }
.data-table .col-num { width:52px; }
.person-label { display:inline-flex; gap:18px; align-items:center; cursor:pointer; min-height:20px; width:100%; }
.person-label input { width:17px; height:17px; accent-color:#0750b2; cursor:pointer; margin:0; }
.state-label { display:inline-block; padding:5px 11px; border-radius:5px; font-size:12px; }
.state-present { color:#14643b; background:#e0f6e8; }
.state-absent { color:#6c7887; background:#f1f3f6; }
.panel-actions { display:flex; align-items:center; justify-content:space-between; gap:14px; border-top:1px solid #e4eaf1; padding-top:13px; margin-top:12px; }
.panel-actions .action-right { display:flex; flex-direction:column; gap:8px; align-items:flex-end; }
.action-right small { display:flex; align-items:center; gap:4px; color:#8a96a7; font-size:11px; }
.action-right small .icon { color:#2a5eab; }
/* Tela 3 — resultado */
.success-banner { display:flex; align-items:center; gap:18px; background:#dff6e8; border:1px solid #bdebd0; padding:15px 20px; border-radius:7px; margin:0 0 15px; }
.success-emblem { width:42px; height:42px; border-radius:50%; display:grid; place-items:center; color:#fff; background:#21915c; }
.success-banner strong { display:block; font-size:15px; color:#173a2c; margin-bottom:4px; }
.success-banner small { color:#3d6957; font-size:12px; }
.outcome-panel { margin-bottom:15px; }
.outcome-panel h2,.results-panel h2 { margin-bottom:14px; }
.outcome-grid { display:grid; grid-template-columns:1fr 1fr; gap:20px; }
.outcome-details { display:flex; flex-direction:column; justify-content:center; gap:12px; padding:4px 3px 8px; }
.info-line { display:flex; align-items:flex-start; gap:14px; min-width:0; }
.info-line>.info-icon { border-radius:6px; background:#e8f2fd; color:#0750ac; height:37px; width:37px; flex:none; display:grid; place-items:center; }
.info-line>span:last-child { min-width:0; }
.info-line small { display:block; font-size:11px; color:#677991; margin-bottom:3px; }
.info-line strong { display:block; color:#1a2e4c; font-size:13px; font-weight:600; line-height:1.45; overflow-wrap:anywhere; }
.outcome-metrics { background:#ecf5ff; border-radius:7px; min-height:205px; padding:18px 17px 15px; display:flex; flex-direction:column; justify-content:center; }
.metric-main { display:flex; align-items:center; flex-direction:column; text-align:center; color:#0644a5; padding:0 0 14px; }
.metric-main strong { font-size:29px; line-height:1.2; margin-top:4px; }
.metric-main span { font-size:12px; color:#2967b5; }
.metric-breakdown { border-top:1px solid #d4e3f4; display:grid; grid-template-columns:repeat(3,minmax(0,1fr)); padding-top:13px; }
.metric-breakdown>div { display:grid; grid-template-columns:auto auto; gap:2px 7px; justify-content:center; align-content:start; color:#133968; text-align:left; }
.metric-breakdown>div+div { border-left:1px solid #d4e1f1; }
.metric-breakdown strong { font-size:21px; line-height:1; }
.metric-breakdown small { grid-column:1/-1; text-align:center; color:#58708d; font-size:11px; line-height:1.25; margin-top:4px; }
.metric-breakdown .metric-good { color:#138254; }
.metric-breakdown .metric-bad { color:#db3d3d; }
.status-cell { width:31%; }
.presence-result { display:inline-flex; align-items:center; gap:8px; font-size:12px; }
.presence-result>span { border-radius:5px; padding:4px 10px; }
.presence-result.present { color:#149253; }
.presence-result.present>span { background:#e1f5e8; color:#20734b; }
.presence-result.absent { color:#e13837; }
.presence-result.absent>span { background:#ffe8e7; color:#c93735; }
.presence-result.pending { color:#8491a6; }
.presence-result.pending>span { background:#f0f2f5; }
.three-actions { padding-top:15px; }
.action-cluster { display:flex; justify-content:flex-end; flex-wrap:wrap; gap:10px; }
/* Other screens */
.two-col { display:grid; grid-template-columns:minmax(265px,1fr) minmax(360px,1.5fr); gap:18px; align-items:start; }
.vertical-form { display:flex; flex-direction:column; gap:14px; }
.vertical-form .btn { align-self:flex-start; margin-top:3px; }
.soft-count { background:#eef2f7; color:#485b76; border-radius:5px; padding:6px 9px; font-size:12px; }
.empty-row { text-align:center; color:#64748c!important; padding:28px 20px!important; }
.row-actions { display:flex; flex-wrap:wrap; align-items:center; gap:12px; }
.table-action,.name-link { color:var(--blue); font-weight:650; }
.table-action { display:inline-flex; align-items:center; gap:6px; white-space:nowrap; }
.row-description { display:block; color:#74839a; font-size:11px; margin-top:4px; line-height:1.35; }
.badge { display:inline-flex; white-space:nowrap; border-radius:5px; padding:6px 10px; font-size:11px; }
.badge-ok { color:#15694b; background:#e2f7eb; }
.badge-wait { color:#8a6830; background:#fff6e4; }
.sub-actions { border-top:1px solid var(--line); margin-top:14px; padding-top:15px; }
.sub-actions a { display:inline-flex; align-items:center; gap:8px; font-weight:650; }
.muted { color:#6c7c90; font-size:12px; }
.extra-row { margin-top:18px; }
.library-grid { grid-template-columns:minmax(275px,.9fr) minmax(380px,1.5fr); }
.actions-cell { width:90px; text-align:right; }
.icon-btn { padding:7px; border-radius:5px; border:1px solid #e4eaf3; background:#fff; color:#5c6b80; }
.icon-btn.danger { color:#cc4545; }
.icon-btn:hover { background:#f2f5fa; }
.btn-small { min-height:30px; padding:6px 9px; font-size:11px; }
.article-panel { max-width:920px; line-height:1.75; font-size:14px; }
.article-panel h2 { margin-top:19px; }
.article-panel h2:first-child { margin-top:0; }
.article-panel p,.article-panel li { color:#435773; }
.article-panel ol { padding-left:22px; }
.article-panel li { padding-bottom:10px; }
.notice { display:flex; gap:10px; align-items:center; padding:13px 15px; margin-bottom:15px; font-size:13px; border-radius:6px; }
.notice-error { background:#fff0f0; border:1px solid #f8c6ca; color:#99333c; }
.notice-success { background:#e6f6ee; border:1px solid #b9e4ce; color:#207b54; }
.notice-muted { background:#eff5ff; border:1px solid #d6e6fa; color:#275888; }
.menu-overlay { display:none; }
:focus-visible { outline:3px solid #67a4ef!important; outline-offset:3px; }
@media(max-width:1200px) {
 .app-side { margin-left:248px; } .sidebar { width:248px; }
 .main-container { padding:23px 28px; }
 .entry-card { padding:27px 18px 22px; }
 .entry-card h2 { font-size:19px; }
 .entry-icon { width:124px; height:124px; }
}
@media(max-width:900px) {
 .entry-cards { gap:15px; }
 .entry-card h2 { font-size:18px; }
 .outcome-grid { gap:12px; }
 .two-col,.library-grid { grid-template-columns:1fr; }
 .action-cluster { gap:8px; }
}
@media(max-width:740px) {
 .app-side { margin-left:0; }
 .sidebar { width:262px; transform:translateX(-100%); transition:transform .2s ease; }
 body.menu-open .sidebar { transform:translateX(0); }
 body.menu-open .menu-overlay { display:block; background:#07182b88; position:fixed; inset:0; z-index:20; }
 .topbar { padding:0 18px; height:58px; }
 .nav-toggle { display:grid; place-items:center; background:transparent; border:0; color:#173d68; padding:8px; margin-left:-6px; }
 .mobile-title { display:block; margin-left:8px; font-size:15px; color:#13345a; font-weight:700; }
 .main-container { padding:20px 20px 28px; }
 .breadcrumbs { margin-bottom:24px; }
 .welcome>h1 { font-size:28px; }
 .entry-cards { gap:16px; }
 .entry-card { padding:20px 12px; min-height:334px; }
 .entry-icon { width:96px; height:96px; }
 .entry-icon .icon { width:56px; height:56px; }
 .entry-card p { font-size:13px; }
 .entry-btn { white-space:normal; font-size:12px; padding:9px 10px; }
 .outcome-grid { grid-template-columns:1fr; }
 .outcome-metrics { min-height:190px; }
 .three-actions { align-items:stretch; flex-direction:column; }
 .action-cluster { justify-content:stretch; }
 .action-cluster .btn { flex:1 1 auto; }
}
@media(max-width:520px) {
 .welcome>h1 { font-size:25px; }
 .welcome>p { font-size:14px; margin-bottom:22px; }
 .entry-cards { flex-direction:column; }
 .entry-card { width:100%; min-height:285px; padding:23px 15px 17px; }
 .entry-icon { width:95px; height:95px; margin-bottom:12px; }
 .entry-card h2 { font-size:19px; }
 .entry-card p { margin-bottom:17px; }
 .entry-btn { height:42px; max-width:280px; font-size:13px; justify-content:center; }
 .section-heading { flex-direction:column; gap:12px; }
 .section-heading h1 { font-size:22px; }
 .section-heading>.btn { align-self:flex-start; }
 .panel { padding:16px 13px; }
 .field-grid { grid-template-columns:1fr; gap:13px; }
 .panel-heading { align-items:flex-start; flex-direction:column; }
 .data-table { min-width:420px; font-size:12px; }
 .presence-table { min-width:330px; }
 .panel-actions { gap:10px; }
 .panel-actions .btn { white-space:normal; }
 .three-actions>.btn { width:100%; }
 .action-cluster { flex-direction:column; }
 .success-banner { padding:13px; gap:10px; }
 .success-banner strong { font-size:13px; }
 .success-banner small { font-size:11px; }
 .main-container { padding-left:14px; padding-right:14px; }
 .footer { font-size:11px; }
}
'''
JS_EMBEDDED = r''''use strict';
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
'''


def e(value: object) -> str:
    return html.escape(str(value if value is not None else ""), quote=True)


def icon(name: str, *, size: int = 19) -> str:
    """Ícones SVG pequenos, locais, sem dependência de internet."""
    shapes = {
        "home": '<path d="m3 10 9-7 9 7v10a1 1 0 0 1-1 1h-5v-7H9v7H4a1 1 0 0 1-1-1z"/>',
        "activity": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/><circle cx="9" cy="14" r="1"/><circle cx="15" cy="14" r="1"/><path d="M7 19v-1M17 19v-1"/>',
        "calendar-users": '<rect x="2" y="3" width="20" height="18" rx="2"/><path d="M7 1v4M17 1v4M2 8h20"/><circle cx="9" cy="12.5" r="2"/><path d="M5.5 18c.4-2.1 2-3 3.5-3s3.1.9 3.5 3"/><circle cx="16.5" cy="13" r="1.5"/><path d="M14.6 18c.3-1.5 1.1-2.2 2.1-2.2 1.2 0 2.2.8 2.4 2.2"/>',
        "book": '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H21V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H21v-5"/><path d="M8 8h9M8 12h7"/>',
        "books": '<path d="m2.5 7 9.5-4.5L21.5 7 12 11.5z"/><path d="m2.5 11 9.5 4.5 9.5-4.5M2.5 15l9.5 4.5 9.5-4.5M2.5 19l9.5 4.5 9.5-4.5"/>',
        "info": '<circle cx="12" cy="12" r="10"/><path d="M12 11v6M12 7h.01"/>',
        "help": '<circle cx="12" cy="12" r="10"/><path d="M9 9a3 3 0 1 1 5.7 1.4c-1.3 1.5-2.7 1.7-2.7 3.6M12 17h.01"/>',
        "arrow-right": '<path d="M5 12h14m-6-6 6 6-6 6"/>',
        "arrow-left": '<path d="M19 12H5m6 6-6-6 6-6"/>',
        "check": '<path d="m5 12 4 4L19 6"/>',
        "check-circle": '<circle cx="12" cy="12" r="10"/><path d="m7 12 3 3 7-7"/>',
        "x-circle": '<circle cx="12" cy="12" r="10"/><path d="m9 9 6 6m0-6-6 6"/>',
        "users": '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
        "list": '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
        "date": '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M16 3v4M8 3v4M3 10h18"/>',
        "menu": '<path d="M4 7h16M4 12h16M4 17h16"/>',
        "user": '<circle cx="12" cy="8" r="4"/><path d="M4.8 20a7.2 7.2 0 0 1 14.4 0"/>',
        "plus": '<path d="M12 5v14M5 12h14"/>',
        "trash": '<path d="M3 6h18M8 6V4h8v2m3 0-1 15H6L5 6M10 10v7M14 10v7"/>',
        "return": '<path d="M9 14 4 9l5-5M4 9h10a6 6 0 0 1 0 12h-2"/>',
        "search": '<circle cx="11" cy="11" r="7"/><path d="m20 20-4-4"/>',
    }
    return f'<svg class="icon" viewBox="0 0 24 24" width="{size}" height="{size}" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{shapes.get(name, shapes["info"])}</svg>'


def logo() -> str:
    # Marca vetorial: livro aberto, pessoas e telhado comunitário.
    return '''<svg width="48" height="48" viewBox="0 0 54 54" aria-hidden="true" fill="none" stroke="white" stroke-linecap="round" stroke-linejoin="round">
    <path stroke-width="2.3" d="M5 23 27 6l22 17M10 23v12L27 46l17-11V23"/><path stroke-width="2" d="M9 35c7-3 13-2 18 4 5-6 11-7 18-4M27 25v14"/>
    <circle cx="27" cy="18" r="3.1" fill="white" stroke="none"/><circle cx="17" cy="23" r="2.3" fill="white" stroke="none"/><circle cx="37" cy="23" r="2.3" fill="white" stroke="none"/>
    <path stroke-width="1.8" d="M22 28c.3-3 2.1-4.4 5-4.4s4.7 1.4 5 4.4M12.8 30c.3-2.8 1.8-4 4.2-4s3.9 1.2 4.2 4M32.8 30c.3-2.8 1.8-4 4.2-4s3.9 1.2 4.2 4"/></svg>'''


@contextmanager
def connect():
    con = sqlite3.connect(DB_FILE, timeout=10)
    con.row_factory = sqlite3.Row
    con.execute("PRAGMA foreign_keys = ON")
    con.execute("PRAGMA busy_timeout = 10000")
    try:
        yield con
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.close()


def init_db():
    DB_FILE.parent.mkdir(parents=True, exist_ok=True)
    with connect() as con:
        con.executescript("""
        CREATE TABLE IF NOT EXISTS participantes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL COLLATE NOCASE,
            turma TEXT NOT NULL DEFAULT '',
            criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS atividades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            data TEXT NOT NULL,
            horario TEXT NOT NULL DEFAULT '',
            responsavel TEXT NOT NULL DEFAULT '',
            local TEXT NOT NULL DEFAULT '',
            categoria TEXT NOT NULL DEFAULT 'Educação',
            descricao TEXT NOT NULL DEFAULT '',
            presenca_registrada INTEGER NOT NULL DEFAULT 0,
            criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS inscricoes (
            atividade_id INTEGER NOT NULL,
            participante_id INTEGER NOT NULL,
            presente INTEGER NOT NULL DEFAULT 0 CHECK (presente IN (0,1)),
            PRIMARY KEY (atividade_id, participante_id),
            FOREIGN KEY(atividade_id) REFERENCES atividades(id) ON DELETE CASCADE,
            FOREIGN KEY(participante_id) REFERENCES participantes(id) ON DELETE CASCADE
        );
        CREATE TABLE IF NOT EXISTS livros (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            autor TEXT NOT NULL,
            categoria TEXT NOT NULL DEFAULT 'Educação',
            quantidade INTEGER NOT NULL DEFAULT 1 CHECK (quantidade >= 0),
            criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
        CREATE TABLE IF NOT EXISTS emprestimos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            livro_id INTEGER NOT NULL,
            participante_id INTEGER NOT NULL,
            retirado_em TEXT NOT NULL,
            devolvido_em TEXT,
            FOREIGN KEY(livro_id) REFERENCES livros(id) ON DELETE RESTRICT,
            FOREIGN KEY(participante_id) REFERENCES participantes(id) ON DELETE RESTRICT
        );
        CREATE INDEX IF NOT EXISTS idx_atividades_data ON atividades(data);
        CREATE INDEX IF NOT EXISTS idx_emprestimos_ativos ON emprestimos(livro_id, devolvido_em);
        """)
        migrate_participant_names(con)


def migrate_participant_names(con):
    """Atualiza o esquema legado preservando IDs e vínculos com outras tabelas."""
    row = con.execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name='participantes'"
    ).fetchone()
    if not row or "UNIQUE" not in row["sql"].upper():
        return

    # PRAGMA foreign_keys só pode ser alterado fora de transação ativa.
    con.commit()
    con.execute("PRAGMA foreign_keys = OFF")
    try:
        con.execute("BEGIN IMMEDIATE")
        con.execute("""
            CREATE TABLE participantes_novos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL COLLATE NOCASE,
                turma TEXT NOT NULL DEFAULT '',
                criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        con.execute("""
            INSERT INTO participantes_novos(id, nome, turma, criado_em)
            SELECT id, nome, turma, criado_em FROM participantes
        """)
        con.execute("DROP TABLE participantes")
        con.execute("ALTER TABLE participantes_novos RENAME TO participantes")
        if con.execute("PRAGMA foreign_key_check").fetchone():
            raise sqlite3.IntegrityError("Migração interrompida: referência inválida")
        con.commit()
    except Exception:
        con.rollback()
        raise
    finally:
        con.execute("PRAGMA foreign_keys = ON")


def get_people(con):
    return con.execute("SELECT id,nome,turma FROM participantes ORDER BY nome COLLATE NOCASE, turma COLLATE NOCASE, id").fetchall()


def fmt_date(iso: str) -> str:
    try:
        return datetime.strptime(iso[:10], "%Y-%m-%d").strftime("%d/%m/%Y")
    except (ValueError, TypeError):
        return iso


def csrf_input(token: str) -> str:
    return f'<input type="hidden" name="_csrf" value="{e(token)}">'


def navigation(path: str) -> str:
    nav = [
        ("/", "Início", "home"),
        ("/atividades", "Atividades e Presenças", "activity"),
        ("/biblioteca", "Biblioteca", "book"),
        ("/sobre", "Sobre", "info"),
        ("/ajuda", "Ajuda", "help"),
    ]
    result = []
    for index, (url, label, glyph) in enumerate(nav):
        active = (path == url or (url == "/atividades" and (path.startswith("/atividades") or path.startswith("/participantes"))) or (url == "/" and path == "/"))
        divider = ' nav-separator' if index == 3 else ''
        result.append(f'<a class="nav-item{divider}{" active" if active else ""}" href="{url}" {"aria-current=page" if active else ""}>{icon(glyph)}<span>{label}</span></a>')
    return "".join(result)


def layout(path: str, page: str, *, page_title: str = "Mlks da Vila", error: str = "", success: str = "") -> str:
    alert = f'<div class="notice notice-error" role="alert">{icon("x-circle")}{e(error)}</div>' if error else ''
    if success:
        alert += f'<div class="notice notice-success" role="status">{icon("check-circle")}{e(success)}</div>'
    return f'''<!doctype html><html lang="pt-BR"><head><meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#122b4a">
<meta name="description" content="Mlks da Vila — atividades, presenças e biblioteca comunitária">
<title>{e(page_title)} | Mlks da Vila</title>
<link rel="stylesheet" href="/static/style.css"></head><body>
<div class="app-shell">
<aside class="sidebar" id="sidebar">
<a class="brand" href="/">{logo()}<span><strong>Mlks da Vila</strong><small>Organizando oportunidades,<br>fortalecendo a comunidade</small></span></a>
<nav class="sidebar-nav" aria-label="Navegação principal">{navigation(path)}</nav>
</aside>
<div class="app-side"><header class="topbar">
<button class="nav-toggle" type="button" aria-label="Abrir menu" aria-expanded="false" aria-controls="sidebar">{icon("menu",size=22)}</button>
<span class="mobile-title">Mlks da Vila</span><span class="top-spacer"></span>
<span class="avatar" title="Projeto comunitário" aria-label="Projeto comunitário">{icon("user",size=17)}</span>
</header><main class="main-container" id="conteudo">{alert}{page}</main>
<footer class="footer">{icon("users", size=17)} <span>Projeto comunitário — Mlks da Vila</span></footer>
</div></div><div class="menu-overlay" id="menu-overlay"></div>
<script src="/static/app.js" defer></script></body></html>'''


def breadcrumbs(*items: tuple[str, str] | str) -> str:
    bits = ['<a href="/">Início</a>']
    for item in items:
        if isinstance(item, tuple):
            bits.append(f'<a href="{e(item[1])}">{e(item[0])}</a>')
        else:
            bits.append(f'<span aria-current="page">{e(item)}</span>')
    return '<div class="breadcrumbs">' + '<span class="crumb-arrow">›</span>'.join(bits) + '</div>'


def section_header(title: str, subtitle: str, right: str = "") -> str:
    return f'<div class="section-heading"><div><h1>{e(title)}</h1><p>{e(subtitle)}</p></div>{right}</div>'


def button_href(url: str, text: str, style: str = "neutral", glyph: str = "") -> str:
    return f'<a href="{e(url)}" class="btn btn-{style}">{icon(glyph, size=16) if glyph else ""}{e(text)}</a>'


def home_page() -> str:
    return f'''{breadcrumbs()}
<section class="welcome">
<h1>Bem-vindo ao Mlks da Vila</h1><p>Selecione uma opção para continuar</p>
<div class="entry-cards">
<article class="entry-card">
<div class="entry-icon entry-icon-blue">{icon("calendar-users", size=78)}</div>
<h2>Atividades e Presenças</h2>
<p>Cadastre atividades, registre participantes e consulte o total de presenças.</p>
<a href="/atividades/nova" class="btn btn-blue entry-btn">Acessar atividades {icon("arrow-right",size=21)}</a>
</article>
<article class="entry-card">
<div class="entry-icon entry-icon-green">{icon("books", size=78)}</div>
<h2>Biblioteca</h2><p>Consulte livros, registre empréstimos e acompanhe devoluções.</p>
<a href="/biblioteca" class="btn btn-green entry-btn">Acessar biblioteca {icon("arrow-right",size=21)}</a>
</article></div></section>'''


def activity_form(con, token: str, values: dict | None = None, selected: set[int] | None = None, *, edit_id: int | None = None) -> str:
    vals = values or {}
    people = get_people(con)
    selected = selected or set()
    today = date.today().isoformat()
    rows = "".join(
        f'''<tr class="person-row"><td class="center">{i}</td>
<td><label class="person-label"><input type="checkbox" name="presentes" value="{p['id']}" {"checked" if p['id'] in selected else ""}>
<span>{e(p['nome'])}<small class="row-description">Turma: {e(p['turma'] or 'Não informada')} · Cadastro #{p['id']}</small></span></label></td><td><span class="state-label {"state-present" if p['id'] in selected else "state-absent"}">{"Presente" if p['id'] in selected else "Ausente"}</span></td></tr>'''
        for i, p in enumerate(people, 1)
    ) if people else '<tr><td colspan="3" class="empty-row">Nenhum participante cadastrado. <a href="/participantes">Cadastre participantes</a> antes de registrar a atividade.</td></tr>'
    count = len(selected)
    title = "Editar atividade e presenças" if edit_id else "Registrar atividade e presenças"
    submit = "Salvar alterações" if edit_id else "Salvar atividade e presenças"
    target = f"/atividades/{edit_id}/editar" if edit_id else "/atividades/nova"
    return f'''{breadcrumbs(("Atividades e Presenças", "/atividades"))}
{section_header(title,"Preencha os dados da atividade e marque os participantes presentes.",button_href("/atividades","Voltar ao menu","neutral","arrow-left"))}
<form method="post" action="{target}" id="atividade-form" data-presenca-form class="activity-form">
{csrf_input(token)}
<section class="panel entry-section"><h2>Dados da atividade</h2>
<div class="field-grid"><label class="field"><span>Nome da atividade <b class="required">*</b></span>
<input required autocomplete="off" maxlength="120" type="text" name="titulo" value="{e(vals.get('titulo',''))}" placeholder="Ex.: Aula de inglês"></label>
<label class="field"><span>Data da atividade <b class="required">*</b></span>
<input required type="date" name="data" value="{e(vals.get('data',today))}"></label></div>
<label class="field"><span>Descrição (opcional)</span><textarea name="descricao" maxlength="800" rows="3" placeholder="Atividade educativa para crianças e adolescentes.">{e(vals.get('descricao',''))}</textarea></label>
</section>
<section class="panel attendance-section"><div class="panel-heading"><div><h2>Participantes</h2><p>Marque quem compareceu à atividade.</p></div><span class="count-badge">{icon("users",size=16)} <span id="presence-counter" aria-live="polite">{count} de {len(people)} participantes presentes</span></span></div>
<div class="table-scroll"><table class="data-table presence-table"><thead><tr><th class="center col-num">#</th><th>Nome</th><th>Situação</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="panel-actions"><a href="/atividades" data-cancel-form class="btn btn-neutral">Cancelar</a><div class="action-right"><button type="submit" class="btn btn-blue" {"disabled" if not people else ""}>{submit}</button><small>{icon("info",size=13)} Confira as informações antes de salvar.</small></div></div>
</section></form>'''


def activity_detail(con, activity, *, just_saved: bool = False) -> str:
    roster = con.execute('''SELECT p.nome, p.turma, p.id, i.presente FROM inscricoes i JOIN participantes p ON p.id=i.participante_id
                             WHERE i.atividade_id=? ORDER BY p.nome COLLATE NOCASE, p.turma COLLATE NOCASE, p.id''', (activity['id'],)).fetchall()
    n = len(roster)
    present = sum(row['presente'] for row in roster)
    absent = n - present
    done = bool(activity['presenca_registrada'])
    rows = ''.join(f'''<tr><td class="center">{k}</td><td>{e(p['nome'])}<small class="row-description">Turma: {e(p['turma'] or 'Não informada')} · Cadastro #{p['id']}</small></td>
<td class="status-cell"><span class="presence-result {"present" if p['presente'] else "absent" if done else "pending"}">{icon("check-circle" if p['presente'] else "x-circle" if done else "info", size=15)}
<span>{"Presente" if p['presente'] else "Ausente" if done else "Pendente"}</span></span></td></tr>'''
        for k,p in enumerate(roster,1)) or '<tr><td colspan="3" class="empty-row">Esta atividade não tem participantes registrados.</td></tr>'
    success = '<div class="success-banner" role="status"><span class="success-emblem">' + icon("check",size=30) + '</span><span><strong>Atividade salva com sucesso!</strong><small>Os dados da atividade e das presenças foram registrados.</small></span></div>' if just_saved else ''
    if not done:
        success = '<div class="notice notice-muted" role="status">' + icon('info') + 'As presenças desta atividade ainda não foram confirmadas. Você pode registrá-las agora.</div>'
    title = 'Resultado do registro' if just_saved else 'Registro de atividade'
    return f'''{breadcrumbs(("Atividades e Presenças", "/atividades"),"Resultado")}
{section_header(title,"Confira os dados da atividade e o total de participantes presentes.")}
{success}
<section class="panel outcome-panel"><h2>Resumo da atividade</h2><div class="outcome-grid"><div class="outcome-details">
<div class="info-line"><span class="info-icon">{icon("activity")}</span><span><small>Atividade</small><strong>{e(activity['titulo'])}</strong></span></div>
<div class="info-line"><span class="info-icon">{icon("date")}</span><span><small>Data</small><strong>{e(fmt_date(activity['data']))}</strong></span></div>
<div class="info-line"><span class="info-icon">{icon("list")}</span><span><small>Descrição</small><strong>{e(activity['descricao'] or 'Nenhuma descrição informada.')}</strong></span></div>
</div><div class="outcome-metrics"><div class="metric-main">{icon("users",size=27)}<strong>{present} de {n}</strong><span>participantes presentes</span></div>
<div class="metric-breakdown"><div>{icon("users",size=20)}<strong>{n}</strong><small>Participantes<br>registrados</small></div>
<div class="metric-good">{icon("check-circle",size=20)}<strong>{present}</strong><small>Presentes</small></div>
<div class="metric-bad">{icon("x-circle",size=20)}<strong>{absent if done else '—'}</strong><small>Ausentes</small></div></div></div></div></section>
<section class="panel results-panel"><h2>Presenças registradas</h2><div class="table-scroll"><table class="data-table result-table"><thead><tr><th class="col-num center">#</th><th>Nome</th><th>Situação</th></tr></thead><tbody>{rows}</tbody></table></div>
<div class="panel-actions three-actions">{button_href('/','Voltar ao menu','neutral','arrow-left')}
<div class="action-cluster">{button_href('/atividades/nova','Registrar outra atividade','outline','activity')}{button_href('/atividades','Consultar presenças','blue','list')}</div></div></section>'''


def activity_listing(con, token: str) -> str:
    activities = con.execute('''SELECT a.*,COUNT(i.participante_id) total,COALESCE(SUM(i.presente),0) presentes
        FROM atividades a LEFT JOIN inscricoes i ON i.atividade_id=a.id
        GROUP BY a.id ORDER BY a.data DESC, a.id DESC''').fetchall()
    items = ''.join(f'''<tr><td><a class="name-link" href="/atividades/{a['id']}">{e(a['titulo'])}</a>
<small class="row-description">{e(a['descricao'][:95]) or 'Sem descrição'}</small></td><td>{e(fmt_date(a['data']))}</td>
<td><span class="badge {"badge-ok" if a['presenca_registrada'] else "badge-wait"}">{f"{a['presentes']} de {a['total']} presentes" if a['presenca_registrada'] else 'Aguardando chamada'}</span></td>
<td><div class="row-actions"><a class="table-action" href="/atividades/{a['id']}">Consultar {icon("arrow-right",size=16)}</a><a class="table-action" href="/atividades/{a['id']}/editar">Editar</a></div></td></tr>''' for a in activities)
    if not items:
        items = '<tr><td colspan="4" class="empty-row">Ainda não existem atividades cadastradas. Use o botão acima para registrar a primeira.</td></tr>'
    return f'''{breadcrumbs("Atividades e Presenças")}
{section_header("Atividades e Presenças","Consulte os registros da comunidade ou cadastre uma nova atividade.",button_href('/atividades/nova','Registrar atividade','blue','plus'))}
<section class="panel list-section"><div class="panel-heading"><div><h2>Atividades cadastradas</h2><p>Abra um registro para consultar presentes e ausentes.</p></div><span class="soft-count">{len(activities)} atividade(s)</span></div>
<div class="table-scroll"><table class="data-table activities-table"><thead><tr><th>Atividade</th><th>Data</th><th>Presenças</th><th></th></tr></thead><tbody>{items}</tbody></table></div>
<div class="sub-actions"><a href="/participantes">{icon('users',size=17)} Gerenciar participantes {icon('arrow-right',size=16)}</a></div>
</section>'''


def people_page(con, token: str) -> str:
    people = get_people(con)
    rows = ''.join(f'''<tr><td>{e(p['nome'])}<small class="row-description">Cadastro #{p['id']}</small></td><td>{e(p['turma'] or '—')}</td>
<td class="actions-cell"><form method="post" action="/participantes/{p['id']}/excluir" data-confirm="Excluir este participante? Só é possível remover quem não possui atividades ou empréstimos vinculados.">{csrf_input(token)}<button type="submit" class="icon-btn danger" aria-label="Excluir {e(p['nome'])}">{icon('trash',size=17)}</button></form></td></tr>''' for p in people)
    if not rows:
        rows = '<tr><td colspan="3" class="empty-row">Nenhum participante cadastrado. Cadastre pessoas para registrar as presenças.</td></tr>'
    return f'''{breadcrumbs(("Atividades e Presenças","/atividades"),"Participantes")}
{section_header("Participantes","Cadastre as pessoas que participam das atividades da ONG.",button_href('/atividades/nova','Registrar atividade','outline','arrow-left'))}
<div class="two-col"><section class="panel"><h2>Novo participante</h2><form action="/participantes" method="post" class="vertical-form">{csrf_input(token)}
<label class="field"><span>Nome completo <b class="required">*</b></span><input type="text" name="nome" maxlength="120" required placeholder="Nome do participante"></label>
<label class="field"><span>Turma ou grupo (opcional)</span><input type="text" name="turma" maxlength="80" placeholder="Ex.: Turma A"></label>
<button type="submit" class="btn btn-blue">{icon('plus',size=16)} Adicionar participante</button></form></section>
<section class="panel"><div class="panel-heading"><h2>Participantes cadastrados</h2><span class="soft-count">{len(people)}</span></div>
<div class="table-scroll"><table class="data-table"><thead><tr><th>Nome</th><th>Turma</th><th></th></tr></thead><tbody>{rows}</tbody></table></div></section></div>'''


def library_page(con, token: str) -> str:
    books = con.execute('''SELECT l.*, (SELECT COUNT(*) FROM emprestimos x WHERE x.livro_id=l.id AND x.devolvido_em IS NULL) emprestados
                           FROM livros l ORDER BY l.titulo COLLATE NOCASE''').fetchall()
    people = get_people(con)
    active_loans = con.execute('''SELECT x.id, x.retirado_em, x.participante_id, p.nome participante, p.turma, l.titulo livro
                                  FROM emprestimos x JOIN livros l ON l.id=x.livro_id JOIN participantes p ON p.id=x.participante_id
                                  WHERE x.devolvido_em IS NULL ORDER BY x.retirado_em DESC''').fetchall()
    books_rows = ''.join(f'''<tr><td><strong>{e(b['titulo'])}</strong><small class="row-description">{e(b['autor'])} · {e(b['categoria'])}</small></td>
<td>{b['quantidade']}</td><td>{b['quantidade']-b['emprestados']}</td></tr>''' for b in books) or '<tr><td class="empty-row" colspan="3">Nenhum livro cadastrado.</td></tr>'
    loan_rows = ''.join(f'''<tr><td>{e(x['livro'])}<small class="row-description">{e(x['participante'])} · {e(x['turma'] or 'Sem turma')} · Cadastro #{x['participante_id']}</small></td>
<td>{e(fmt_date(x['retirado_em']))}</td><td class="actions-cell"><form method="post" action="/biblioteca/emprestimos/{x['id']}/devolver">{csrf_input(token)}<button type="submit" class="btn btn-outline btn-small">{icon('return',size=15)} Devolver</button></form></td></tr>''' for x in active_loans) or '<tr><td colspan="3" class="empty-row">Nenhum empréstimo em aberto.</td></tr>'
    book_select = '<option value="">Selecione um livro</option>' + ''.join(f'<option value="{b["id"]}" {"disabled" if b["quantidade"] <= b["emprestados"] else ""}>{e(b["titulo"])} — {b["quantidade"]-b["emprestados"]} disponível(is)</option>' for b in books)
    people_select = '<option value="">Selecione um participante</option>' + ''.join(f'<option value="{p["id"]}">{e(p["nome"])} · {e(p["turma"] or "Sem turma")} · Cadastro #{p["id"]}</option>' for p in people)
    return f'''{breadcrumbs("Biblioteca")}
{section_header("Biblioteca","Consulte o acervo, registre empréstimos e acompanhe devoluções.")}
<div class="two-col library-grid"><section class="panel"><h2>Cadastrar livro</h2>
<form method="post" action="/biblioteca/livros" class="vertical-form">{csrf_input(token)}
<label class="field"><span>Título <b class="required">*</b></span><input name="titulo" maxlength="160" required placeholder="Nome do livro"></label>
<label class="field"><span>Autor(a) <b class="required">*</b></span><input name="autor" maxlength="120" required placeholder="Nome do autor"></label>
<label class="field"><span>Categoria</span><select name="categoria"><option>Educação</option><option>Literatura</option><option>Infantil</option><option>Tecnologia</option><option>Outros</option></select></label>
<label class="field"><span>Quantidade de exemplares <b class="required">*</b></span><input name="quantidade" min="1" max="9999" value="1" required type="number"></label>
<button type="submit" class="btn btn-blue">{icon('plus',size=16)} Cadastrar livro</button></form></section>
<section class="panel"><div class="panel-heading"><h2>Acervo cadastrado</h2><span class="soft-count">{len(books)} título(s)</span></div>
<div class="table-scroll"><table class="data-table"><thead><tr><th>Título</th><th>Total</th><th>Disponíveis</th></tr></thead><tbody>{books_rows}</tbody></table></div></section></div>
<div class="two-col library-grid extra-row"><section class="panel"><h2>Registrar empréstimo</h2>
<form method="post" action="/biblioteca/emprestimos" class="vertical-form">{csrf_input(token)}
<label class="field"><span>Livro <b class="required">*</b></span><select name="livro_id" required>{book_select}</select></label>
<label class="field"><span>Participante <b class="required">*</b></span><select name="participante_id" required>{people_select}</select></label>
<button type="submit" class="btn btn-green" {"disabled" if not people or not books else ""}>{icon('book',size=16)} Registrar empréstimo</button>
{'' if people else '<p class="muted">Cadastre participantes para emprestar livros. <a href="/participantes">Gerenciar participantes</a>.</p>'}</form></section>
<section class="panel"><div class="panel-heading"><h2>Empréstimos em aberto</h2><span class="soft-count">{len(active_loans)}</span></div>
<div class="table-scroll"><table class="data-table"><thead><tr><th>Livro / pessoa</th><th>Empréstimo</th><th></th></tr></thead><tbody>{loan_rows}</tbody></table></div></section></div>'''


def info_page(kind: str) -> str:
    if kind == 'sobre':
        return f'''{breadcrumbs("Sobre")}{section_header("Sobre o Mlks da Vila","Organizando oportunidades, fortalecendo a comunidade.")}
<section class="panel article-panel"><h2>Nosso projeto</h2><p>O Mlks da Vila é um projeto comunitário dedicado ao fortalecimento da educação e da participação social. Este sistema foi criado para apoiar voluntários no registro das atividades, no acompanhamento das presenças e na gestão da biblioteca.</p><h2>Impacto educacional</h2><p>O projeto está alinhado ao ODS 4 — Educação de Qualidade, facilitando a organização de ações educacionais da comunidade.</p></section>'''
    return f'''{breadcrumbs("Ajuda")}{section_header("Ajuda","Passo a passo para utilizar o sistema.")}
<section class="panel article-panel"><h2>Como registrar uma atividade</h2><ol><li>Acesse <a href="/participantes">Participantes</a> e cadastre as pessoas que fazem parte da ONG.</li><li>Em <a href="/atividades/nova">Atividades e Presenças</a>, preencha o nome e a data da atividade.</li><li>Marque as caixas dos participantes presentes e confira o contador.</li><li>Clique em <strong>Salvar atividade e presenças</strong> e consulte o resumo na tela de resultado.</li><li>Em <a href="/biblioteca">Biblioteca</a>, cadastre títulos, registre empréstimos e marque as devoluções.</li></ol><p>Os dados são armazenados apenas no computador que executa este sistema, no arquivo <code>dados/mlks_da_vila.db</code>.</p></section>'''


def form_val(form: dict[str,list[str]], key: str) -> str:
    return form.get(key, [""])[0].strip()


class Handler(BaseHTTPRequestHandler):
    server_version = 'MlksDaVila/2.0'

    def token(self) -> str:
        cookie = SimpleCookie()
        try:
            cookie.load(self.headers.get('Cookie', ''))
        except Exception:
            pass
        token = cookie['mlks_csrf'].value if 'mlks_csrf' in cookie else ''
        self.new_cookie = not bool(re.fullmatch(r'[a-f0-9]{64}', token))
        if self.new_cookie:
            token = secrets.token_hex(32)
        self.csrf = token
        return token

    def send_content(self, payload: str | bytes, code: int = 200, type_: str = 'text/html; charset=utf-8'):
        raw = payload.encode('utf-8') if isinstance(payload,str) else payload
        self.send_response(code)
        self.send_header('Content-Type',type_)
        self.send_header('Content-Length',str(len(raw)))
        self.send_header('Cache-Control', 'no-store' if type_.startswith('text/html') else 'public, max-age=300')
        self.send_header('X-Content-Type-Options','nosniff')
        self.send_header('X-Frame-Options','DENY')
        self.send_header('Content-Security-Policy',"default-src 'self'; style-src 'self'; script-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'self'")
        if getattr(self, 'new_cookie', False):
            self.send_header('Set-Cookie', f'mlks_csrf={self.csrf}; HttpOnly; SameSite=Lax; Path=/')
        self.end_headers()
        self.wfile.write(raw)

    def redirect(self, location: str):
        self.send_response(HTTPStatus.SEE_OTHER)
        self.send_header('Location', location)
        self.send_header('Content-Length','0')
        self.end_headers()

    def show(self, path: str, content: str, title: str = 'Mlks da Vila', *, error: str = '', success: str = ''):
        self.send_content(layout(path,content,page_title=title,error=error,success=success),422 if error else 200)

    def not_found(self):
        self.send_content(layout('/','<section class="panel article-panel"><h1>Página não encontrada</h1><p>O endereço solicitado não existe.</p><a href="/" class="btn btn-blue">Voltar ao início</a></section>'),404)

    def do_GET(self):
        self.token()
        url = urlsplit(self.path)
        path = url.path
        if path == '/static/style.css':
            file = ROOT/'static'/'style.css'
            self.send_content(file.read_bytes() if file.exists() else CSS_EMBEDDED.encode('utf-8'),type_='text/css; charset=utf-8')
            return
        if path == '/static/app.js':
            file = ROOT/'static'/'app.js'
            self.send_content(file.read_bytes() if file.exists() else JS_EMBEDDED.encode('utf-8'),type_='application/javascript; charset=utf-8')
            return
        if path == '/favicon.ico':
            self.send_content(b'', code=204, type_='image/x-icon')
            return
        with connect() as con:
            if path == '/':
                self.show(path,home_page(), 'Início')
            elif path == '/atividades':
                self.show(path,activity_listing(con,self.csrf),'Atividades e Presenças',success='Registro atualizado com sucesso.' if 'atualizado' in parse_qs(url.query) else '')
            elif path == '/atividades/nova':
                self.show(path,activity_form(con,self.csrf),'Registrar atividade')
            elif path == '/participantes':
                self.show(path,people_page(con,self.csrf),'Participantes',success='Participante cadastrado com sucesso.' if 'ok' in parse_qs(url.query) else '')
            elif path == '/biblioteca':
                self.show(path,library_page(con,self.csrf),'Biblioteca',success='Operação realizada com sucesso.' if 'ok' in parse_qs(url.query) else '')
            elif path == '/sobre':
                self.show(path,info_page('sobre'),'Sobre')
            elif path == '/ajuda':
                self.show(path,info_page('ajuda'),'Ajuda')
            elif path in ('/resultados','/presencas'):
                self.redirect('/atividades')
            elif match := re.fullmatch(r'/atividades/(\d+)/editar',path):
                a = con.execute('SELECT * FROM atividades WHERE id=?',(int(match.group(1)),)).fetchone()
                if a is None: return self.not_found()
                selected = {r[0] for r in con.execute('SELECT participante_id FROM inscricoes WHERE atividade_id=? AND presente=1',(a['id'],))}
                self.show(path,activity_form(con,self.csrf, dict(a), selected, edit_id=a['id']),'Editar atividade')
            elif match := re.fullmatch(r'/atividades/(\d+)(?:/presencas)?',path):
                a = con.execute('SELECT * FROM atividades WHERE id=?',(int(match.group(1)),)).fetchone()
                if a is None: return self.not_found()
                self.show(path,activity_detail(con,a,just_saved=parse_qs(url.query).get('salvo',[''])[0]=='1'),'Resultado do registro')
            else:
                self.not_found()

    def do_POST(self):
        self.token()
        path = urlsplit(self.path).path
        try:
            size = int(self.headers.get('Content-Length','-1'))
        except ValueError:
            size = -1
        if size < 0 or size > 1000000:
            return self.send_content(layout(path,'<p>Requisição inválida.</p>'), 413)
        if not self.headers.get('Content-Type','').startswith('application/x-www-form-urlencoded'):
            return self.send_content(layout(path,'<p>Formato de formulário inválido.</p>'),415)
        form = parse_qs(self.rfile.read(size).decode('utf-8',errors='replace'),keep_blank_values=True)
        if self.new_cookie or not compare_digest(form_val(form,'_csrf'),self.csrf):
            return self.send_content(layout(path,'<section class="panel article-panel"><h1>Formulário expirado</h1><p>Atualize a página e tente novamente.</p></section>'),403)
        with connect() as con:
            if path == '/participantes':
                name, group = form_val(form,'nome'), form_val(form,'turma')
                if not (1 <= len(name) <= 120) or len(group) > 80:
                    return self.show(path,people_page(con,self.csrf),'Participantes',error='Informe um nome válido, com até 120 caracteres.')
                con.execute('INSERT INTO participantes(nome,turma) VALUES (?,?)',(name,group))
                return self.redirect('/participantes?ok=1')
            if match := re.fullmatch(r'/participantes/(\d+)/excluir',path):
                pid = int(match.group(1))
                used = con.execute('SELECT 1 FROM inscricoes WHERE participante_id=? UNION SELECT 1 FROM emprestimos WHERE participante_id=? LIMIT 1',(pid,pid)).fetchone()
                if used:
                    return self.show(path,people_page(con,self.csrf),'Participantes',error='Não é possível excluir um participante com histórico de presenças ou empréstimos.')
                con.execute('DELETE FROM participantes WHERE id=?',(pid,))
                return self.redirect('/participantes?ok=1')
            if path == '/atividades/nova' or (match := re.fullmatch(r'/atividades/(\d+)/editar',path)):
                edit_id = int(match.group(1)) if path != '/atividades/nova' else None
                if edit_id and not con.execute('SELECT 1 FROM atividades WHERE id=?',(edit_id,)).fetchone():
                    return self.not_found()
                fields = {key:form_val(form,key) for key in ['titulo','data','descricao']}
                raw = form.get('presentes',[])
                selected = {int(v) for v in raw if v.isdigit()}
                error = ''
                if not fields['titulo'] or len(fields['titulo'])>120:
                    error = 'Informe o nome da atividade (até 120 caracteres).'
                elif len(fields['descricao']) > 800:
                    error = 'A descrição pode ter no máximo 800 caracteres.'
                else:
                    try:
                        if datetime.strptime(fields['data'],'%Y-%m-%d').strftime('%Y-%m-%d') != fields['data']:
                            raise ValueError
                    except ValueError:
                        error = 'Selecione uma data válida para a atividade.'
                allowed = {p['id'] for p in get_people(con)}
                if not error and (not allowed or len(raw)!=len(selected) or selected - allowed):
                    error = 'Cadastre participantes ou atualize a página para selecionar presenças válidas.'
                if not error:
                    duplicate = con.execute('SELECT id FROM atividades WHERE titulo = ? COLLATE NOCASE AND data=? AND id!=? LIMIT 1', (fields['titulo'],fields['data'],edit_id or -1)).fetchone()
                    if duplicate:
                        error = 'Esta atividade já foi registrada nessa data. Consulte o registro existente em Atividades e Presenças.'
                if error:
                    return self.show(path,activity_form(con,self.csrf,fields,selected,edit_id=edit_id),'Registrar atividade',error=error)
                if edit_id:
                    con.execute('UPDATE atividades SET titulo=?,data=?,descricao=?,presenca_registrada=1 WHERE id=?',
                                (fields['titulo'],fields['data'],fields['descricao'],edit_id))
                    con.execute('DELETE FROM inscricoes WHERE atividade_id=?',(edit_id,))
                    aid = edit_id
                else:
                    aid = con.execute('''INSERT INTO atividades(titulo,data,horario,responsavel,local,categoria,descricao,presenca_registrada)
                           VALUES (?,?,'','','','Educação',?,1)''',(fields['titulo'],fields['data'],fields['descricao'])).lastrowid
                con.executemany('INSERT INTO inscricoes(atividade_id,participante_id,presente) VALUES (?,?,?)',
                                [(aid,p['id'],int(p['id'] in selected)) for p in get_people(con)])
                return self.redirect(f'/atividades/{aid}?salvo=1')
            if path == '/biblioteca/livros':
                title,author,category,qty = (form_val(form,k) for k in ['titulo','autor','categoria','quantidade'])
                if not title or not author or len(title)>160 or len(author)>120 or category not in ('Educação','Literatura','Infantil','Tecnologia','Outros') or not qty.isdigit() or not (1<=int(qty)<=9999):
                    return self.show(path,library_page(con,self.csrf),'Biblioteca',error='Preencha os dados do livro e informe uma quantidade válida.')
                con.execute('INSERT INTO livros(titulo,autor,categoria,quantidade) VALUES (?,?,?,?)',(title,author,category,int(qty)))
                return self.redirect('/biblioteca?ok=1')
            if path == '/biblioteca/emprestimos':
                raw_book,raw_person = form_val(form,'livro_id'),form_val(form,'participante_id')
                if not (raw_book.isdigit() and raw_person.isdigit()):
                    return self.show(path,library_page(con,self.csrf),'Biblioteca',error='Selecione um livro e um participante válidos.')
                book_id, person_id = int(raw_book), int(raw_person)
                item = con.execute('SELECT quantidade FROM livros WHERE id=?',(book_id,)).fetchone()
                person = con.execute('SELECT id FROM participantes WHERE id=?',(person_id,)).fetchone()
                loans = con.execute('SELECT COUNT(*) FROM emprestimos WHERE livro_id=? AND devolvido_em IS NULL',(book_id,)).fetchone()[0]
                if not item or not person or item['quantidade'] <= loans:
                    return self.show(path,library_page(con,self.csrf),'Biblioteca',error='Livro indisponível ou participante não encontrado.')
                con.execute('INSERT INTO emprestimos(livro_id,participante_id,retirado_em) VALUES (?,?,?)',(book_id,person_id,date.today().isoformat()))
                return self.redirect('/biblioteca?ok=1')
            if match := re.fullmatch(r'/biblioteca/emprestimos/(\d+)/devolver',path):
                cur = con.execute('UPDATE emprestimos SET devolvido_em=? WHERE id=? AND devolvido_em IS NULL',(date.today().isoformat(),int(match.group(1))))
                if not cur.rowcount:
                    return self.not_found()
                return self.redirect('/biblioteca?ok=1')
            self.not_found()


def main():
    init_db()
    server = ThreadingHTTPServer((HOST,PORT), Handler)
    print('\nMlks da Vila — MVP em Python')
    print(f'Acesse: http://{HOST}:{PORT}')
    print(f'Banco de dados: {DB_FILE}')
    print('Para encerrar, pressione Ctrl+C.\n')
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print('\nServidor encerrado.')
    finally:
        server.server_close()


if __name__ == '__main__':
    main()
