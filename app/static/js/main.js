/* ──────────────────────────────────────────────────────────
   app/static/js/main.js
   ──────────────────────────────────────────────────────────
   Single, large JavaScript file for entire application
   ────────────────────────────────────────────────────────── */

let patients = [];
let currentDfn = null;
let overviewData = null;
let tabData = {};
let sortState = {};
let timelineCache = null;
let timelineFilter = 'all';

const TL_ICONS = {problem:'🔴',rx:'💊',lab:'🔬',appointment:'📅',note:'📝',order:'📋',surgery:'🔪',adt:'🏥',immunization:'💉',radiology:'📷'};

function toggleSidebar(){
  const sb=document.querySelector('.sidebar');
  const bd=document.querySelector('.sidebar-backdrop');
  const isOpen=sb.classList.toggle('open');
  bd.classList.toggle('show',isOpen);
}
function closeSidebar(){
  document.querySelector('.sidebar').classList.remove('open');
  document.querySelector('.sidebar-backdrop').classList.remove('show');
}

let tipEl=null;
function showTip(ev,html){if(!tipEl){tipEl=document.createElement('div');tipEl.className='tooltip';document.body.appendChild(tipEl)}tipEl.innerHTML=html;tipEl.style.display='block';const r=ev.target.getBoundingClientRect();const y=r.top<60?r.bottom+8:r.top-8;tipEl.style.left=Math.min(r.left+r.width/2,window.innerWidth-160)+'px';tipEl.style.top=y+'px';tipEl.style.transform=r.top<60?'translate(-50%,0)':'translate(-50%,-100%)';}
function hideTip(){if(tipEl)tipEl.style.display='none'}

const IC={
overview:'<svg class="ic" viewBox="0 0 16 16"><rect x="1" y="1" width="6" height="6" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><rect x="9" y="1" width="6" height="6" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><rect x="1" y="9" width="6" height="6" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/><rect x="9" y="9" width="6" height="6" rx="1" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>',
problems:'<svg class="ic" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.5"/><line x1="8" y1="4" x2="8" y2="9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><circle cx="8" cy="11.5" r=".75" fill="currentColor"/></svg>',
meds:'<svg class="ic" viewBox="0 0 16 16"><rect x="4" y="1" width="8" height="14" rx="3" fill="none" stroke="currentColor" stroke-width="1.5"/><line x1="4" y1="8" x2="12" y2="8" stroke="currentColor" stroke-width="1.5"/></svg>',
labs:'<svg class="ic" viewBox="0 0 16 16"><path d="M6 1v5L2 14a1 1 0 001 1h10a1 1 0 001-1L10 6V1" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="5" y1="1" x2="11" y2="1" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
vitals:'<svg class="ic" viewBox="0 0 16 16"><path d="M1 8h3l2-5 2 10 2-5h5" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></svg>',
allergies:'<svg class="ic" viewBox="0 0 16 16"><path d="M8 1L2 5v4c0 4 3 6 6 6s6-2 6-6V5z" fill="none" stroke="currentColor" stroke-width="1.5"/><line x1="8" y1="5" x2="8" y2="9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><circle cx="8" cy="11" r=".75" fill="currentColor"/></svg>',
notes:'<svg class="ic" viewBox="0 0 16 16"><path d="M3 1h7l3 3v11H3z" fill="none" stroke="currentColor" stroke-width="1.5"/><polyline points="10,1 10,4 13,4" fill="none" stroke="currentColor" stroke-width="1.5"/><line x1="5" y1="7" x2="11" y2="7" stroke="currentColor" stroke-width="1.2"/><line x1="5" y1="9.5" x2="11" y2="9.5" stroke="currentColor" stroke-width="1.2"/></svg>',
orders:'<svg class="ic" viewBox="0 0 16 16"><rect x="2" y="1" width="12" height="14" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><line x1="5" y1="5" x2="11" y2="5" stroke="currentColor" stroke-width="1.2"/><line x1="5" y1="8" x2="11" y2="8" stroke="currentColor" stroke-width="1.2"/><line x1="5" y1="11" x2="9" y2="11" stroke="currentColor" stroke-width="1.2"/></svg>',
schedule:'<svg class="ic" viewBox="0 0 16 16"><rect x="1.5" y="2.5" width="13" height="12" rx="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><line x1="1.5" y1="6" x2="14.5" y2="6" stroke="currentColor" stroke-width="1.5"/><line x1="5" y1="1" x2="5" y2="4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="11" y1="1" x2="11" y2="4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
timeline:'<svg class="ic" viewBox="0 0 16 16"><circle cx="8" cy="8" r="6.5" fill="none" stroke="currentColor" stroke-width="1.5"/><polyline points="8,4 8,8 11,10" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
immunizations:'<svg class="ic" viewBox="0 0 16 16"><line x1="8" y1="2" x2="8" y2="12" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><line x1="5" y1="6" x2="11" y2="6" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M6 12h4l1 3H5z" fill="none" stroke="currentColor" stroke-width="1.5" stroke-linejoin="round"/></svg>',
surgeries:'<svg class="ic" viewBox="0 0 16 16"><circle cx="10" cy="3" r="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M2 14L9 5" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/><path d="M6 10l-4 4" stroke="currentColor" stroke-width="1.5" stroke-linecap="round"/></svg>',
radiology:'<svg class="ic" viewBox="0 0 16 16"><rect x="2" y="2" width="12" height="12" rx="2" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="8" r="3" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="8" cy="8" r="1" fill="currentColor"/></svg>',
procedures:'<svg class="ic" viewBox="0 0 16 16"><circle cx="5" cy="3" r="2" fill="none" stroke="currentColor" stroke-width="1.5"/><path d="M5 5v4a3 3 0 006 0" fill="none" stroke="currentColor" stroke-width="1.5"/><circle cx="14" cy="6" r="1.5" fill="none" stroke="currentColor" stroke-width="1.5"/><line x1="11" y1="9" x2="14" y2="6" stroke="currentColor" stroke-width="1.5"/></svg>',
};

const DOMAIN={
problems:{color:'#dc2626',bg:'#fef2f2',label:'Problems'},
allergies:{color:'#ea580c',bg:'#fff7ed',label:'Allergies'},
meds:{color:'#7c3aed',bg:'#f5f3ff',label:'Medications'},
labs:{color:'#0d9488',bg:'#f0fdfa',label:'Lab Results'},
vitals:{color:'#16a34a',bg:'#f0fdf4',label:'Vitals'},
notes:{color:'#2563eb',bg:'#eff6ff',label:'Notes'},
orders:{color:'#4f46e5',bg:'#eef2ff',label:'Orders'},
schedule:{color:'#0891b2',bg:'#ecfeff',label:'Appointments'},
timeline:{color:'#1a73a7',bg:'#e3f2fd',label:'Timeline'},
immunizations:{color:'#059669',bg:'#ecfdf5',label:'Immunizations'},
surgeries:{color:'#b91c1c',bg:'#fef2f2',label:'Surgeries'},
radiology:{color:'#7e22ce',bg:'#faf5ff',label:'Radiology'},
procedures:{color:'#ca8a04',bg:'#fefce8',label:'Procedures'},
consults:{color:'#6366f1',bg:'#eef2ff',label:'Consults'},
};

const LAB_FLAGS={'L':'Low — below reference range','H':'High — above reference range','L*':'Critical Low — immediate attention','H*':'Critical High — immediate attention','LL':'Panic Low — life-threatening','HH':'Panic High — life-threatening'};
function escapeHtml(s){if(!s)return '';const d=document.createElement('div');d.textContent=s;return d.innerHTML;}
const SURG_SCHEDULE={'EM':'Emergency','U':'Unscheduled','EL':'Elective'};
const SURG_ADMISSION={'I':'Inpatient','O':'Outpatient'};
const SURG_TYPE={'M':'Major','N':'Minor','J':'Joint'};
const VITAL_RANGES={
'BLOOD PRESSURE':{parse:v=>{const p=v.split('/');return{sys:+p[0],dia:+p[1]}},check:v=>v.sys>=140||v.dia>=90?'critical':v.sys>=120||v.dia>=80?'warning':'normal'},
'PULSE':{parse:v=>+v,check:v=>v>120||v<50?'critical':v>100||v<60?'warning':'normal'},
'TEMPERATURE':{parse:v=>+v,check:v=>v>100.4?'critical':v>99||v<97?'warning':'normal'},
'RESPIRATION':{parse:v=>+v,check:v=>v>24||v<10?'critical':v>20||v<12?'warning':'normal'},
'PAIN':{parse:v=>+v,check:v=>v>=7?'critical':v>=4?'warning':'normal'},
};

