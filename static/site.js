/* Mlks da Vila — versão estática para GitHub Pages.
 * Dados locais por navegador; não sincroniza participantes entre dispositivos.
 */
(() => {
  'use strict';
  const STORAGE_KEY = 'mlks-da-vila:pages:v1';
  const $ = (sel, root = document) => root.querySelector(sel);
  const main = $('#conteudo');
  const nav = $('.sidebar-nav');
  const navButton = $('.nav-toggle');
  const icons = {
    users: '<path d="M16 21v-2a4 4 0 0 0-4-4H6a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M22 21v-2a4 4 0 0 0-3-3.87M16 3.13a4 4 0 0 1 0 7.75"/>',
    list: '<path d="M8 6h13M8 12h13M8 18h13M3 6h.01M3 12h.01M3 18h.01"/>',
    date: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/>',
    activity: '<rect x="3" y="5" width="18" height="16" rx="2"/><path d="M7 3v4M17 3v4M3 10h18"/><circle cx="9" cy="14" r="1"/><circle cx="15" cy="14" r="1"/>',
    books: '<path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H21V3H6.5A2.5 2.5 0 0 0 4 5.5z"/><path d="M4 19.5A2.5 2.5 0 0 0 6.5 22H21v-5"/><path d="M8 8h9M8 12h7"/>',
    check: '<path d="m4 12 5 5L20 6"/>',
    'check-circle': '<circle cx="12" cy="12" r="10"/><path d="m7 12 3 3 7-7"/>',
    'x-circle': '<circle cx="12" cy="12" r="10"/><path d="m8 8 8 8m0-8-8 8"/>',
    'arrow-right': '<path d="M5 12h14m-6-6 6 6-6 6"/>',
    'arrow-left': '<path d="M19 12H5m6 6-6-6 6-6"/>',
    plus: '<path d="M12 5v14M5 12h14"/>',
    info: '<circle cx="12" cy="12" r="10"/><path d="M12 11v6M12 7h.01"/>',
    trash: '<path d="M3 6h18M8 6V4h8v2m3 0-1 15H6L5 6m5 4v7m4-7v7"/>',
    return: '<path d="m9 14-4-4 4-4M5 10h9a5 5 0 0 1 0 10h-3"/>',
    shield: '<path d="M12 2 4 6v6c0 5 3 8 8 10 5-2 8-5 8-10V6z"/><path d="m9 12 2 2 4-4"/>'
  };
  const icon = (name, size=17) => `<svg class="icon" viewBox="0 0 24 24" width="${size}" height="${size}" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${icons[name] || icons.info}</svg>`;
  const esc = value => String(value == null ? '' : value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const isoToday = () => { const d = new Date(), offset=d.getTimezoneOffset(); return new Date(d.getTime()-offset*60000).toISOString().slice(0,10); };
  const fmtDate = date => { if(!/^\d{4}-\d{2}-\d{2}$/.test(String(date))) return esc(date); const [y,m,d]=date.split('-'); return `${d}/${m}/${y}`; };
  const normalized = s => String(s || '').trim().normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const initial = () => ({version:1, nextId:1, participants:[], activities:[], books:[], loans:[]});
  let database;
  let transientNotice = '';
  const save = () => { try { localStorage.setItem(STORAGE_KEY, JSON.stringify(database)); return true; } catch(err) { window.alert('O navegador não conseguiu salvar os dados. Confira o espaço e as permissões de armazenamento.'); return false; } };
  const load = () => { try { const raw=localStorage.getItem(STORAGE_KEY); if(!raw) return initial(); const obj=JSON.parse(raw); if(!obj || obj.version!==1 || !['participants','activities','books','loans'].every(k=>Array.isArray(obj[k]))) throw Error('Estrutura incompatível'); obj.nextId=Number.isInteger(obj.nextId)?obj.nextId:1; return obj; } catch(err) { window.alert('Os dados salvos neste navegador não puderam ser carregados. Uma sessão vazia será aberta; nenhum dado antigo foi substituído.'); return initial(); } };
  database = load();
  const newId = () => database.nextId++;
  const navigate = path => { if(location.hash === '#'+path) render(); else location.hash = '#'+path; };
  const route = () => decodeURI((location.hash || '#/').slice(1)).split('?')[0] || '/';
  const setNav = path => {
    nav.querySelectorAll('.nav-item').forEach(el => {
      const target = el.getAttribute('href')?.slice(1);
      const active = target === '/' ? path==='/' : path===target || (target==='/atividades' && (path.startsWith('/atividades')||path==='/participantes'));
      el.classList.toggle('active',active);
      if(active) el.setAttribute('aria-current','page'); else el.removeAttribute('aria-current');
    });
  };
  const closeMenu = () => { document.body.classList.remove('menu-open'); navButton.setAttribute('aria-expanded','false'); };
  navButton.addEventListener('click', () => { const open=document.body.classList.toggle('menu-open'); navButton.setAttribute('aria-expanded',String(open)); });
  $('#menu-overlay').addEventListener('click',closeMenu);
  nav.addEventListener('click', e => { if(e.target.closest('a')) closeMenu(); });
  document.addEventListener('keydown',e=>{if(e.key==='Escape') closeMenu();});
  function crumbs(items = []) { let html='<a href="#/">Início</a>'; for(const item of items) html+=`<span class="crumb-arrow">›</span>${item.href?`<a href="#${esc(item.href)}">${esc(item.name)}</a>`:esc(item.name)}`; return `<div class="breadcrumbs">${html}</div>`; }
  const heading = (title,subtitle,button='') => `<div class="section-heading"><div><h1>${esc(title)}</h1><p>${esc(subtitle)}</p></div>${button}</div>`;
  const link = (path,text,style='neutral',ico='') => `<a href="#${path}" class="btn btn-${style}">${ico?icon(ico):''}${esc(text)}</a>`;
  const alert = (text,kind='error') => `<div class="notice notice-${kind}" role="alert">${icon('info')}<span>${esc(text)}</span></div>`;
  function homePage() { return `${crumbs()}<section class="welcome"><h1>Bem-vindo ao Mlks da Vila</h1><p>Selecione uma opção para continuar</p><div class="entry-cards">
    <article class="entry-card"><div class="entry-icon entry-icon-blue">${icon('activity',78)}</div><h2>Atividades e Presenças</h2><p>Cadastre atividades, registre participantes e consulte o total de presenças.</p><a href="#/atividades/nova" class="btn btn-blue entry-btn">Acessar atividades ${icon('arrow-right',21)}</a></article>
    <article class="entry-card"><div class="entry-icon entry-icon-green">${icon('books',78)}</div><h2>Biblioteca</h2><p>Consulte livros, registre empréstimos e acompanhe devoluções.</p><a href="#/biblioteca" class="btn btn-green entry-btn">Acessar biblioteca ${icon('arrow-right',21)}</a></article>
    </div></section>`; }
  function activityForm(id=null) {
    const data=id?database.activities.find(a=>a.id===id):null;
    if(id!==null && !data) return notFound();
    const people = id===null ? database.participants : data.participantIds.map(pid=>database.participants.find(p=>p.id===pid)).filter(Boolean);
    const checked = new Set(data?.presentIds || []);
    const rows=people.length?people.map((p,i)=>`<tr class="person-row"><td class="center">${i+1}</td><td><label class="person-label"><input type="checkbox" name="presentes" value="${p.id}" ${checked.has(p.id)?'checked':''}><span>${esc(p.name)}</span></label></td><td><span class="state-label ${checked.has(p.id)?'state-present':'state-absent'}">${checked.has(p.id)?'Presente':'Ausente'}</span></td></tr>`).join(''):`<tr><td colspan="3" class="empty-row">Nenhum participante cadastrado. <a href="#/participantes">Cadastre participantes</a> antes de registrar a atividade.</td></tr>`;
    const title=id===null?'Registrar atividade e presenças':'Editar atividade e presenças';
    return `${crumbs([{name:'Atividades e Presenças',href:'/atividades'},{name:id===null?'Nova atividade':'Editar atividade'}])}${heading(title,'Preencha os dados da atividade e marque os participantes presentes.',link('/atividades','Voltar ao menu','neutral','arrow-left'))}<form data-form="activity" data-id="${id ?? ''}" class="activity-form">
      <section class="panel entry-section"><h2>Dados da atividade</h2><div class="field-grid"><label class="field"><span>Nome da atividade <b class="required">*</b></span><input name="titulo" maxlength="120" required value="${esc(data?.title || '')}" placeholder="Ex.: Aula de inglês"></label><label class="field"><span>Data da atividade <b class="required">*</b></span><input type="date" name="data" required value="${esc(data?.date || isoToday())}"></label></div><label class="field"><span>Descrição (opcional)</span><textarea name="descricao" maxlength="800" rows="3" placeholder="Atividade educativa para crianças e adolescentes.">${esc(data?.description || '')}</textarea></label></section>
      <section class="panel attendance-section"><div class="panel-heading"><div><h2>Participantes</h2><p>Marque quem compareceu à atividade.</p></div><span class="count-badge">${icon('users')} <span id="presence-counter" aria-live="polite">${checked.size} de ${people.length} participantes presentes</span></span></div><div class="table-scroll"><table class="data-table presence-table"><thead><tr><th class="center col-num">#</th><th>Nome</th><th>Situação</th></tr></thead><tbody>${rows}</tbody></table></div><div class="panel-actions"><a href="#/atividades" data-cancel="activity" class="btn btn-neutral">Cancelar</a><div class="action-right"><button class="btn btn-blue" type="submit" ${!people.length?'disabled':''}>${id===null?'Salvar atividade e presenças':'Salvar alterações'}</button><small>${icon('info',13)} Confira as informações antes de salvar.</small></div></div></section>
      </form>`;
  }
  function activityResult(id) {
    const activity=database.activities.find(a=>a.id===id);
    if(!activity) return notFound();
    const people=activity.participantIds.map(pid=>database.participants.find(p=>p.id===pid)).filter(Boolean);
    const present=people.filter(p=>activity.presentIds.includes(p.id)).length, absent=people.length-present;
    const saved=(location.hash||'').includes('?salvo=1');
    const rows=people.map((p,i)=>`<tr><td class="center">${i+1}</td><td>${esc(p.name)}</td><td class="status-cell"><span class="presence-result ${activity.presentIds.includes(p.id)?'present':'absent'}">${icon(activity.presentIds.includes(p.id)?'check-circle':'x-circle',15)}<span>${activity.presentIds.includes(p.id)?'Presente':'Ausente'}</span></span></td></tr>`).join('') || '<tr><td colspan="3" class="empty-row">Nenhum participante nesta atividade.</td></tr>';
    return `${crumbs([{name:'Atividades e Presenças',href:'/atividades'},{name:'Resultado'}])}${heading('Resultado do registro','Confira os dados da atividade e o total de participantes presentes.',link(`/atividades/${id}/editar`,'Editar atividade','neutral','activity'))}${saved?`<div class="success-banner" role="status"><span class="success-emblem">${icon('check',30)}</span><span><strong>Atividade salva com sucesso!</strong><small>Os dados da atividade e das presenças foram registrados.</small></span></div>`:''}
    <section class="panel outcome-panel"><h2>Resumo da atividade</h2><div class="outcome-grid"><div class="outcome-details"><div class="info-line"><span class="info-icon">${icon('activity')}</span><span><small>Atividade</small><strong>${esc(activity.title)}</strong></span></div><div class="info-line"><span class="info-icon">${icon('date')}</span><span><small>Data</small><strong>${fmtDate(activity.date)}</strong></span></div><div class="info-line"><span class="info-icon">${icon('list')}</span><span><small>Descrição</small><strong>${esc(activity.description||'Nenhuma descrição informada.')}</strong></span></div></div><div class="outcome-metrics"><div class="metric-main">${icon('users',27)}<strong>${present} de ${people.length}</strong><span>participantes presentes</span></div><div class="metric-breakdown"><div>${icon('users',20)}<strong>${people.length}</strong><small>Participantes<br>registrados</small></div><div class="metric-good">${icon('check-circle',20)}<strong>${present}</strong><small>Presentes</small></div><div class="metric-bad">${icon('x-circle',20)}<strong>${absent}</strong><small>Ausentes</small></div></div></div></div></section>
    <section class="panel results-panel"><h2>Presenças registradas</h2><div class="table-scroll"><table class="data-table result-table"><thead><tr><th class="col-num center">#</th><th>Nome</th><th>Situação</th></tr></thead><tbody>${rows}</tbody></table></div><div class="panel-actions three-actions">${link('/','Voltar ao menu','neutral','arrow-left')}<div class="action-cluster">${link('/atividades/nova','Registrar outra atividade','outline','activity')}${link('/atividades','Consultar presenças','blue','list')}</div></div></section>`;
  }
  function activityList() {
    const data=[...database.activities].sort((a,b)=>b.date.localeCompare(a.date)||b.id-a.id);
    const rows=data.map(a=>`<tr><td><a class="name-link" href="#/atividades/${a.id}">${esc(a.title)}</a><small class="row-description">${esc(a.description?.slice(0,95)||'Sem descrição')}</small></td><td>${fmtDate(a.date)}</td><td><span class="badge badge-ok">${a.presentIds.length} de ${a.participantIds.length} presentes</span></td><td><div class="row-actions"><a class="table-action" href="#/atividades/${a.id}">Consultar ${icon('arrow-right',16)}</a><a class="table-action" href="#/atividades/${a.id}/editar">Editar</a></div></td></tr>`).join('') || '<tr><td colspan="4" class="empty-row">Ainda não existem atividades cadastradas. Registre a primeira pelo botão acima.</td></tr>';
    return `${crumbs([{name:'Atividades e Presenças'}])}${heading('Atividades e Presenças','Gerencie ações realizadas pela ONG e consulte seus registros.',link('/atividades/nova','Registrar atividade','blue','plus'))}<section class="panel list-section"><div class="panel-heading"><div><h2>Atividades cadastradas</h2><p>Abra um registro para consultar presentes e ausentes.</p></div><span class="soft-count">${data.length} atividade(s)</span></div><div class="table-scroll"><table class="data-table activities-table"><thead><tr><th>Atividade</th><th>Data</th><th>Presenças</th><th></th></tr></thead><tbody>${rows}</tbody></table></div><div class="sub-actions"><a href="#/participantes">${icon('users')} Gerenciar participantes ${icon('arrow-right')}</a></div></section>`;
  }
  function participantsPage() {
    const rows=[...database.participants].sort((a,b)=>a.name.localeCompare(b.name,'pt-BR')).map(p=>`<tr><td>${esc(p.name)}</td><td>${esc(p.group || '—')}</td><td class="actions-cell"><button type="button" class="icon-btn danger" data-delete-participant="${p.id}" aria-label="Excluir ${esc(p.name)}">${icon('trash')}</button></td></tr>`).join('') || '<tr><td colspan="3" class="empty-row">Nenhum participante cadastrado. Cadastre pessoas para registrar presenças.</td></tr>';
    return `${crumbs([{name:'Atividades e Presenças',href:'/atividades'},{name:'Participantes'}])}${heading('Participantes','Cadastre as pessoas que participam das ações da ONG.',link('/atividades','Voltar às atividades','neutral','arrow-left'))}<div class="two-col"><section class="panel"><h2>Novo participante</h2><form data-form="participant" class="vertical-form"><label class="field"><span>Nome completo <b class="required">*</b></span><input name="nome" maxlength="120" required placeholder="Nome do participante"></label><label class="field"><span>Turma ou grupo (opcional)</span><input name="turma" maxlength="80" placeholder="Ex.: Turma A"></label><button class="btn btn-blue" type="submit">${icon('plus')} Adicionar participante</button></form></section><section class="panel"><div class="panel-heading"><h2>Participantes cadastrados</h2><span class="soft-count">${database.participants.length}</span></div><div class="table-scroll"><table class="data-table"><thead><tr><th>Nome</th><th>Turma</th><th></th></tr></thead><tbody>${rows}</tbody></table></div></section></div>`;
  }
  function libraryPage() {
    const books=[...database.books].sort((a,b)=>a.title.localeCompare(b.title,'pt-BR'));
    const active=database.loans.filter(l=>!l.returnDate);
    const countAvailable=id=>{const b=database.books.find(x=>x.id===id);return b?Math.max(0,b.quantity-active.filter(x=>x.bookId===id).length):0;};
    const bookRows=books.map(b=>`<tr><td><strong>${esc(b.title)}</strong><small class="row-description">${esc(b.author||'Autor não informado')} · ${esc(b.category||'Geral')}</small></td><td>${b.quantity}</td><td>${countAvailable(b.id)}</td></tr>`).join('') || '<tr><td class="empty-row" colspan="3">Nenhum livro cadastrado.</td></tr>';
    const loanRows=active.map(l=>{const book=database.books.find(b=>b.id===l.bookId);const person=database.participants.find(p=>p.id===l.participantId);return `<tr><td>${esc(book?.title||'Livro indisponível')}<small class="row-description">${esc(person?.name||'Participante não encontrado')}</small></td><td>${fmtDate(l.loanDate)}</td><td class="actions-cell"><button type="button" class="btn btn-outline btn-small" data-return="${l.id}">${icon('return',15)} Devolver</button></td></tr>`;}).join('')||'<tr><td colspan="3" class="empty-row">Nenhum empréstimo em aberto.</td></tr>';
    const bookOptions=books.filter(b=>countAvailable(b.id)>0).map(b=>`<option value="${b.id}">${esc(b.title)} (${countAvailable(b.id)} disponível(is))</option>`).join('');
    const peopleOptions=database.participants.map(p=>`<option value="${p.id}">${esc(p.name)}</option>`).join('');
    return `${crumbs([{name:'Biblioteca'}])}${heading('Biblioteca','Consulte o acervo e acompanhe empréstimos e devoluções.')}<div class="two-col library-grid"><section class="panel"><h2>Cadastrar livro</h2><form data-form="book" class="vertical-form"><label class="field"><span>Título <b class="required">*</b></span><input name="titulo" maxlength="160" required placeholder="Nome do livro"></label><label class="field"><span>Autor</span><input name="autor" maxlength="120" placeholder="Autor(a)"></label><label class="field"><span>Categoria</span><input name="categoria" maxlength="80" placeholder="Educação, literatura..."></label><label class="field"><span>Quantidade de exemplares <b class="required">*</b></span><input type="number" name="quantidade" min="1" max="1000" value="1" required></label><button class="btn btn-green" type="submit">${icon('plus')} Adicionar livro</button></form></section><section class="panel"><div class="panel-heading"><h2>Acervo da biblioteca</h2><span class="soft-count">${books.length} título(s)</span></div><div class="table-scroll"><table class="data-table"><thead><tr><th>Livro</th><th>Total</th><th>Disponíveis</th></tr></thead><tbody>${bookRows}</tbody></table></div></section></div><div class="two-col library-grid extra-row"><section class="panel"><h2>Registrar empréstimo</h2><form data-form="loan" class="vertical-form"><label class="field"><span>Livro <b class="required">*</b></span><select name="livro" required ${bookOptions?'':'disabled'}><option value="">Selecione...</option>${bookOptions}</select></label><label class="field"><span>Participante <b class="required">*</b></span><select name="participante" required ${peopleOptions?'':'disabled'}><option value="">Selecione...</option>${peopleOptions}</select></label><button class="btn btn-blue" type="submit" ${bookOptions&&peopleOptions?'':'disabled'}>Registrar empréstimo</button>${!peopleOptions?'<small class="muted">Cadastre participantes antes de registrar um empréstimo.</small>':''}</form></section><section class="panel"><div class="panel-heading"><h2>Empréstimos em aberto</h2><span class="soft-count">${active.length}</span></div><div class="table-scroll"><table class="data-table"><thead><tr><th>Livro / participante</th><th>Retirada</th><th></th></tr></thead><tbody>${loanRows}</tbody></table></div></section></div>`;
  }
  function aboutPage() { return `${crumbs([{name:'Sobre'}])}${heading('Sobre o projeto','Organizando oportunidades, fortalecendo a comunidade.')}<section class="panel article-panel"><h2>O Mlks da Vila</h2><p>O Mlks da Vila é um projeto comunitário voltado à organização de atividades e ao incentivo à educação. O sistema facilita o cadastro de ações, o acompanhamento de participantes, o registro de presenças e o controle da biblioteca.</p><h2>ODS 4 — Educação de Qualidade</h2><p>O MVP apoia a organização e o acompanhamento das atividades educacionais, ajudando os voluntários a manter registros claros e acessíveis.</p><h2>Sobre esta versão online</h2><p>Os dados ficam salvos somente neste navegador, neste dispositivo. O GitHub Pages não fornece um banco de dados compartilhado. Não cadastre dados pessoais sensíveis nesta demonstração pública.</p></section>`; }
  function helpPage() { return `${crumbs([{name:'Ajuda'}])}${heading('Ajuda','Como usar o Mlks da Vila.')}<section class="panel article-panel"><h2>Primeiros passos</h2><ol><li>Entre em <a href="#/participantes">Participantes</a> e cadastre as pessoas da ONG.</li><li>Em <a href="#/atividades/nova">Atividades e Presenças</a>, informe o nome, a data e marque quem compareceu.</li><li>Clique em <strong>Salvar atividade e presenças</strong> para consultar o resumo do registro.</li><li>Na <a href="#/biblioteca">Biblioteca</a>, cadastre livros e controle empréstimos e devoluções.</li></ol><h2>Onde os dados são salvos?</h2><p>Somente no armazenamento local deste navegador. Cada aparelho possui seus próprios registros. Limpar os dados do site pode apagá-los.</p><div class="data-tools"><button class="btn btn-outline" type="button" data-export="1">Exportar cópia de segurança (.json)</button><label class="btn btn-neutral import-label">Importar cópia (.json)<input type="file" id="import-backup" accept=".json,application/json" hidden></label></div><p class="muted">A importação substitui todos os registros locais deste navegador. Não compartilhe cópias contendo dados pessoais.</p></section>`; }
  const notFound=()=>`${crumbs([{name:'Página não encontrada'}])}${heading('Página não encontrada','Não localizamos o conteúdo solicitado.')}${link('/','Voltar ao início','blue','arrow-left')}`;
  function render() {
    const path=route();setNav(path);closeMenu();
    let page;
    const result=path.match(/^\/atividades\/(\d+)$/),edit=path.match(/^\/atividades\/(\d+)\/editar$/);
    if(path==='/') page=homePage();
    else if(path==='/atividades')page=activityList();
    else if(path==='/atividades/nova')page=activityForm();
    else if(result)page=activityResult(Number(result[1]));
    else if(edit)page=activityForm(Number(edit[1]));
    else if(path==='/participantes')page=participantsPage();
    else if(path==='/biblioteca')page=libraryPage();
    else if(path==='/sobre')page=aboutPage();
    else if(path==='/ajuda')page=helpPage();
    else page=notFound();
    main.innerHTML=(transientNotice?alert(transientNotice,'success'):'')+page;
    transientNotice='';
    document.title=(path==='/'?'Início':path.startsWith('/atividades')?'Atividades e Presenças':path.slice(1).replace(/^./,c=>c.toUpperCase()))+' | Mlks da Vila';
    window.scrollTo({top:0,behavior:'instant'});
  }
  function formError(form,message) { let previous=form.querySelector('.notice-error'); if(previous) previous.remove(); form.insertAdjacentHTML('afterbegin',alert(message)); form.querySelector('.notice-error').scrollIntoView({block:'nearest'}); }
  function updateCount() { const form=$('form[data-form="activity"]');if(!form)return;const checks=[...form.querySelectorAll('input[name="presentes"]')];const yes=checks.filter(c=>c.checked).length;$('#presence-counter').textContent=`${yes} de ${checks.length} participantes presentes`;for(const c of checks){const el=c.closest('tr')?.querySelector('.state-label');if(el){el.textContent=c.checked?'Presente':'Ausente';el.classList.toggle('state-present',c.checked);el.classList.toggle('state-absent',!c.checked);}} }
  main.addEventListener('change',e=>{if(e.target.matches('input[name="presentes"]'))updateCount();if(e.target.id==='import-backup')importBackup(e.target.files?.[0]);});
  main.addEventListener('click',e=>{
    const cancel=e.target.closest('[data-cancel="activity"]');
    if(cancel){const form=$('form[data-form="activity"]');const title=form?.elements.titulo.value.trim(),desc=form?.elements.descricao.value.trim(),checked=form?.querySelector('input[name="presentes"]:checked');if((title||desc||checked)&&!confirm('Cancelar o cadastro? As informações não salvas serão perdidas.'))e.preventDefault();return;}
    const del=e.target.closest('[data-delete-participant]');
    if(del){const id=Number(del.dataset.deleteParticipant);const p=database.participants.find(x=>x.id===id);if(!p)return;
      if(database.activities.some(a=>a.participantIds.includes(id)) || database.loans.some(l=>l.participantId===id)){window.alert('Este participante possui atividades ou empréstimos vinculados e não pode ser excluído.');return;}
      if(confirm(`Excluir o participante ${p.name}?`)){const backup=JSON.stringify(database);database.participants=database.participants.filter(x=>x.id!==id);if(save())render();else database=JSON.parse(backup);}return;}
    const ret=e.target.closest('[data-return]');
    if(ret){const l=database.loans.find(x=>x.id===Number(ret.dataset.return));if(!l||l.returnDate)return;if(confirm('Confirmar devolução deste livro?')){const backup=JSON.stringify(database);l.returnDate=isoToday();if(save()){transientNotice='Devolução registrada com sucesso.';render();}else database=JSON.parse(backup);}return;}
    if(e.target.closest('[data-export]'))exportBackup();
  });
  main.addEventListener('submit',e=>{
    const form=e.target.closest('form[data-form]'); if(!form)return;e.preventDefault();if(!form.reportValidity())return;
    const fd=new FormData(form),kind=form.dataset.form;let backup=JSON.stringify(database);
    if(kind==='participant'){
      const name=String(fd.get('nome')||'').trim(),group=String(fd.get('turma')||'').trim();
      if(name.length<2||name.length>120){formError(form,'Informe um nome com 2 a 120 caracteres.');return;}
      if(database.participants.some(p=>normalized(p.name)===normalized(name))){formError(form,'Este participante já foi cadastrado.');return;}
      database.participants.push({id:newId(),name,group:group.slice(0,80)});if(save()){transientNotice='Participante cadastrado com sucesso.';render();}else database=JSON.parse(backup);return;
    }
    if(kind==='activity'){
      const title=String(fd.get('titulo')||'').trim(),date=String(fd.get('data')||''),description=String(fd.get('descricao')||'').trim();
      const editId=Number(form.dataset.id)||null;
      if(title.length<2||title.length>120){formError(form,'Informe o nome da atividade com 2 a 120 caracteres.');return;}
      if(!/^\d{4}-\d{2}-\d{2}$/.test(date)||Number.isNaN(new Date(date+'T12:00:00').getTime())){formError(form,'Informe uma data válida.');return;}
      if(database.activities.some(a=>a.id!==editId&&normalized(a.title)===normalized(title)&&a.date===date)){formError(form,'Já existe uma atividade com este nome nesta data.');return;}
      const presentIds=fd.getAll('presentes').map(Number),activity=editId?database.activities.find(a=>a.id===editId):null;
      if(editId && !activity){formError(form,'Atividade não localizada.');return;}
      const peopleIds=activity?activity.participantIds:database.participants.map(p=>p.id);
      if(!peopleIds.length){formError(form,'Cadastre participantes antes de salvar a atividade.');return;}
      if(presentIds.some(id=>!peopleIds.includes(id))){formError(form,'Há uma seleção de participante inválida.');return;}
      const obj={id:editId||newId(),title,date,description:description.slice(0,800),participantIds:peopleIds,presentIds:[...new Set(presentIds)]};
      if(activity)Object.assign(activity,obj);else database.activities.push(obj);
      if(save())navigate(`/atividades/${obj.id}?salvo=1`);else database=JSON.parse(backup);return;
    }
    if(kind==='book'){
      const title=String(fd.get('titulo')||'').trim(),author=String(fd.get('autor')||'').trim(),category=String(fd.get('categoria')||'').trim(),quantity=Number(fd.get('quantidade'));
      if(title.length<2||title.length>160||!Number.isInteger(quantity)||quantity<1||quantity>1000){formError(form,'Confira o título e a quantidade (de 1 a 1000).');return;}
      if(database.books.some(b=>normalized(b.title)===normalized(title))){formError(form,'Esse título já está cadastrado.');return;}
      database.books.push({id:newId(),title,author:author.slice(0,120),category:category.slice(0,80),quantity});if(save()){transientNotice='Livro cadastrado com sucesso.';render();}else database=JSON.parse(backup);return;
    }
    if(kind==='loan'){
      const bookId=Number(fd.get('livro')),participantId=Number(fd.get('participante'));const book=database.books.find(b=>b.id===bookId);
      const count=database.loans.filter(l=>l.bookId===bookId&&!l.returnDate).length;
      if(!book || !database.participants.some(p=>p.id===participantId) || count>=book.quantity){formError(form,'Livro ou participante inválido, ou sem exemplares disponíveis.');return;}
      database.loans.push({id:newId(),bookId,participantId,loanDate:isoToday(),returnDate:null});if(save()){transientNotice='Empréstimo registrado com sucesso.';render();}else database=JSON.parse(backup);
    }
  });
  function exportBackup(){const blob=new Blob([JSON.stringify(database,null,2)],{type:'application/json'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=`mlks-da-vila-backup-${isoToday()}.json`;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  async function importBackup(file){if(!file)return;try{if(file.size>5*1024*1024)throw Error('Arquivo maior que 5 MB.');const data=JSON.parse(await file.text());if(!data||data.version!==1||!['participants','activities','books','loans'].every(k=>Array.isArray(data[k]))||!Number.isInteger(data.nextId)||data.nextId<1)throw Error('O arquivo não é um backup compatível.');if(data.participants.length>10000||data.activities.length>10000||data.books.length>10000||data.loans.length>10000)throw Error('O arquivo possui registros demais.');if(!confirm('Importar esta cópia irá SUBSTITUIR todos os dados deste navegador. Deseja continuar?'))return;const previous=database;database=data;if(save()){transientNotice='Cópia de segurança importada.';navigate('/');}else database=previous;}catch(err){window.alert('Não foi possível importar: '+err.message);} }
  window.addEventListener('hashchange',render);
  if(!location.hash)location.replace(location.pathname+location.search+'#/');else render();
})();
