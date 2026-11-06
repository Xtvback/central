/* Estúdio Editorial · André M. Fernandes · aplicação estática e sem credenciais */
(function () {
  'use strict';
  const DATA = window.EDITORIAL_DATA;
  if (!DATA) { document.body.textContent = 'Não foi possível carregar os dados editoriais.'; return; }
  const KEY = 'amf_estudio_editorial_v1';
  const $ = (sel, root=document) => root.querySelector(sel);
  const $$ = (sel, root=document) => Array.from(root.querySelectorAll(sel));
  const text = s => String(s == null ? '' : s);
  const esc = s => text(s).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
  const today = () => {
    const parts = new Intl.DateTimeFormat('en-GB',{timeZone:'Europe/Lisbon',year:'numeric',month:'2-digit',day:'2-digit'}).formatToParts(new Date());
    const v = {}; parts.forEach(p => { v[p.type] = p.value; });
    return v.year + '-' + v.month + '-' + v.day;
  };
  const addDays = (d, count) => {
    const t = new Date(d + 'T12:00:00Z'); t.setUTCDate(t.getUTCDate() + count); return t.toISOString().slice(0,10);
  };
  const format = (d, opts={day:'numeric',month:'long',year:'numeric'}) =>
    new Intl.DateTimeFormat('pt-PT', {...opts,timeZone:'UTC'}).format(new Date(d+'T12:00:00Z'));
  const catNames = {escrita:'Escrita',vida:'Vida e relações',debate:'Dilema',livros:'Livros',familia:'Família',local:'Plano local'};
  const blank = () => ({done:{},extra:{},customPosts:[],notes:{},reviews:{},results:{}});
  let state = blank();
  try { const parsed = JSON.parse(localStorage.getItem(KEY) || 'null'); if(parsed && typeof parsed==='object') state = Object.assign(blank(),parsed); } catch(e) {}
  const persist = () => { try {localStorage.setItem(KEY,JSON.stringify(state));} catch(e) {toast('Não foi possível guardar neste navegador.');} };
  const allPosts = () => DATA.scheduled.concat(state.customPosts || []).sort((a,b) => (a.date+a.time).localeCompare(b.date+b.time));
  const fromId = id => allPosts().find(p => p.id===id);
  const readableTime = p => p.time || 'Por definir';
  const niceDay = d => format(d,{weekday:'long',day:'numeric',month:'long'});
  const shortDay = d => format(d,{day:'numeric',month:'short'});
  let activeView='inicio', displayMonth=today().slice(0,7), selectedDate=today(), routineDate=today(), toastTimer=null;
  function toast(message) { const el=$('#toast'); el.textContent=message; el.classList.add('show'); clearTimeout(toastTimer); toastTimer=setTimeout(()=>el.classList.remove('show'),3200); }
  function navigate(view) {
    if(!$('#view-'+view)) return;
    activeView=view;
    $$('.view').forEach(el=>el.classList.toggle('active',el.id==='view-'+view));
    $$('.nav-link').forEach(el=>el.classList.toggle('active',el.dataset.view===view));
    $('#crumb-current').textContent={inicio:'Visão geral',calendario:'Calendário',publicacoes:'Publicações',rotina:'O meu dia',resultados:'Resultados'}[view];
    if(view==='calendario') renderCalendar();
    if(view==='publicacoes') renderPosts();
    if(view==='rotina') renderRoutine();
    if(view==='resultados') renderResults();
    if(view==='inicio') renderHome();
    window.scrollTo({top:0,behavior:'auto'});
    try {history.replaceState(null,'','#'+view);}catch(e){}
  }
  function tasksFor(date) {
    const posts=allPosts(), list=[];
    const datePosts=posts.filter(p=>p.date===date);
    datePosts.forEach(p=>{
      if (p.revision && !state.reviews[p.id]) list.push({id:'review-'+p.id,title:'Decidir se manténs o texto de «'+p.title+'»',detail:'Há uma proposta editorial. A revisão não está aplicada no Metricool.',post:p.id});
      list.push({id:'check-'+p.id,title:'Confirmar o post «'+p.title+'» no Metricool',detail:'Threads · '+readableTime(p)+(p.status==='local'?' · Planeado apenas neste site':' · Agendado no Metricool'),post:p.id});
      list.push({id:'reply-'+p.id,title:'Voltar para responder a quem comentar',detail:'Uma conversa genuína vale mais do que publicar e desaparecer.',post:p.id});
    });
    posts.filter(p=>addDays(p.date,1)===date).forEach(p=>list.push({id:'measure-'+p.id,title:'Ver o desempenho de «'+p.title+'»',detail:'Anotar visualizações, interações e evolução dos seguidores.'}));
    DATA.milestones.filter(m=>m.date===date).forEach((m,i)=>list.push({id:'milestone-'+i,title:m.title,detail:m.task}));
    if(new Date(date+'T12:00:00Z').getUTCDay()===0) list.push({id:'weekly',title:'Balanço leve da semana',detail:'15 minutos: o que gerou respostas, partilhas e seguidores? Sem obsessões.'});
    list.push({id:'presence',title:'Passar pelo Threads e participar numa conversa',detail:'5–10 minutos, se houver tempo. Comenta apenas temas que realmente te interessam.'});
    (state.extra[date] || []).forEach(t=>list.push({id:t.id,title:t.title,detail:'Adicionado por ti',custom:true}));
    return list;
  }
  function done(date, id) {return !!state.done[date+'|'+id];}
  function taskHtml(task,date) {
    const checked=done(date,task.id);
    return '<div class="task '+(checked?'checked':'')+'"><input type="checkbox" aria-label="Concluir tarefa" data-task="'+esc(task.id)+'" data-date="'+esc(date)+'" '+(checked?'checked':'')+'><label data-action="toggle-task" data-task="'+esc(task.id)+'" data-date="'+esc(date)+'"><span class="task-title">'+esc(task.title)+'</span><span class="task-meta">'+esc(task.detail)+'</span></label>'+(task.custom?'<button class="task-remove" data-action="remove-task" data-date="'+esc(date)+'" data-task="'+esc(task.id)+'" aria-label="Eliminar tarefa">×</button>':'')+'</div>';
  }
  function statsHtml(items) {return items.map(it=>'<div class="stat"><div class="stat-top"><span class="star">'+esc(it.icon)+'</span> '+esc(it.label)+'</div><b>'+esc(it.value)+'</b><small>'+esc(it.info)+'</small></div>').join('');}
  function nextScheduled() {return DATA.scheduled.find(p=>p.date>=today()) || null;}
  function renderHome() {
    $('#today-chip').textContent = format(today(),{weekday:'short',day:'numeric',month:'short'}).toUpperCase();
    $('#home-stats').innerHTML=statsHtml([
      {icon:'◷',label:'Threads agendados',value:DATA.scheduled.filter(p=>p.date>=today()).length,info:'Fotografia do Metricool · 6 nov.'},
      {icon:'✎',label:'Versões a rever',value:DATA.scheduled.filter(p=>p.revision && !state.reviews[p.id] && p.date>=today()).length,info:'Propostas, ainda não aplicadas'},
      {icon:'♡',label:'Seguidores de partida',value:'96',info:'Threads em 6 de novembro'},
      {icon:'↗',label:'Melhor publicação',value:'938',info:'Visualizações · 2 novembro'}
    ]);
    const list=tasksFor(today()); $('#home-tasks').innerHTML=list.slice(0,5).map(t=>taskHtml(t,today())).join('');
    const p=nextScheduled();
    $('#next-post').innerHTML=p?('<div class="next-label">'+esc(format(p.date,{weekday:'long',day:'numeric',month:'long'}))+' · '+esc(p.time)+'</div><div class="next-title">'+esc(p.title)+'</div><p class="next-quote">'+esc(p.text.split('\n\n').slice(0,2).join('\n\n'))+'</p><div class="next-actions"><button class="primary-btn" data-action="open-post" data-id="'+esc(p.id)+'">Ver publicação ↗</button><a class="outline-btn" href="'+esc(DATA.metricoolUrl)+'" target="_blank" rel="noopener noreferrer">Abrir Metricool ↗</a></div>'):
      '<p class="panel-text">Não há mais posts confirmados no instantâneo. Está na hora de preparar os próximos.</p><button data-goto="publicacoes" class="outline-btn">Ver rascunhos</button>';
    const milestone=DATA.milestones.find(m=>m.date>=today()) || DATA.milestones[DATA.milestones.length-1];
    $('#home-milestone').innerHTML='<div class="milestone-date">'+esc(shortDay(milestone.date))+'</div><div class="milestone-title">'+esc(milestone.title)+'</div><p class="milestone-desc">'+esc(milestone.task)+'</p>';
  }
  function eventsFor(date) {
    const out=[];
    allPosts().filter(p=>p.date===date).forEach(p=>out.push({kind:p.status==='local'?'local':'post',post:p,title:p.title,subtitle:(p.time||'')+' · '+(p.status==='local'?'Planeado localmente':'Agendado no Metricool')}));
    DATA.milestones.filter(m=>m.date===date).forEach(m=>out.push({kind:'plan',title:m.title,subtitle:m.task}));
    return out;
  }
  function renderCalendar() {
    const [y,m]=displayMonth.split('-').map(Number);
    const first=new Date(Date.UTC(y,m-1,1,12)), offset=(first.getUTCDay()+6)%7, count=new Date(Date.UTC(y,m,0,12)).getUTCDate();
    const length=Math.ceil((count+offset)/7)*7;
    $('#month-title').textContent=format(displayMonth+'-01',{month:'long',year:'numeric'});
    let html='';
    for(let n=0;n<length;n++){
      const d=addDays(displayMonth+'-01',n-offset),day=Number(d.slice(8));
      const events=eventsFor(d), outside=d.slice(0,7)!==displayMonth;
      const content=events.slice(0,2).map(e=>'<span class="cal-event '+e.kind+'" title="'+esc(e.title)+'">'+esc(e.title)+'</span>').join('');
      html+='<button class="cal-day '+(outside?'outside ':'')+(d===today()?'today ':'')+(d===selectedDate?'selected':'')+'" data-action="select-day" data-date="'+esc(d)+'" aria-label="'+esc(niceDay(d))+', '+events.length+' eventos"><span class="cal-number">'+day+'</span>'+content+'</button>';
    }
    $('#calendar-grid').innerHTML=html;
    $('#selected-date-title').textContent=niceDay(selectedDate);
    const ev=eventsFor(selectedDate);
    $('#selected-date-events').innerHTML=ev.length?ev.map(e=>'<div class="day-event"><span class="pill '+(e.kind==='plan'?'gold':e.kind==='local'?'green':'')+'">'+(e.kind==='plan'?'PLANO':e.kind==='local'?'LOCAL':'THREADS')+'</span><strong>'+esc(e.title)+'</strong><small>'+esc(e.subtitle)+'</small>'+(e.post?'<button class="text-action" data-action="open-post" data-id="'+esc(e.post.id)+'">Ver texto ↗</button>':'')+'</div>').join(''):'<p class="day-empty">Sem publicações ou marcos previstos. Também há dias para viver e escrever.</p>';
  }
  function renderPosts() {
    const query=($('#post-search').value||'').toLowerCase().trim(),filter=$('#post-filter').value;
    const out=allPosts().filter(p=>{
      const matching=!query||((p.title+' '+p.text+' '+(p.revision||'')).toLowerCase().includes(query));
      const type=filter==='all'||(filter==='review'&&p.revision)||(filter==='local'&&p.status==='local')||p.category===filter;
      return matching && type;
    });
    $('#post-list').innerHTML=out.length?out.map(p=>{
      const local=p.status==='local';
      const pill=local?'<span class="pill green">PLANO LOCAL</span>':p.date<today()?'<span class="pill gold">DATA PASSADA</span>':'<span class="pill">METRICOOL</span>';
      return '<article class="post-card"><div class="post-top"><span>'+esc(shortDay(p.date))+' · '+esc(p.time||'—')+'</span>'+pill+'</div><h3>'+esc(p.title)+'</h3><p class="post-excerpt">'+esc(p.text)+'</p><div class="post-bottom"><span class="review-tag">'+(p.revision?(state.reviews[p.id]?'✓ Revisão avaliada':'✎ Proposta de revisão'):esc(catNames[p.category]||'Editorial'))+'</span><button class="view-btn" data-action="open-post" data-id="'+esc(p.id)+'">Ver detalhes ↗</button></div></article>';
    }).join(''):'<div class="panel empty">Não existem publicações com este filtro.</div>';
  }
  function renderRoutine() {
    $('#routine-date').value=routineDate;
    $('#routine-day-title').textContent=niceDay(routineDate);
    const list=tasksFor(routineDate);
    $('#routine-tasks').innerHTML=list.map(t=>taskHtml(t,routineDate)).join('');
    $('#routine-progress').textContent=list.filter(t=>done(routineDate,t.id)).length+'/'+list.length+' concluídas';
    $('#milestones').innerHTML=DATA.milestones.map(m=>'<div class="timeline-item"><div class="milestone-date">'+esc(shortDay(m.date))+'</div><div><strong>'+esc(m.title)+'</strong><p>'+esc(m.task)+'</p></div></div>').join('');
  }
  function renderResults() {
    const results=Object.values(state.results);
    $('#result-stats').innerHTML=statsHtml([
      {icon:'◉',label:'Visualizações iniciais',value:'1.385',info:'6 publicações até 5 nov.'},
      {icon:'♧',label:'Interações iniciais',value:'70',info:'Likes, respostas, reposts e citações'},
      {icon:'↗',label:'Taxa de interação',value:'5,05%',info:'70 / 1.385 visualizações'},
      {icon:'✎',label:'Resultados adicionais',value:results.length,info:'Registados por ti neste navegador'}
    ]);
    const max=Math.max(...DATA.historic.map(p=>p.views));
    $('#historical-chart').innerHTML=DATA.historic.map(p=>'<div class="chart-row"><span title="'+esc(p.title)+'">'+esc(p.title)+'</span><div class="bar-bg"><div class="bar-fill" style="width:'+((p.views/max)*100).toFixed(1)+'%"></div></div><b>'+p.views+'</b></div>').join('');
    const select=$('#result-post'),sel=select.value;
    select.innerHTML=DATA.scheduled.map(p=>'<option value="'+esc(p.id)+'">'+esc(shortDay(p.date)+' · '+p.title)+'</option>').join('');
    if(DATA.scheduled.some(p=>p.id===sel))select.value=sel;
    fillResultFields();
    $('#manual-results').innerHTML=results.length?DATA.scheduled.filter(p=>state.results[p.id]).map(p=>{const r=state.results[p.id],rate=r.views?((r.interactions/r.views)*100).toFixed(1)+'%':'—';return '<div class="manual-result"><strong>'+esc(shortDay(p.date)+' · '+p.title)+'</strong><span>'+esc(r.views)+' vistas · '+esc(r.interactions)+' interações · '+rate+'</span></div>';}).join(''):'<p class="panel-text">Ainda não registaste resultados dos próximos posts. Começa depois de serem publicados.</p>';
  }
  function fillResultFields() {
    const r=state.results[$('#result-post').value] || {};
    $('#result-views').value=r.views==null?'':r.views;
    $('#result-interactions').value=r.interactions==null?'':r.interactions;
  }
  function modalOpen(html) {$('#modal-content').innerHTML=html;$('#modal').hidden=false;document.body.style.overflow='hidden';$('.modal-close').focus();}
  function closeModal() {$('#modal').hidden=true;document.body.style.overflow='';}
  function openPost(id) {
    const p=fromId(id);if(!p)return;
    const local=p.status==='local',review=!!state.reviews[p.id];
    modalOpen('<div class="eyebrow small">'+esc(shortDay(p.date)+' · '+p.time)+' · '+(local?'PLANO LOCAL':'METRICOOL')+'</div><h2 id="modal-title">'+esc(p.title)+'</h2><span class="modal-label">Texto '+(local?'do rascunho':'atualmente agendado')+'</span><div class="post-full">'+esc(p.text)+'</div>'+(p.revision?'<div class="divider"></div><span class="modal-label">Sugestão editorial · ainda não agendada</span><div class="post-full proposal">'+esc(p.revision)+'</div><label class="task"><input type="checkbox" data-action="reviewed" data-id="'+esc(p.id)+'" '+(review?'checked':'')+'><span class="task-title">Já decidi sobre esta revisão</span></label>':'')+'<div class="modal-actions"><button class="subtle-btn" data-action="copy-post" data-id="'+esc(p.id)+'" data-which="original">Copiar original</button>'+(p.revision?'<button class="subtle-btn" data-action="copy-post" data-id="'+esc(p.id)+'" data-which="revision">Copiar proposta</button>':'')+(local?'':'<a class="outline-btn" target="_blank" rel="noopener noreferrer" href="'+esc(DATA.metricoolUrl)+'">Abrir Metricool ↗</a>')+'</div><div class="divider"></div><label class="modal-label" for="note-input">Notas pessoais deste post</label><textarea id="note-input" class="note-field editor-form" rows="3" placeholder="Ideias, observações, decisões…">'+esc(state.notes[p.id]||'')+'</textarea><div class="modal-actions"><button class="primary-btn" data-action="save-note" data-id="'+esc(p.id)+'">Guardar nota</button>'+(local?'<button class="outline-btn" data-action="remove-post" data-id="'+esc(p.id)+'">Eliminar plano local</button>':'')+'</div>');
  }
  function openNewEvent(mode) {
    const t=mode==='post',defaultDate=activeView==='calendario'?selectedDate:today();
    modalOpen('<div class="eyebrow small">PLANEAMENTO PESSOAL</div><h2 id="modal-title">'+(t?'Novo rascunho':'Adicionar ao calendário')+'</h2><p class="panel-text">Este registo fica apenas no navegador e não é agendado no Metricool.</p><form class="editor-form" id="new-post-form"><label>Título<input name="title" maxlength="120" placeholder="Tema da publicação" required></label><div class="form-grid"><label>Data<input name="date" type="date" value="'+esc(defaultDate)+'" required></label><label>Hora<input name="time" type="time" value="20:30" required></label></div><label>Texto ou notas<textarea name="text" placeholder="Escreve aqui o texto ou deixa uma ideia para desenvolver…"></textarea></label><button type="submit" class="primary-btn">Guardar no meu plano</button></form>');
  }
  function safeFile(textData,name,type) {
    const blob=new Blob([textData],{type:type||'application/octet-stream'}),url=URL.createObjectURL(blob),a=document.createElement('a');a.href=url;a.download=name;document.body.appendChild(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),10000);
  }
  function backup() {safeFile(JSON.stringify({app:'amf_editorial',version:1,exported:new Date().toISOString(),data:state},null,2),'estudio-editorial-copia.json','application/json');toast('Cópia de segurança exportada.');}
  function calendarIcs() {
    const quote=s=>text(s).replace(/\\/g,'\\\\').replace(/\r?\n/g,'\\n').replace(/,/g,'\\,').replace(/;/g,'\\;');
    const stamp=new Date().toISOString().replace(/[-:]/g,'').replace(/\.\d+/,'');
    const items=allPosts().map(p=>{const dt=p.date.replace(/-/g,'')+'T'+(p.time||'20:30').replace(':','')+'00';return ['BEGIN:VEVENT','UID:'+p.id+'@amf-editorial','DTSTAMP:'+stamp,'DTSTART;TZID=Europe/Lisbon:'+dt,'SUMMARY:'+quote((p.status==='local'?'PLANO LOCAL: ':'THREADS: ')+p.title),'DESCRIPTION:'+quote(p.status==='local'?'Planeado localmente. Ainda não agendado no Metricool.':'Verificar publicação agendada no Metricool.'),'END:VEVENT'].join('\r\n');});
    DATA.milestones.forEach((m,i)=>items.push(['BEGIN:VEVENT','UID:plan'+i+'@amf-editorial','DTSTAMP:'+stamp,'DTSTART;VALUE=DATE:'+m.date.replace(/-/g,''),'SUMMARY:'+quote('Plano editorial: '+m.title),'DESCRIPTION:'+quote(m.task),'END:VEVENT'].join('\r\n')));
    safeFile('BEGIN:VCALENDAR\r\nVERSION:2.0\r\nPRODID:-//AMF//Estudio Editorial//PT\r\nCALSCALE:GREGORIAN\r\n'+items.join('\r\n')+'\r\nEND:VCALENDAR\r\n','calendario-editorial.ics','text/calendar');toast('Calendário .ics exportado.'); 
  }
  async function clipboard(value) {try{await navigator.clipboard.writeText(value);toast('Texto copiado.');}catch(e){toast('Não foi possível copiar automaticamente. Seleciona o texto.');}}
  document.addEventListener('click',e=>{
    const nav=e.target.closest('[data-view]');if(nav){navigate(nav.dataset.view);return;}
    const goto=e.target.closest('[data-goto]');if(goto){navigate(goto.dataset.goto);return;}
    const act=e.target.closest('[data-action]');if(!act)return;
    const a=act.dataset.action;
    if(a==='close-modal'){closeModal();return;}
    if(a==='new-post'||a==='new-event'){openNewEvent(a==='new-post'?'post':'event');return;}
    if(a==='open-post'){openPost(act.dataset.id);return;}
    if(a==='select-day'){selectedDate=act.dataset.date;displayMonth=selectedDate.slice(0,7);renderCalendar();return;}
    if(a==='prev-month'||a==='next-month'){const [y,m]=displayMonth.split('-').map(Number),d=new Date(Date.UTC(y,m-1+(a==='next-month'?1:-1),1,12));displayMonth=d.toISOString().slice(0,7);selectedDate=displayMonth+'-01';renderCalendar();return;}
    if(a==='go-today'){selectedDate=today();displayMonth=selectedDate.slice(0,7);renderCalendar();return;}
    if(a==='toggle-task'){const key=act.dataset.date+'|'+act.dataset.task;state.done[key]=!state.done[key];persist();refreshTasks();return;}
    if(a==='remove-task'){state.extra[act.dataset.date]=(state.extra[act.dataset.date]||[]).filter(t=>t.id!==act.dataset.task);delete state.done[act.dataset.date+'|'+act.dataset.task];persist();refreshTasks();return;}
    if(a==='copy-post'){const p=fromId(act.dataset.id);if(p)clipboard(act.dataset.which==='revision'?p.revision:p.text);return;}
    if(a==='save-note'){state.notes[act.dataset.id]=$('#note-input').value;persist();toast('Nota guardada neste navegador.');return;}
    if(a==='remove-post'){state.customPosts=(state.customPosts||[]).filter(p=>p.id!==act.dataset.id);persist();closeModal();renderPosts();renderCalendar();renderHome();toast('Plano local eliminado.');return;}
    if(a==='export-backup'){backup();return;}
    if(a==='import-backup'){$('#import-file').click();return;}
    if(a==='export-ical'){calendarIcs();return;}
  });
  document.addEventListener('change',e=>{
    if(e.target.matches('input[type=checkbox][data-task]')){const key=e.target.dataset.date+'|'+e.target.dataset.task;state.done[key]=e.target.checked;persist();refreshTasks();}
    if(e.target.matches('[data-action=reviewed]')){state.reviews[e.target.dataset.id]=e.target.checked;persist();renderPosts();renderHome();toast('Decisão editorial registada apenas neste site.');}
  });
  function refreshTasks(){renderHome();renderRoutine();}
  $('#post-search').addEventListener('input',renderPosts);
  $('#post-filter').addEventListener('change',renderPosts);
  $('#routine-date').addEventListener('change',e=>{routineDate=e.target.value||today();renderRoutine();});
  $('#result-post').addEventListener('change',fillResultFields);
  $('#extra-task-form').addEventListener('submit',e=>{e.preventDefault();const input=$('#extra-task'),title=input.value.trim();if(!title)return;(state.extra[routineDate]||(state.extra[routineDate]=[])).push({id:'extra'+Date.now(),title});input.value='';persist();refreshTasks();toast('Tarefa adicionada.');});
  $('#results-form').addEventListener('submit',e=>{e.preventDefault();const id=$('#result-post').value;let v=$('#result-views').value, i=$('#result-interactions').value;if(v===''||i===''){toast('Preenche os dois valores.');return;}state.results[id]={views:Math.max(0,parseInt(v,10)||0),interactions:Math.max(0,parseInt(i,10)||0)};persist();renderResults();toast('Resultado registado.');});
  $('#modal-content').addEventListener('submit',e=>{if(e.target.id!=='new-post-form')return;e.preventDefault();const form=new FormData(e.target),title=text(form.get('title')).trim(),date=text(form.get('date')),time=text(form.get('time')),body=text(form.get('text')).trim();if(!title||!date||!time)return;(state.customPosts||(state.customPosts=[])).push({id:'local'+Date.now(),date,time,title,text:body||'Ainda sem texto. Desenvolver ideia.',category:'local',status:'local'});persist();closeModal();renderPosts();renderCalendar();renderHome();toast('Plano local guardado. Ainda não está no Metricool.');});
  $('#modal').addEventListener('click',e=>{if(e.target.id==='modal')closeModal();});
  document.addEventListener('keydown',e=>{if(e.key==='Escape'&&!$('#modal').hidden)closeModal();});
  $('#import-file').addEventListener('change',async e=>{const file=e.target.files&&e.target.files[0];if(!file)return;try{const content=JSON.parse(await file.text());if(content.app!=='amf_editorial'||!content.data||typeof content.data!=='object')throw Error('Formato desconhecido');state=Object.assign(blank(),content.data);persist();renderAll();toast('Cópia importada com sucesso.');}catch(err){toast('Cópia inválida. Não foram alterados os teus dados.');}e.target.value='';});
  function renderAll(){renderHome();renderCalendar();renderPosts();renderRoutine();renderResults();}
  // A exportação iCalendar é útil para consultar datas noutras agendas sem alterar o Metricool.
  const calendarActions=$('.calendar-head');
  const button=document.createElement('button');button.className='outline-btn';button.dataset.action='export-ical';button.textContent='Exportar .ics ↓';
  calendarActions.appendChild(button);
  renderAll();
  const initial=location.hash.slice(1);if(['inicio','calendario','publicacoes','rotina','resultados'].includes(initial))navigate(initial);
})();