function labRowClass(f){if(!f)return'';const u=f.toUpperCase();if(u==='HH'||u==='LL'||u.includes('*'))return'lab-row-critical';if(u==='H'||u==='L')return'lab-row-abnormal';return'';}
function vitalSeverity(name,reading){const cfg=VITAL_RANGES[(name||'').toUpperCase()];if(!cfg)return'normal';try{return cfg.check(cfg.parse(reading))}catch(e){return'normal'}}
function getInitials(name){const p=(name||'').split(',');return((p[1]||' ')[1]||'').toUpperCase()+((p[0]||' ')[0]||'').toUpperCase();}
function avatarColor(name){const c=['#dc2626','#ea580c','#16a34a','#0d9488','#2563eb','#7c3aed','#b91c1c','#0891b2'];let h=0;for(let i=0;i<(name||'').length;i++)h=((h<<5)-h)+(name||'').charCodeAt(i);return c[Math.abs(h)%c.length]}
function dailyMedUrl(d){return'https://dailymed.nlm.nih.gov/dailymed/search.cfm?query='+encodeURIComponent((d||'').split(' ').slice(0,2).join(' '))}
function counterHtml(key,count,tab){const d=DOMAIN[tab]||DOMAIN[key]||{color:'#1a73a7',bg:'#e3f2fd'};const icon=IC[tab]||IC[key]||'';const dim=count===0?' dimmed':'';return`<div class="demo-item clickable${dim}" onclick="switchTab('${tab}')" style="background:${d.bg};border-left:3px solid ${d.color}"><div style="color:${d.color}">${icon}</div><div class="val" style="color:${d.color}">${count}</div><div class="label">${d.label||key}</div></div>`;}
let medsFilter='';

function dateColor(ds){
  if(!ds)return'var(--muted)';
  const d=(ds+'').substring(0,10);
  if(d.length<10||d[4]!=='-')return'var(--muted)';
  const ms=Date.now()-new Date(d).getTime();
  if(isNaN(ms))return'var(--muted)';
  const y=ms/(365.25*864e5);
  if(y<2)return'#16a34a';
  if(y<5)return'#ca8a04';
  if(y<15)return'#ea580c';
  return'#94a3b8';
}
function dateHtml(ds){
  if(!ds)return'<span style="color:var(--muted)">—</span>';
  return`<span style="color:${dateColor(ds)}">${ds}</span>`;
}

async function api(url, opts) {
  try {
    const r = await fetch(url, opts);
    if (!r.ok) return {};
    return r.json();
  } catch(e) { return {}; }
}

function formatName(n) {
  if (!n) return '';
  const parts = n.split(',');
  const last = (parts[0] || '').trim();
  const first = (parts[1] || '').trim();
  const cap = s => s ? s.charAt(0).toUpperCase() + s.slice(1).toLowerCase() : '';
  return (first.split(' ').map(cap).join(' ') + ' ' + cap(last)).trim();
}

function labFlagClass(flag) {
  if (!flag) return 'normal';
  const f = flag.toUpperCase();
  if (f === 'HH' || f === 'LL' || f.includes('*')) return 'critical';
  if (f === 'H' || f === 'L') return 'warning';
  return 'normal';
}

function statusBadge(name) {
  const sn = (name || '').toLowerCase();
  if (sn.indexOf('active') >= 0) return 'badge-active';
  if (sn.indexOf('pending') >= 0) return 'badge-pending';
  if (sn.indexOf('complete') >= 0) return 'badge-complete';
  if (sn.indexOf('discontinued') >= 0 || sn.indexOf('cancelled') >= 0) return 'badge-dc';
  return 'badge-complete';
}

function apptBadge(status) {
  const s = (status || '').toUpperCase();
  if (s.includes('CHECKED OUT')) return 'appt-badge appt-badge-checked-out';
  if (s.includes('NO SHOW')) return 'appt-badge appt-badge-no-show';
  if (s.includes('CHECKED IN')) return 'appt-badge appt-badge-checked-in';
  if (s.includes('INPATIENT')) return 'appt-badge appt-badge-inpatient';
  return '';
}

function rxBadge(status) {
  const s = (status || '').toUpperCase();
  if (s === 'ACTIVE') return 'badge-active';
  if (s === 'EXPIRED') return 'badge-complete';
  if (s.includes('DISCONTINUED') || s === 'DELETED') return 'badge-dc';
  if (s === 'SUSPENDED' || s === 'HOLD') return 'badge-pending';
  return '';
}

function showToast(msg, color) {
  const t = document.createElement('div');
  t.style.cssText = `position:fixed;bottom:24px;right:24px;background:${color||'#1e293b'};color:#fff;padding:12px 20px;border-radius:8px;font-size:13px;z-index:200;box-shadow:0 4px 12px rgba(0,0,0,.2);max-width:400px;font-family:monospace`;
  t.textContent = msg;
  document.body.appendChild(t);
  setTimeout(() => t.remove(), 4000);
}
function readOnlyToast() { showToast('Read-only demo — real VistA VEHU data'); }

function sortBy(tab, column) {
  const st = sortState[tab] || {};
  const dir = (st.column === column && st.dir === 'asc') ? 'desc' : 'asc';
  sortState[tab] = { column, dir };
  const data = tabData[tab] || [];
  data.sort((a, b) => {
    const va = (a[column] || ''), vb = (b[column] || '');
    const cmp = va < vb ? -1 : va > vb ? 1 : 0;
    return dir === 'asc' ? cmp : -cmp;
  });
  const renderers = {problems: renderProblems, meds: renderMeds, labs: renderLabs, schedule: renderSchedule};
  if (renderers[tab]) renderers[tab]();
}

function thS(tab, col, label) {
  const st = sortState[tab] || {};
  const arrow = st.column === col ? (st.dir === 'asc' ? ' ▲' : ' ▼') : '';
  return `<th class="sortable" onclick="sortBy('${tab}','${col}')">${label}${arrow}</th>`;
}

// ── Init ──────────────────────────────────────────────────────

async function init() {
  const ov = await api('/api/overview');
  overviewData = ov;
  document.getElementById('stats-specs').textContent = (ov.packages||15) + ' packages';
  document.getElementById('stats-bugs').textContent = (ov.total_records||0).toLocaleString() + ' records';
  document.getElementById('no-patient-stats').textContent =
    'Real VistA VEHU data — ' + (ov.total_records||0).toLocaleString() + ' records from MUMPS globals via PostgreSQL';
  // const data = await api('/api/patients?per_page=500');
  const data = await api('/api/patients');
  patients = data.patients || [];
  renderPatientList();
}

function filterPatients(query) {
  const q = (query || '').toUpperCase();
  const list = q
    ? patients.filter(p =>
        (p.name || '').toUpperCase().includes(q) ||
        (p.city || '').toUpperCase().includes(q))
    : patients;
  renderPatientList(list);
}

function renderPatientList(list) {
  list = list || patients;
  const el = document.getElementById('patient-list');
  el.innerHTML = list.map(p => `
    <div class="patient-item ${currentDfn==p.dfn?'active':''}" onclick="selectPatient('${p.dfn}')">
      <div class="avatar" style="background:${avatarColor(p.name)}">${getInitials(p.name)}</div>
      <div>
        <div class="name">${formatName(p.name)}</div>
        <div class="info">${p.sex||''} · ${p.dob||''} · ${p.city||''}, ${p.state||''}</div>
        <div class="badges">
          ${p.veteran?'<span class="b sc-badge">Veteran</span>':''}
          ${p.service_connected?`<span class="b" style="background:#dbeafe;color:#1e40af">SC ${p.sc_percentage||0}%</span>`:''}
        </div>
      </div>
    </div>
  `).join('');
}

async function selectPatient(dfn) {
  currentDfn = String(dfn);
  tabData = {};
  sortState = {};
  timelineCache = null;
  timelineFilter = 'all';
  medsFilter = '';
  closeSidebar();
  const q = document.getElementById('patient-search').value;
  filterPatients(q);
  document.querySelectorAll('.section').forEach(s => s.innerHTML = '');
  document.getElementById('no-patient').style.display = 'none';
  document.getElementById('patient-view').style.display = 'block';
  switchTab('overview');
}

document.querySelectorAll('.tab').forEach(t => {
  t.addEventListener('click', () => switchTab(t.dataset.tab));
  const d = DOMAIN[t.dataset.tab];
  if (d && IC[t.dataset.tab]) t.innerHTML = `<span style="color:${d.color}">${IC[t.dataset.tab]}</span> ${t.textContent}`;
});

function switchTab(tab) {
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.tab===tab));
  document.querySelectorAll('.section').forEach(s => s.classList.remove('active'));
  const dc=DOMAIN[tab]; document.querySelector('.tabs').style.setProperty('--tab-active',dc?dc.color:'#1a73a7');
  const sec = document.getElementById('sec-'+tab);
  if (sec) sec.classList.add('active');
  const loaders = {overview:loadOverview, problems:loadProblems, meds:loadMeds, labs:loadLabs, vitals:loadVitals, allergies:loadAllergies, notes:loadNotes, orders:loadOrders, schedule:loadSchedule, timeline:loadTimeline, immunizations:loadImmunizations, surgeries:loadSurgeries, radiology:loadRadiology, procedures:loadProcedures};
  if (loaders[tab]) loaders[tab]();
  loadMumpsGlobals(tab);
}

// ── Overview ──────────────────────────────────────────────────

async function loadOverview() {
  const dfn = currentDfn;
  try {
  const [pd, vitalsData, probData] = await Promise.all([
    api(`/api/patient/${dfn}`),
    api(`/api/patient/${dfn}/vitals?per_page=200`),
    api(`/api/patient/${dfn}/problems`)
  ]);
  if (currentDfn !== dfn) return;

  const vitals = vitalsData.vitals || [];
  const activeProblems = (probData.problems || []).filter(p => p.status === 'A');
  const latest = {};
  vitals.forEach(v => {
    const key = v.vital_name || 'Unknown';
    if (!latest[key] || (v.datetime_taken || '') > (latest[key].datetime_taken || ''))
      latest[key] = v;
  });

  const totalCounts = (pd.problems_count||0)+(pd.allergies_count||0)+(pd.rx_count||0)+(pd.labs_count||0)+(pd.vitals_count||0)+(pd.orders_count||0)+(pd.notes_count||0)+(pd.appointments_count||0);

  const el = document.getElementById('sec-overview');
  el.innerHTML = `
    <div class="card">
      <h3>${formatName(pd.name)} ${(pd.allergies_count||0) > 0 ? '<span class="allergy-flag">⚠ ALLERGIES</span>' : ''}</h3>
      <div class="info-grid">
        <div>
          <div class="info-row"><span class="label">DOB</span><span>${pd.dob ? dateHtml(pd.dob) : '—'}</span></div>
          <div class="info-row"><span class="label">Sex</span><span>${pd.sex === 'M' ? 'Male' : pd.sex === 'F' ? 'Female' : pd.sex || '—'}</span></div>
          <div class="info-row"><span class="label">SSN</span><span>${pd.ssn || '—'}</span></div>
          <div class="info-row"><span class="label">Occupation</span><span>${pd.occupation || '—'}</span></div>
        </div>
        <div>
          <div class="info-row"><span class="label">Address</span><span>${pd.street_1 || '—'}</span></div>
          <div class="info-row"><span class="label">City/State</span><span>${pd.city || ''}, ${pd.state || ''} ${pd.zip || ''}</span></div>
          <div class="info-row"><span class="label">Home Phone</span><span>${pd.phone_home || '—'}</span></div>
          ${pd.phone_work ? `<div class="info-row"><span class="label">Work Phone</span><span>${pd.phone_work}</span></div>` : ''}
          ${pd.phone_cell ? `<div class="info-row"><span class="label">Cell Phone</span><span>${pd.phone_cell}</span></div>` : ''}
          ${pd.email ? `<div class="info-row"><span class="label">Email</span><span>${pd.email}</span></div>` : ''}
        </div>
      </div>
    </div>
    <div class="card">
      <h3>Service Information</h3>
      <div class="info-grid">
        <div>
          <div class="info-row"><span class="label">Veteran</span><span>${pd.veteran ? 'Yes' : 'No'}</span></div>
          <div class="info-row"><span class="label">Service Connected</span><span>${pd.service_connected ? 'Yes' : 'No'}</span></div>
          <div class="info-row"><span class="label">SC %</span><span>${pd.sc_percentage || 0}%</span></div>
        </div>
        <div></div>
      </div>
    </div>
    ${totalCounts === 0 && !pd.name ? '<div class="card" style="text-align:center;padding:32px;color:var(--muted)"><div style="font-size:32px;margin-bottom:8px">📋</div>No clinical data loaded for this patient.<br><span style="font-size:12px">API may be unavailable or patient record is empty.</span></div>' : `
    <div class="demo-grid">
      ${counterHtml('problems',pd.problems_count||0,'problems')}
      ${counterHtml('allergies',pd.allergies_count||0,'allergies')}
      ${counterHtml('meds',pd.rx_count||0,'meds')}
      ${counterHtml('labs',pd.labs_count||0,'labs')}
      ${counterHtml('vitals',pd.vitals_count||0,'vitals')}
      ${counterHtml('orders',pd.orders_count||0,'orders')}
      ${counterHtml('notes',pd.notes_count||0,'notes')}
      ${counterHtml('schedule',pd.appointments_count||0,'schedule')}
      ${counterHtml('consults',pd.consults_count||0,'orders')}
      ${counterHtml('immunizations',pd.immunizations_count||0,'immunizations')}
      ${counterHtml('surgeries',pd.surgeries_count||0,'surgeries')}
    </div>`}
    ${activeProblems.length > 0 ? `
    <div class="card">
      <h3>Active Problems</h3>
      <div class="problem-chips">
        ${activeProblems.map(p => `<span class="chip" onclick="switchTab('problems')">${p.narrative || p.diagnosis || '—'}</span>`).join('')}
      </div>
    </div>` : ''}
    ${Object.keys(latest).length > 0 ? `
    <div class="card">
      <h3>Latest Vitals</h3>
      <div class="vital-cards">
        ${Object.values(latest).map(v => {
          const sev = vitalSeverity(v.vital_name, v.reading);
          return `<div class="vital-card vital-${sev}">
            <div class="type">${v.vital_name || '—'}</div>
            <div class="reading">${v.reading || '—'}</div>
            <div class="time">${dateHtml(v.datetime_taken)}</div>
          </div>`;
        }).join('')}
      </div>
    </div>` : ''}
  `;
  } catch(err) { console.error('loadOverview error:', err); document.getElementById('sec-overview').innerHTML='<div class="card empty">Error loading overview. Try selecting patient again.</div>'; }
}

// ── Problems ──────────────────────────────────────────────────

async function loadProblems() {
  const dfn = currentDfn;
  try {
  const data = await api(`/api/patient/${dfn}/problems`);
  if (currentDfn !== dfn) return;
  tabData.problems = (data.problems || []).sort((a,b) => (a.status==='A'?0:1)-(b.status==='A'?0:1));
  renderProblems();
  } catch(err) { console.error('loadProblems error:', err); }
}

function renderProblems() {
  const probs = tabData.problems || [];
  const el = document.getElementById('sec-problems');
  el.innerHTML = `
    <div class="toolbar">
      <button class="btn btn-primary" onclick="showAddProblemForm()">+ Add Problem</button>
    </div>
    <div class="card">
      <h3><span style="color:${DOMAIN.problems.color}">${IC.problems}</span> Problems (${probs.length})</h3>
      <table>
        <thead><tr>
          ${thS('problems','status','Status')}
          ${thS('problems','narrative','Problem')}
          ${thS('problems','diagnosis','Diagnosis')}
          ${thS('problems','date_onset','Onset')}
          ${thS('problems','date_resolved','Resolved')}
          ${thS('problems','provider','Provider')}
          <th>Action</th>
        </tr></thead>
        <tbody>
          ${probs.map(p => `<tr class="${p.status==='A'?'prob-active':'prob-inactive'}">
            <td><span class="status-${p.status}">${p.status === 'A' ? 'Active' : p.status === 'I' ? 'Inactive' : p.status || '—'}</span></td>
            <td><strong>${p.narrative || '—'}</strong></td>
            <td>${p.diagnosis || '—'}</td>
            <td>${dateHtml(p.date_onset)}</td>
            <td>${dateHtml(p.date_resolved)}</td>
            <td>${p.provider || '—'}</td>
            <td>${p.status==='A' ? `<button class="btn btn-sm btn-danger" onclick="inactivateProblem('${p.id}')">Inactivate</button>` : ''}</td>
          </tr>`).join('')}
        </tbody>
      </table>
      ${probs.length === 0 ? '<div class="empty">No problems recorded</div>' : ''}
    </div>
  `;
}

// ── Meds ──────────────────────────────────────────────────────

async function loadMeds() {
  const dfn = currentDfn;
  try {
  const data = await api(`/api/patient/${dfn}/prescriptions`);
  if (currentDfn !== dfn) return;
  tabData.meds = data.prescriptions || [];
  renderMeds();
  } catch(err) { console.error('loadMeds error:', err); }
}

function filterMedsInput(val){medsFilter=val;renderMeds();}
function renderMedsTable(rows, tab) {
  return rows.map(r => `<tr>
    <td><a href="${dailyMedUrl(r.drug_name)}" target="_blank" rel="noopener" class="drug-link">${r.drug_name || '—'}</a></td>
    <td>${r.qty || '—'}</td><td>${r.days_supply || '—'}</td><td>${r.refills_remaining || '—'}</td>
    <td>${dateHtml(r.issue_date)}</td>
    <td><span class="badge-pill ${rxBadge(r.status)}">${r.status || '—'}</span></td>
    <td>${r.provider || '—'}</td>
  </tr>`).join('');
}
function renderMeds() {
  let rxs = tabData.meds || [];
  const q = (medsFilter||'').toUpperCase();
  if (q) rxs = rxs.filter(r => (r.drug_name||'').toUpperCase().includes(q));
  const active = rxs.filter(r => (r.status||'').toUpperCase()==='ACTIVE');
  const other = rxs.filter(r => (r.status||'').toUpperCase()!=='ACTIVE');
  const thead = `<thead><tr>${thS('meds','drug_name','Drug')}<th>Qty</th><th>Days</th><th>Refills</th>${thS('meds','issue_date','Fill Date')}${thS('meds','status','Status')}${thS('meds','provider','Provider')}</tr></thead>`;
  const el = document.getElementById('sec-meds');
  el.innerHTML = `
    <div class="toolbar">
      <button class="btn btn-primary" onclick="readOnlyToast()">+ New Rx</button>
      <input type="text" class="tab-filter" placeholder="Filter medications..." value="${medsFilter}" oninput="filterMedsInput(this.value)">
    </div>
    <div class="card">
      <h3><span style="color:${DOMAIN.meds.color}">${IC.meds}</span> Prescriptions (${(tabData.meds||[]).length}${q?' — filtered: '+rxs.length:''})</h3>
      ${active.length > 0 ? `
        <div class="meds-section-header meds-active-header">Active (${active.length})</div>
        <table>${thead}<tbody>${renderMedsTable(active)}</tbody></table>` : ''}
      ${other.length > 0 ? `
        <div class="meds-section-header meds-other-header">${active.length>0?'Other':'All'} (${other.length})</div>
        <table>${thead}<tbody>${renderMedsTable(other)}</tbody></table>` : ''}
      ${rxs.length === 0 ? '<div class="empty">No prescriptions</div>' : ''}
    </div>
  `;
}

// ── Labs ──────────────────────────────────────────────────────

async function loadLabs() {
  const dfn = currentDfn;
  try {
  const data = await api(`/api/patient/${dfn}/labs`);
  if (currentDfn !== dfn) return;
  tabData.labs = data.labs || [];
  renderLabs();
  } catch(err) { console.error('loadLabs error:', err); }
}

function renderLabs() {
  const labs = tabData.labs || [];
  const el = document.getElementById('sec-labs');
  el.innerHTML = `
    <div class="card">
      <h3><span style="color:${DOMAIN.labs.color}">${IC.labs}</span> Lab Results (${labs.length})</h3>
      ${labs.length === 0 ? '<div class="empty">No lab results available</div>' : `
      <table>
        <thead><tr>
          ${thS('labs','collection_datetime','Date')}
          ${thS('labs','test_name','Test')}
          ${thS('labs','result_value','Result')}
          <th>Units</th><th>Ref Range</th>
          ${thS('labs','abnormal_flag','Flag')}
        </tr></thead>
        <tbody>
          ${labs.map(l => {
            const cls = labFlagClass(l.abnormal_flag);
            const rowCls = labRowClass(l.abnormal_flag);
            const flagKey = (l.abnormal_flag||'').toUpperCase();
            const flagTip = LAB_FLAGS[flagKey]||'';
            const valColor = cls==='critical'?'color:#dc2626':cls==='warning'?'color:#b45309':'';
            return `<tr class="${rowCls}">
              <td>${dateHtml(l.collection_datetime)}</td>
              <td>${l.test_name || '—'}</td>
              <td><strong style="${valColor}">${l.result_value || '—'}</strong></td>
              <td style="color:var(--muted)">${l.units || ''}</td>
              <td style="color:var(--muted)">${l.reference_range || ''}</td>
              <td><span class="${cls==='critical'?'sev-Severe':cls==='warning'?'sev-Moderate':''}" ${flagTip?`onmouseenter="showTip(event,'${flagTip}')" onmouseleave="hideTip()"`:''} style="cursor:${flagTip?'help':'default'}">${l.abnormal_flag || ''}</span></td>
            </tr>`;
          }).join('')}
        </tbody>
      </table>`}
    </div>
  `;
}

// ── Vitals ────────────────────────────────────────────────────

async function loadVitals(overrideVitals) {
  const dfn = currentDfn;
  try {
  let vitals, paginationTotal;
  if (overrideVitals) {
    vitals = overrideVitals;
    paginationTotal = vitals.length;
  } else {
    const data = await api(`/api/patient/${dfn}/vitals?per_page=200`);
    if (currentDfn !== dfn) return;
    vitals = data.vitals || [];
    paginationTotal = data.pagination && data.pagination.total > vitals.length ? data.pagination.total : null;
  }
  const latest = {};
  vitals.forEach(v => {
    const key = v.vital_name || 'Unknown';
    if (!latest[key] || (v.datetime_taken || '') > (latest[key].datetime_taken || ''))
      latest[key] = v;
  });
  const el = document.getElementById('sec-vitals');
  el.innerHTML = `
    <div class="toolbar">
      <button class="btn btn-primary" onclick="showAddVitalForm()">+ Enter Vitals</button>
    </div>
    <div class="vital-cards">
      ${Object.values(latest).map(v => {
        const sev = vitalSeverity(v.vital_name, v.reading);
        return `<div class="vital-card vital-${sev}">
          <div class="type">${v.vital_name || '—'}</div>
          <div class="reading">${v.reading || '—'}</div>
          <div class="time">${dateHtml(v.datetime_taken)}</div>
        </div>`;
      }).join('')}
    </div>
    ${Object.keys(latest).length === 0 ? '<div class="card empty">No vitals recorded</div>' : ''}
    <div class="card">
      <h3><span style="color:${DOMAIN.vitals.color}">${IC.vitals}</span> Vital Signs History (${vitals.length}${paginationTotal ? ' of ' + paginationTotal : ''})</h3>
      <table>
        <thead><tr><th>Date/Time</th><th>Type</th><th>Reading</th><th>Location</th><th>Entered By</th></tr></thead>
        <tbody>
          ${vitals.map(v => `<tr>
            <td>${dateHtml(v.datetime_taken)}</td>
            <td>${v.vital_name || '—'}</td>
            <td><strong>${v.reading || '—'}</strong></td>
            <td>${v.location || '—'}</td>
            <td>${v.entered_by || '—'}</td>
          </tr>`).join('')}
        </tbody>
      </table>
      ${vitals.length === 0 ? '<div class="empty">No vitals recorded</div>' : ''}
    </div>
  `;
  } catch(err) { console.error('loadVitals error:', err); }
}

// ── Allergies ─────────────────────────────────────────────────

async function loadAllergies(overrideAllergies) {
  const dfn = currentDfn;
  try {
  let allergies;
  if (overrideAllergies) {
    allergies = overrideAllergies;
  } else {
    const data = await api(`/api/patient/${dfn}/allergies`);
    if (currentDfn !== dfn) return;
    allergies = data.allergies || [];
  }
  const el = document.getElementById('sec-allergies');
  el.innerHTML = `
    <div class="toolbar">
      <button class="btn btn-primary" onclick="showAddAllergyForm()">+ Add Allergy</button>
    </div>
    <h3 class="card" style="padding:12px 20px;margin-bottom:12px"><span style="color:${DOMAIN.allergies.color}">${IC.allergies}</span> Allergies (${allergies.length})</h3>
    ${allergies.map(a => `
      <div class="card">
        <div style="display:flex;justify-content:space-between;align-items:center">
          <div>
            <h3 style="margin-bottom:4px">${a.reactant || '—'}</h3>
            <div style="font-size:12px;color:var(--muted)">
              ${a.allergy_type === 'D' ? 'Drug' : a.allergy_type === 'F' ? 'Food' : a.allergy_type || 'Other'}
              ${a.mechanism ? ' · ' + (a.mechanism === 'A' ? 'Allergy' : 'Pharmacological') : ''}
            </div>
          </div>
        </div>
        <div style="margin-top:8px;font-size:11px">
          Entered: ${dateHtml(a.entry_date)} · ${a.verified ? '<span style="color:#16a34a;font-weight:600">Verified</span>' : '<span style="color:#ea580c;font-weight:600">Unverified</span>'}
        </div>
      </div>
    `).join('')}
    ${allergies.length === 0 ? '<div class="card empty">No Known Allergies (NKA)</div>' : ''}
  `;
  } catch(err) { console.error('loadAllergies error:', err); }
}

// ── Notes ─────────────────────────────────────────────────────

async function loadNotes() {
  const dfn = currentDfn;
  try {
  const [notesData, mhData] = await Promise.all([
    api(`/api/patient/${dfn}/notes`),
    api(`/api/patient/${dfn}/mh`)
  ]);
  if (currentDfn !== dfn) return;
  const notes = notesData.notes || [];
  const mh = mhData.results || [];
  const el = document.getElementById('sec-notes');
  el.innerHTML = `
    <h3 class="card" style="padding:12px 20px;margin-bottom:12px"><span style="color:${DOMAIN.notes.color}">${IC.notes}</span> Clinical Notes (${notes.length})</h3>
    ${notes.map(n => `
      <div class="note-card">
        <div class="note-header" onclick="this.parentElement.classList.toggle('expanded')">
          <div style="display:flex;align-items:center">
            <span class="expand-icon">▶</span>
            <div>
              <strong>${n.title || 'Untitled'}</strong>
              <span style="font-size:11px;color:var(--muted);margin-left:8px">${dateHtml(n.document_date)} · ${n.author || '—'}${n.attending ? ' · Att: ' + n.attending : ''}</span>
            </div>
          </div>
          <span class="badge-pill ${n.status_name === 'COMPLETED' ? 'badge-active' : 'badge-pending'}">${n.status_name || '—'}</span>
        </div>
        <div class="note-body">
          <div class="note-text">${n.body ? escapeHtml(n.body) : '<em style="color:var(--muted)">No content</em>'}</div>
        </div>
      </div>
    `).join('')}
    ${notes.length === 0 ? '<div class="card empty">No clinical notes</div>' : ''}
    ${mh.length > 0 ? `
    <div class="subsection">
      <h4>MH Screening Results</h4>
      ${mh.map(m => `
        <div class="card">
          <div style="display:flex;justify-content:space-between;align-items:center">
            <strong>${m.instrument || '—'}</strong>
            <span>${dateHtml(m.date_given)}</span>
          </div>
          <div style="margin-top:8px">Score: <strong>${m.total_score}</strong> — ${m.interpretation || '—'}</div>
        </div>
      `).join('')}
    </div>` : ''}
  `;
  } catch(err) { console.error('loadNotes error:', err); }
}

// ── Orders ────────────────────────────────────────────────────

async function loadOrders() {
  const dfn = currentDfn;
  try {
  const [ordersData, consultsData] = await Promise.all([
    api(`/api/patient/${dfn}/orders`),
    api(`/api/patient/${dfn}/consults`)
  ]);
  if (currentDfn !== dfn) return;
  const orders = ordersData.orders || [];
  const consults = consultsData.consults || [];
  const el = document.getElementById('sec-orders');
  el.innerHTML = `
    <div class="card">
      <h3><span style="color:${DOMAIN.orders.color}">${IC.orders}</span> Orders (${orders.length}${ordersData.pagination && ordersData.pagination.total > orders.length ? ' of ' + ordersData.pagination.total : ''})</h3>
      <table>
        <thead><tr><th>ID</th><th>Status</th><th>Entered</th><th>Start</th><th>Location</th><th>Provider</th></tr></thead>
        <tbody>
          ${orders.map(o => `
            <tr>
              <td style="color:var(--muted);font-size:11px">${o.id || '—'}</td>
              <td><span class="badge-pill ${statusBadge(o.status_name)}">${o.status_name || '—'}</span></td>
              <td>${dateHtml(o.when_entered)}</td>
              <td>${dateHtml(o.start_datetime)}</td>
              <td>${o.location || '—'}</td>
              <td>${o.provider || '—'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      ${orders.length === 0 ? '<div class="empty">No orders</div>' : ''}
    </div>
    <div class="card subsection">
      <h3><span style="color:${DOMAIN.consults.color}">${IC.orders}</span> Consults (${consults.length})</h3>
      <table>
        <thead><tr><th>Service</th><th>Status</th><th>Requested</th><th>Urgency</th><th>Disposition</th><th>From</th><th>Requesting</th></tr></thead>
        <tbody>
          ${consults.map(c => `
            <tr>
              <td><strong>${c.service || '—'}</strong></td>
              <td><span class="badge-pill ${statusBadge(c.status_name)}">${c.status_name || '—'}</span></td>
              <td>${dateHtml(c.date_of_request)}</td>
              <td>${c.urgency || '—'}</td>
              <td>${c.disposition || '—'}</td>
              <td>${c.from_location || '—'}</td>
              <td>${c.sending_provider || '—'}</td>
            </tr>
          `).join('')}
        </tbody>
      </table>
      ${consults.length === 0 ? '<div class="empty">No consults</div>' : ''}
    </div>
  `;
  } catch(err) { console.error('loadOrders error:', err); }
}

// ── Schedule ──────────────────────────────────────────────────

async function loadSchedule() {
  const dfn = currentDfn;
  try {
  const data = await api(`/api/patient/${dfn}/appointments`);
  if (currentDfn !== dfn) return;
  tabData.schedule = data.appointments || [];
  renderSchedule();
  } catch(err) { console.error('loadSchedule error:', err); }
}

function renderSchedule() {
  const appointments = tabData.schedule || [];
  const el = document.getElementById('sec-schedule');
  el.innerHTML = `
    <div class="toolbar">
      <button class="btn btn-primary" onclick="readOnlyToast()">+ Schedule Appointment</button>
    </div>
    <div class="card">
      <h3><span style="color:${DOMAIN.schedule.color}">${IC.schedule}</span> Appointments (${appointments.length})</h3>
      <table>
        <thead><tr>
          ${thS('schedule','appointment_datetime','Date/Time')}
          ${thS('schedule','clinic_name','Clinic')}
          ${thS('schedule','status','Status')}
        </tr></thead>
        <tbody>
          ${appointments.map(a => `<tr>
            <td>${dateHtml(a.appointment_datetime)}</td>
            <td>${a.clinic_name || '—'}</td>
            <td><span class="${apptBadge(a.status)}">${a.status || '—'}</span></td>
          </tr>`).join('')}
        </tbody>
      </table>
      ${appointments.length === 0 ? '<div class="empty">No appointments scheduled</div>' : ''}
    </div>
  `;
}

// ── Timeline ──────────────────────────────────────────────────

async function loadTimeline() {
  const dfn = currentDfn;
  try {
  const data = await api(`/api/patient/${dfn}/timeline`);
  if (currentDfn !== dfn) return;
  timelineCache = data.events || [];
  timelineFilter = 'all';
  renderTimeline();
  } catch(err) { console.error('loadTimeline error:', err); }
}

function filterTimeline(type) {
  timelineFilter = type;
  document.querySelectorAll('.tl-filter').forEach(b => b.classList.toggle('active', b.dataset.type === type));
  renderTimeline();
}

function renderTimeline() {
  const events = timelineFilter === 'all' ? timelineCache : timelineCache.filter(e => e.type === timelineFilter);
  const groups = {};
  events.forEach(e => {
    const key = e.sort_date || 'Unknown';
    if (!groups[key]) groups[key] = [];
    groups[key].push(e);
  });
  const sortedDates = Object.keys(groups).filter(d => d !== 'Unknown').sort().reverse();
  if (groups['Unknown']) sortedDates.push('Unknown');

  const el = document.getElementById('sec-timeline');
  el.innerHTML = `
    <div class="card">
      <h3><span style="color:${DOMAIN.timeline.color}">${IC.timeline}</span> Patient Timeline (${timelineCache.length} events)</h3>
      <div class="timeline-filters">
        <button class="tl-filter ${timelineFilter==='all'?'active':''}" data-type="all" onclick="filterTimeline('all')">All</button>
        <button class="tl-filter ${timelineFilter==='problem'?'active':''}" data-type="problem" onclick="filterTimeline('problem')">🔴 Problems</button>
        <button class="tl-filter ${timelineFilter==='rx'?'active':''}" data-type="rx" onclick="filterTimeline('rx')">💊 Meds</button>
        <button class="tl-filter ${timelineFilter==='lab'?'active':''}" data-type="lab" onclick="filterTimeline('lab')">🔬 Labs</button>
        <button class="tl-filter ${timelineFilter==='appointment'?'active':''}" data-type="appointment" onclick="filterTimeline('appointment')">📅 Appts</button>
        <button class="tl-filter ${timelineFilter==='note'?'active':''}" data-type="note" onclick="filterTimeline('note')">📝 Notes</button>
        <button class="tl-filter ${timelineFilter==='order'?'active':''}" data-type="order" onclick="filterTimeline('order')">📋 Orders</button>
        <button class="tl-filter ${timelineFilter==='surgery'?'active':''}" data-type="surgery" onclick="filterTimeline('surgery')">🔪 Surgery</button>
        <button class="tl-filter ${timelineFilter==='adt'?'active':''}" data-type="adt" onclick="filterTimeline('adt')">🏥 ADT</button>
        <button class="tl-filter ${timelineFilter==='radiology'?'active':''}" data-type="radiology" onclick="filterTimeline('radiology')">📷 Radiology</button>
      </div>
      ${events.length === 0 ? '<div class="empty">No clinical events recorded</div>' : sortedDates.map(date => `
        <div class="tl-date-group">
          <div class="tl-date" style="color:${dateColor(date)}">${date}</div>
          ${groups[date].map(e => `
            <div class="tl-event">
              <span class="tl-icon">${TL_ICONS[e.type]||'•'}</span>
              <span class="tl-type">${e.type}</span>
              <strong>${e.title || '—'}</strong>
              <span style="color:var(--muted)">${e.detail || ''}</span>
            </div>
          `).join('')}
        </div>
      `).join('')}
    </div>
  `;
}

// ── Immunizations ─────────────────────────────────────────────

async function loadImmunizations() {
  const dfn = currentDfn;
  try {
  const data = await api(`/api/patient/${dfn}/immunizations`);
  if (currentDfn !== dfn) return;
  const rows = data.immunizations || [];
  document.getElementById('sec-immunizations').innerHTML = `
    <div class="card">
      <h3><span style="color:${DOMAIN.immunizations.color}">${IC.immunizations}</span> Immunizations (${rows.length})</h3>
      ${rows.length === 0 ? '<div class="empty">No immunizations recorded</div>' : `
      <table>
        <thead><tr><th>Immunization</th><th>Series</th><th>Reaction</th></tr></thead>
        <tbody>${rows.map(r => `<tr>
          <td><strong>${r.immunization || '—'}</strong></td>
          <td>${r.series || '—'}</td>
          <td>${r.reaction || '—'}</td>
        </tr>`).join('')}</tbody>
      </table>`}
    </div>
  `;
  } catch(err) { console.error('loadImmunizations error:', err); }
}

// ── Surgeries ─────────────────────────────────────────────────

async function loadSurgeries() {
  const dfn = currentDfn;
  try {
  const data = await api(`/api/patient/${dfn}/surgeries`);
  if (currentDfn !== dfn) return;
  const rows = data.surgeries || [];
  document.getElementById('sec-surgeries').innerHTML = `
    <div class="card">
      <h3><span style="color:${DOMAIN.surgeries.color}">${IC.surgeries}</span> Surgical History (${rows.length})</h3>
      ${rows.length === 0 ? '<div class="empty">No surgical history</div>' : `
      <table>
        <thead><tr><th>Date</th><th>Procedure</th><th>Specialty</th><th>Type</th><th>Schedule</th><th>Admission</th></tr></thead>
        <tbody>${rows.map(r => {
          const schedCls = r.schedule_type==='EM'?'badge-dc':r.schedule_type==='EL'?'badge-active':'badge-pending';
          return `<tr>
          <td>${dateHtml(r.date_of_operation)}</td>
          <td>${r.procedure||'—'}</td>
          <td>${r.specialty||'—'}</td>
          <td>${SURG_TYPE[r.major_minor]||r.major_minor||'—'}</td>
          <td><span class="badge-pill ${schedCls}" onmouseenter="showTip(event,'${SURG_SCHEDULE[r.schedule_type]||r.schedule_type||''}')" onmouseleave="hideTip()">${SURG_SCHEDULE[r.schedule_type]||r.schedule_type||'—'}</span></td>
          <td onmouseenter="showTip(event,'${SURG_ADMISSION[r.admission_status]||''}')" onmouseleave="hideTip()" style="cursor:help">${SURG_ADMISSION[r.admission_status]||r.admission_status||'—'}</td>
        </tr>`}).join('')}</tbody>
      </table>`}
    </div>
  `;
  } catch(err) { console.error('loadSurgeries error:', err); }
}

// ── Radiology ─────────────────────────────────────────────────

async function loadRadiology() {
  const dfn = currentDfn;
  try {
  const data = await api(`/api/patient/${dfn}/rad_reports`);
  if (currentDfn !== dfn) return;
  const rows = data.rad_reports || [];
  document.getElementById('sec-radiology').innerHTML = `
    <div class="card">
      <h3><span style="color:${DOMAIN.radiology.color}">${IC.radiology}</span> Radiology Reports (${rows.length})</h3>
      ${rows.length === 0 ? '<div class="empty">No radiology reports</div>' : `
      <table>
        <thead><tr><th>Exam Date</th><th>Case #</th><th>Status</th><th>Verified</th></tr></thead>
        <tbody>${rows.map(r => `<tr>
          <td>${dateHtml(r.exam_date)}</td>
          <td>${r.day_case || '—'}</td>
          <td>${r.status === 'V' ? '<span class="badge-pill badge-active">Verified</span>' : r.status || '—'}</td>
          <td>${dateHtml(r.verified_date)}</td>
        </tr>`).join('')}</tbody>
      </table>`}
    </div>
  `;
  } catch(err) { console.error('loadRadiology error:', err); }
}

// ── Procedures ────────────────────────────────────────────────

async function loadProcedures() {
  const dfn = currentDfn;
  try {
  const data = await api(`/api/patient/${dfn}/procedures`);
  if (currentDfn !== dfn) return;
  const rows = data.procedures || [];
  document.getElementById('sec-procedures').innerHTML = `
    <div class="card">
      <h3><span style="color:${DOMAIN.procedures.color}">${IC.procedures}</span> Procedures (${rows.length})</h3>
      ${rows.length === 0 ? '<div class="empty">No procedures recorded</div>' : `
      <table>
        <thead><tr><th>CPT Code</th><th>Description</th></tr></thead>
        <tbody>${rows.map(r => `<tr>
          <td><strong>${r.cpt_code || '—'}</strong></td>
          <td>${r.provider_narrative || '—'}</td>
        </tr>`).join('')}</tbody>
      </table>`}
    </div>
  `;
  } catch(err) { console.error('loadProcedures error:', err); }
}

// ── Modal ─────────────────────────────────────────────────────

function showModal(html) {
  document.getElementById('modal-content').innerHTML = html;
  document.getElementById('modal').classList.add('show');
}
function closeModal() { document.getElementById('modal').classList.remove('show'); }
document.getElementById('modal').addEventListener('click', e => { if (e.target === e.currentTarget) closeModal(); });

// ── Clinical Write Operations ─────────────────────────────────

function showAddVitalForm() {
  if (!currentDfn) return;
  showModal(`
    <h3>Enter Vital Sign</h3>
    <div class="form-group">
      <label>Vital Type</label>
      <select id="wv-type">
        <option value="TEMPERATURE">Temperature</option>
        <option value="BLOOD PRESSURE">Blood Pressure</option>
        <option value="PULSE">Pulse</option>
        <option value="RESPIRATION">Respiration</option>
        <option value="WEIGHT">Weight</option>
        <option value="HEIGHT">Height</option>
        <option value="PAIN">Pain</option>
        <option value="PULSE OXIMETRY">Pulse Oximetry</option>
      </select>
    </div>
    <div class="form-group">
      <label>Reading</label>
      <input id="wv-reading" placeholder="e.g. 98.6, 120/80, 72">
    </div>
    <div class="form-actions">
      <button class="btn" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary" onclick="submitVital()">Save to MUMPS</button>
    </div>
  `);
}

async function submitVital() {
  const vtype = document.getElementById('wv-type').value;
  const reading = document.getElementById('wv-reading').value.trim();
  if (!reading) { showToast('Reading is required', '#dc2626'); return; }
  try {
    const resp = await fetch('/api/clinical/vital', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({patient_dfn: currentDfn, vital_type: vtype, reading})
    });
    const data = await resp.json();
    if (data.error) { showToast(data.error, '#dc2626'); return; }
    closeModal();
    showToast(`SET ${data.global_ref} — ${vtype}: ${reading}`, '#16a34a');
    loadVitalsLive();
    loadMumpsGlobals('vitals');
  } catch(e) { showToast(e.message, '#dc2626'); }
}

async function loadVitalsLive() {
  try {
    const data = await api(`/api/live/patient/${currentDfn}/vitals`);
    if (!data.vitals || data.vitals.length === 0) { loadVitals(); return; }
    loadVitals(data.vitals);
  } catch(e) { loadVitals(); }
}

function showAddProblemForm() {
  if (!currentDfn) return;
  showModal(`
    <h3>Add Problem</h3>
    <div class="form-group">
      <label>Problem Narrative</label>
      <input id="wp-narrative" placeholder="e.g. HYPERTENSION, DIABETES MELLITUS">
    </div>
    <div class="form-group">
      <label>Date of Onset</label>
      <input id="wp-onset" type="date">
    </div>
    <div class="form-group">
      <label>Status</label>
      <select id="wp-status">
        <option value="A">Active</option>
        <option value="I">Inactive</option>
      </select>
    </div>
    <div class="form-actions">
      <button class="btn" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary" onclick="submitProblem()">Save to MUMPS</button>
    </div>
  `);
}

async function submitProblem() {
  const narrative = document.getElementById('wp-narrative').value.trim();
  const dateOnset = document.getElementById('wp-onset').value;
  const status = document.getElementById('wp-status').value;
  if (!narrative) { showToast('Narrative is required', '#dc2626'); return; }
  try {
    const resp = await fetch('/api/clinical/problem', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({patient_dfn: currentDfn, narrative, status, date_onset: dateOnset})
    });
    const data = await resp.json();
    if (data.error) { showToast(data.error, '#dc2626'); return; }
    closeModal();
    showToast(`SET ${data.global_ref} — ${narrative} [${status}]`, '#16a34a');
    loadProblemsLive();
    loadMumpsGlobals('problems');
  } catch(e) { showToast(e.message, '#dc2626'); }
}

async function inactivateProblem(ien) {
  if (!ien) return;
  try {
    const resp = await fetch(`/api/clinical/problem/${ien}/inactivate`, {
      method: 'POST', headers: {'Content-Type':'application/json'}
    });
    const data = await resp.json();
    if (data.error) { showToast(data.error, '#dc2626'); return; }
    showToast(`SET ^AUPNPROB(${ien},0) $P12: A→I`, '#16a34a');
    loadProblemsLive();
    loadMumpsGlobals('problems');
  } catch(e) { showToast(e.message, '#dc2626'); }
}

async function loadProblemsLive() {
  try {
    const data = await api(`/api/live/patient/${currentDfn}/problems`);
    if (!data.problems) return;
    tabData.problems = data.problems;
    renderProblems();
  } catch(e) { loadProblems(); }
}

function showAddAllergyForm() {
  if (!currentDfn) return;
  showModal(`
    <h3>Add Allergy</h3>
    <div class="form-group">
      <label>Reactant</label>
      <input id="wa-reactant" placeholder="e.g. PENICILLIN, ASPIRIN, SHELLFISH">
    </div>
    <div class="form-group">
      <label>Type</label>
      <select id="wa-type">
        <option value="D">Drug</option>
        <option value="F">Food</option>
        <option value="O">Other</option>
      </select>
    </div>
    <div class="form-group">
      <label>Mechanism</label>
      <select id="wa-mechanism">
        <option value="ALLERGY">Allergy</option>
        <option value="PHARMACOLOGIC">Pharmacologic</option>
      </select>
    </div>
    <div class="form-actions">
      <button class="btn" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary" onclick="submitAllergy()">Save to MUMPS</button>
    </div>
  `);
}

async function submitAllergy() {
  const reactant = document.getElementById('wa-reactant').value.trim();
  const atype = document.getElementById('wa-type').value;
  const mechanism = document.getElementById('wa-mechanism').value;
  if (!reactant) { showToast('Reactant is required', '#dc2626'); return; }
  try {
    const resp = await fetch('/api/clinical/allergy', {
      method: 'POST', headers: {'Content-Type':'application/json'},
      body: JSON.stringify({patient_dfn: currentDfn, reactant, allergy_type: atype, mechanism})
    });
    const data = await resp.json();
    if (data.error) { showToast(data.error, '#dc2626'); return; }
    closeModal();
    showToast(`SET ${data.global_ref} — ${reactant} [${atype}]`, '#16a34a');
    loadAllergiesLive();
    loadMumpsGlobals('allergies');
  } catch(e) { showToast(e.message, '#dc2626'); }
}

async function loadAllergiesLive() {
  try {
    const data = await api(`/api/live/patient/${currentDfn}/allergies`);
    if (!data.allergies || data.allergies.length === 0) { loadAllergies(); return; }
    loadAllergies(data.allergies);
  } catch(e) { loadAllergies(); }
}

// ── MUMPS Panel ──────────────────────────────────────────────

let mumpsActive = false;
let mumpsOnline = false;
let currentMumpsTab = null;
let mumpsGlobalData = {};

const TAB_GLOBALS = {
  problems:      { global: '^AUPNPROB',  label: 'Problem List (File 9000011)' },
  allergies:     { global: '^GMR(120.8)', label: 'Allergy (File 120.8)' },
  vitals:        { global: '^GMR(120.5)', label: 'Vitals (File 120.5)' },
  meds:          { global: '^PSRX',       label: 'Prescription (File 52)' },
  orders:        { global: '^OR(100)',    label: 'Order (File 100)' },
  notes:         { global: '^TIU(8925)',  label: 'TIU Document (File 8925)' },
  consults:      { global: '^GMR(123)',   label: 'Consult (File 123)' },
  surgeries:     { global: '^SRF',        label: 'Surgery (File 130)' },
  schedule:      { global: '^SCE',        label: 'Scheduling (File 409.5)' },
  immunizations: { global: '^AUPNVIMM',  label: 'Immunization (File 9000010.11)' },
  procedures:    { global: '^AUPNVCPT',  label: 'Procedure (File 9000010.18)' },
  radiology:     { global: '^RARPT',      label: 'Rad Report (File 74)' },
};

async function checkMumpsStatus() {
  try {
    const resp = await fetch('/api/mumps/status');
    const data = await resp.json();
    mumpsOnline = data.status === 'online';
  } catch(e) { mumpsOnline = false; }
  const dot = document.getElementById('mumps-status-dot');
  dot.className = 'mumps-status ' + (mumpsOnline ? 'online' : 'offline');
}

function toggleMumpsPanel() {
  mumpsActive = !mumpsActive;
  document.querySelector('.layout').classList.toggle('mumps-active', mumpsActive);
  document.getElementById('mumps-toggle-btn').classList.toggle('active', mumpsActive);
  if (mumpsActive) {
    checkMumpsStatus();
    const activeTab = document.querySelector('.tab.active');
    if (activeTab && activeTab.dataset.tab && currentDfn) {
      loadMumpsGlobals(activeTab.dataset.tab);
    }
  }
}

async function loadMumpsGlobals(tab) {
  if (!mumpsActive || !currentDfn) return;
  currentMumpsTab = tab;
  const cfg = TAB_GLOBALS[tab];
  const body = document.getElementById('mumps-panel-body');
  const globalName = document.getElementById('mumps-global-name');
  const writeForm = document.getElementById('mumps-write-form');

  if (!cfg) {
    globalName.textContent = '';
    body.innerHTML = '<div class="mumps-empty">No MUMPS global mapping for this tab</div>';
    writeForm.style.display = 'none';
    return;
  }

  globalName.textContent = cfg.label;
  body.innerHTML = '<div class="mumps-loading">Loading globals...</div>';
  writeForm.style.display = 'block';

  try {
    const resp = await fetch(`/api/mumps/patient/${currentDfn}/globals/${tab}`);
    const data = await resp.json();
    mumpsGlobalData = data;

    if (!data.records || data.records.length === 0) {
      body.innerHTML = '<div class="mumps-empty">No records found in ' + escapeHtml(cfg.global) + '</div>';
      return;
    }

    let html = `<div class="mumps-section">
      <div class="mumps-section-title">${escapeHtml(cfg.global)} — ${data.records.length} record${data.records.length>1?'s':''} (of ${data.total_iens})</div>`;

    data.records.forEach((r, idx) => {
      const pieces = r.node_0 ? r.node_0.split('^') : [];
      html += `<div class="mumps-record" id="mrec-${idx}" onclick="toggleMumpsRecord(${idx}, '${escapeHtml(cfg.global)}', '${r.ien}')">
        <div><span class="mumps-ien">IEN ${r.ien}</span> <span class="mumps-ref">${escapeHtml(r.global_ref)}</span></div>
        <div class="mumps-val" style="margin-top:3px">${escapeHtml(r.node_0||'(empty)')}</div>
        <div class="mumps-pieces" style="margin-top:4px">
          ${pieces.map((p,i) => `<span class="mumps-piece-num">$P${i+1}:</span><span class="mumps-piece-val">${escapeHtml(p)||'""'}</span>`).join('')}
        </div>
        <div class="mumps-explore-nodes" id="mnodes-${idx}"></div>
      </div>`;
    });

    html += '</div>';
    body.innerHTML = html;
  } catch(e) {
    body.innerHTML = `<div class="mumps-empty" style="color:#f85149">Error: ${escapeHtml(e.message)}</div>`;
  }
}

async function toggleMumpsRecord(idx, globalName, ien) {
  const el = document.getElementById('mrec-' + idx);
  const nodesEl = document.getElementById('mnodes-' + idx);
  if (el.classList.contains('expanded')) {
    el.classList.remove('expanded');
    nodesEl.innerHTML = '';
    return;
  }
  el.classList.add('expanded');
  nodesEl.innerHTML = '<div style="color:#58a6ff;padding:4px 0">Exploring...</div>';

  try {
    const resp = await fetch(`/api/mumps/explore?global=${encodeURIComponent(globalName)}&ien=${ien}`);
    const data = await resp.json();
    let html = '<div class="mumps-global-tree">';
    if (data.top_value) {
      html += `<div class="mumps-node"><span class="mumps-node-key">${escapeHtml(globalName)}(${ien})</span><span class="mumps-node-eq">=</span><span class="mumps-node-val">${escapeHtml(data.top_value)}</span></div>`;
    }
    const keys = Object.keys(data.nodes || {}).sort((a,b) => {
      const na=parseFloat(a), nb=parseFloat(b);
      if (!isNaN(na) && !isNaN(nb)) return na-nb;
      return a.localeCompare(b);
    });
    keys.forEach(k => {
      const v = data.nodes[k];
      const pieces = v ? v.split('^') : [];
      html += `<div class="mumps-node">
        <span class="mumps-node-key">${escapeHtml(k)}</span><span class="mumps-node-eq"> = </span><span class="mumps-node-val">${escapeHtml(v||'""')}</span>
        ${pieces.length > 1 ? `<div class="mumps-pieces">${pieces.map((p,i) => `<span class="mumps-piece-num">$P${i+1}:</span><span class="mumps-piece-val">${escapeHtml(p)||'""'}</span>`).join('')}</div>` : ''}
      </div>`;
    });
    html += '</div>';
    nodesEl.innerHTML = html;
  } catch(e) {
    nodesEl.innerHTML = `<div style="color:#f85149">${escapeHtml(e.message)}</div>`;
  }
}

async function mumpsWrite() {
  const cfg = TAB_GLOBALS[currentMumpsTab];
  if (!cfg) return;
  const ien = document.getElementById('mw-ien').value.trim();
  const node = document.getElementById('mw-node').value.trim() || '0';
  const pieceStr = document.getElementById('mw-piece').value.trim();
  const value = document.getElementById('mw-value').value;
  const status = document.getElementById('mumps-write-status');

  if (!ien) { status.textContent = 'IEN required'; status.style.color='#f85149'; return; }

  status.textContent = 'Writing...'; status.style.color='#58a6ff';

  try {
    const body = {global: cfg.global, ien, node, value};
    if (pieceStr) body.piece = parseInt(pieceStr);
    const resp = await fetch('/api/mumps/write', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(body),
    });
    const data = await resp.json();
    if (data.error) {
      status.textContent = data.error; status.style.color='#f85149';
      return;
    }
    status.textContent = 'SET complete'; status.style.color='#3fb950';

    const diffHtml = `<div class="mumps-diff">
      <div style="color:#8b949e;font-size:10px;margin-bottom:4px">${escapeHtml(data.ref)}</div>
      <div class="mumps-diff-before">- ${escapeHtml(data.before||'(empty)')}</div>
      <div class="mumps-diff-after">+ ${escapeHtml(data.after||'(empty)')}</div>
    </div>`;
    const body2 = document.getElementById('mumps-panel-body');
    body2.insertAdjacentHTML('afterbegin', diffHtml);

    setTimeout(() => loadMumpsGlobals(currentMumpsTab), 500);
  } catch(e) {
    status.textContent = e.message; status.style.color='#f85149';
  }
}

init();