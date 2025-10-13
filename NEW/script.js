/* Helper functions */
const $  = (s,root=document)=>root.querySelector(s);
const $$ = (s,root=document)=>Array.from(root.querySelectorAll(s));
function go(u){ location.href=u; }

/* Sidebar hover controller: keep expanded while hovering/clicking */
function setupSidebarHover(){
  const aside = document.querySelector('aside.sidebar');
  if(!aside) return;

  let isDown = false;
  let leaveTimer = null;
  const root = document.documentElement;

  const open  = () => root.classList.add('sb-open');
  const close = () => root.classList.remove('sb-open');

  aside.addEventListener('mouseenter', () => {
    if (leaveTimer) { clearTimeout(leaveTimer); leaveTimer = null; }
    open();
  });

  aside.addEventListener('mouseleave', () => {
    if (isDown) return;
    leaveTimer = setTimeout(close, 90);
  });
const $ = selector => document.querySelector(selector);
const $$ = selector => document.querySelectorAll(selector);

function go(page) {
  window.location.href = `${page}.html`;
}

document.addEventListener('DOMContentLoaded', () => {
  // Sidebar hover manager
  const sidebar = $('.sidebar');
  if (sidebar) {
    sidebar.addEventListener('mouseenter', () => document.documentElement.classList.add('sb-open'));
    sidebar.addEventListener('mouseleave', () => setTimeout(() => document.documentElement.classList.remove('sb-open'), 300));
  }

  // Year select persistence
  const yearSelect = $('#yearSelect');
  if (yearSelect) {
    yearSelect.value = sessionStorage.getItem('yearSelect') || '2023';
    yearSelect.addEventListener('change', () => sessionStorage.setItem('yearSelect', yearSelect.value));
  }

  // Password 👁 toggles
  $$('[data-toggle="password"]').forEach(btn => {
    btn.addEventListener('click', () => {
      const input = btn.previousElementSibling;
      input.type = input.type === 'password' ? 'text' : 'password';
    });
  });

  // Logout modal
  if (location.pathname.includes('logout.html')) {
    showModal('Are you sure you want to logout?', () => go('login'));
  }

  // Active nav highlight
  const current = location.pathname.split('/').pop().replace('.html', '');
  $$('nav a').forEach(link => {
    if (link.href.includes(current)) link.classList.add('active');
  });
});

// Modal logic
function showModal(message, onConfirm) {
  const backdrop = document.createElement('div');
  backdrop.className = 'modal-backdrop';
  backdrop.innerHTML = `
    <div class="modal">
      <h2>${message}</h2>
      <div class="modal-actions" style="flex-direction: row-reverse;">
        <button class="btn primary" id="confirmYes">Yes</button>
        <button class="btn" id="confirmCancel">Cancel</button>
      </div>
    </div>
  `;
  document.body.appendChild(backdrop);
  $('#confirmYes').onclick = () => {
    onConfirm();
    backdrop.remove();
  };
  $('#confirmCancel').onclick = () => backdrop.remove();
  backdrop.onclick = e => { if (e.target === backdrop) backdrop.remove(); };
}
  aside.addEventListener('mousedown', () => {
    isDown = true;
    open();
  });

  document.addEventListener('mouseup', () => {
    isDown = false;
    if (!aside.matches(':hover')) close();
  });
}

/* Logo click redirects to dashboard */
function setupLogo(){
  const logo = $('.logo');
  if (logo) logo.addEventListener('click', () => go('dashboard.html'));
}

/* Highlight active nav link */
function setActiveNav(){
  const file = location.pathname.split('/').pop() || 'dashboard.html';
  $$('aside .nav a').forEach(a=>{
    if(a.getAttribute('href')===file) a.classList.add('active');
  });
}

/* Remember year selection */
function setupTopbar(){
  const year=$('#year-select');
  if(year){
    const v = sessionStorage.getItem('yearSelect');
    if(v) year.value=v;
    year.addEventListener('change',()=>sessionStorage.setItem('yearSelect',year.value));
  }
}

/* Modal helpers */
function openModal(node){
  let b=$('.modal-backdrop');
  if(!b){
    b=document.createElement('div'); b.className='modal-backdrop';
    document.body.appendChild(b);
  }
  b.innerHTML=''; b.appendChild(node); b.style.display='flex';
  b.onclick=e=>{ if(e.target===b) closeModal(); };
}
function closeModal(){
  const b=$('.modal-backdrop');
  if(b){ b.style.display='none'; b.innerHTML=''; }
}

/* Logout confirmation */
function confirmLogout(){
  const node=document.createElement('div');
  node.className='modal';
  node.innerHTML=`
    <h3>Are you sure you want to logout?</h3>
    <div class="modal-actions">
      <button class="btn gray" id="cancel">Cancel</button>
      <button class="btn red" id="yes">Yes</button>
    </div>`;
  openModal(node);
  $('#cancel',node).onclick=closeModal;
  $('#yes',node).onclick=()=>{ closeModal(); go('login.html'); };
}
function wireLogout(){ 
  $$('[data-action="logout"]').forEach(x=>x.addEventListener('click',e=>{
    e.preventDefault(); confirmLogout();
  })); 
}

/* Icons for table actions */
const icons = {
  edit:`<svg class="icon" viewBox="0 0 24 24" fill="none"><path d="M4 17.25V20h2.75L17.81 8.94l-2.75-2.75L4 17.25z" stroke="currentColor" stroke-width="2"/><path d="M15.06 6.19l2.75 2.75" stroke="currentColor" stroke-width="2"/></svg>`,
  trash:`<svg class="icon" viewBox="0 0 24 24" fill="none"><path d="M3 6h18M8 6V4h8v2M6 6l1 14h10l1-14" stroke="currentColor" stroke-width="2"/></svg>`
};

/* Products page table + Create/Add New */
function initProducts(){
  const tbody = document.querySelector('#products-table tbody'); 
  if(!tbody) return;

  const addBtn = document.getElementById('createNew');

  let rows = [
    ['0001','Shin Ramyun — Spicy instant noodles','00','Noodles & Instant Meals','00','00.00'],
    ['0002','Chapagetti — Black bean noodles','00','Noodles & Instant Meals','00','00.00'],
    ['0003','Neoguri — Spicy seafood udon','00','Noodles & Instant Meals','00','00.00'],
    ['0004','Bibim Men — Cold spicy noodles','00','Noodles & Instant Meals','00','00.00'],
    ['0005','Japchae — Stir-fried glass noodles','00','Noodles & Instant Meals','00','00.00'],
    ['0006','Ottogi Cooked Rice — Pre-cooked rice packs','00','Rice & Grains','00','00.00'],
    ['0007','CJ Hetbahn — Instant white rice','00','Rice & Grains','00','00.00'],
    ['0008','Mixed Grain Rice (4-grain)','00','Rice & Grains','00','00.00'],
    ['0009','Glutinous Rice (Japanese)','00','Rice & Grains','00','00.00'],
    ['0010','Barley Rice','00','Rice & Grains','00','00.00']
  ];

  function render(){
    tbody.innerHTML='';
    rows.forEach((r,i)=>{
      const tr=document.createElement('tr');
      tr.innerHTML=`
        <td>${r[0]}</td>
        <td>${r[1]}</td>
        <td>${r[2]}</td>
        <td>${r[3]}</td>
        <td>${r[4]}</td>
        <td>${r[5]}</td>
        <td style="text-align:right">
          <div class="actions">
            <button class="icon-btn edit" data-i="${i}" title="Edit">${icons.edit}</button>
            <button class="icon-btn del"  data-i="${i}" title="Remove">${icons.trash}</button>
          </div>
        </td>`;
      tbody.appendChild(tr);
    });
    $$('.icon-btn.edit').forEach(b=>b.onclick=()=>openEdit(+b.dataset.i));
    $$('.icon-btn.del').forEach(b=>b.onclick=()=>openRemove(+b.dataset.i));
  }

  function openCreate(){
    const node=document.createElement('div');
    node.className='modal';
    node.innerHTML=`
      <h3>Create New Item</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        <label>Product ID<input class="field" id="nid" placeholder="e.g. 0011"></label>
        <label>Qty.<input class="field" id="nqty" value="0" type="number" min="0"></label>
        <label style="grid-column:1/-1">Product Name<input class="field" id="nname" placeholder="Product Name"></label>
        <label>Category<input class="field" id="ncat" placeholder="Category"></label>
        <label>Item Stock<input class="field" id="nstock" value="0" type="number" min="0"></label>
        <label>Retail Price<input class="field" id="nprice" value="0.00" type="number" step="0.01" min="0"></label>
      </div>
      <div class="modal-actions">
        <button class="btn gray" id="cancel">Cancel</button>
        <button class="btn primary" id="save">Add Item</button>
      </div>`;
    openModal(node);
    $('#cancel',node).onclick=closeModal;

    node.querySelectorAll('input').forEach(inp=>{
      inp.addEventListener('keydown',e=>{
        if(e.key==='Enter'){ e.preventDefault(); $('#save',node).click(); }
      });
    });

    $('#save',node).onclick=()=>{
      const id    = $('#nid',node).value.trim() || String(rows.length+1).padStart(4,'0');
      const name  = $('#nname',node).value.trim();
      const qty   = $('#nqty',node).value || '0';
      const cat   = $('#ncat',node).value.trim() || 'Uncategorized';
      const stock = $('#nstock',node).value || '0';
      const price = $('#nprice',node).value || '0.00';

      if(!name){
        $('#nname',node).focus();
        return;
      }
      if(rows.some(r=>r[0]===id)){
        alert('Product ID already exists. Please choose a different ID.');
        $('#nid',node).focus();
        return;
      }

      rows.push([id, name, qty, cat, stock, Number(price).toFixed(2)]);
      closeModal();
      render();
    };
  }

  function openEdit(i){
    const r = rows[i];
    const node=document.createElement('div');
    node.className='modal';
    node.innerHTML=`
      <h3>Edit Item</h3>
      <div style="display:grid;grid-template-columns:1fr 1fr;gap:12px">
        <label>Product ID<input class="field" id="eid" value="${r[0]}"></label>
        <label>Qty.<input class="field" id="eqty" value="${r[2]}"></label>
        <label style="grid-column:1/-1">Product Name<input class="field" id="ename" value="${r[1]}"></label>
        <label>Category<input class="field" id="ecat" value="${r[3]}"></label>
        <label>Item Stock<input class="field" id="estock" value="${r[4]}"></label>
        <label>Retail Price<input class="field" id="eprice" value="${r[5]}"></label>
      </div>
      <div class="modal-actions">
        <button class="btn gray" id="cancel">Cancel</button>
        <button class="btn primary" id="save">Save</button>
      </div>`;
    openModal(node);
    $('#cancel',node).onclick=closeModal;
    $('#save',node).onclick=()=>{
      rows[i]=[
        $('#eid',node).value,$('#ename',node).value,$('#eqty',node).value,
        $('#ecat',node).value,$('#estock',node).value,$('#eprice',node).value
      ];
      closeModal(); render();
    };
  }

  function openRemove(i){
    const node=document.createElement('div');
    node.className='modal';
    node.innerHTML=`
      <h3 style="text-align:center;margin:14px 0">Are you sure you want to remove this item?</h3>
      <div class="modal-actions" style="justify-content:center">
        <button class="btn red" id="yes">Yes</button>
        <button class="btn gray" id="cancel">Cancel</button>
      </div>`;
    openModal(node);
    $('#cancel',node).onclick=closeModal;
    $('#yes',node).onclick=()=>{ rows.splice(i,1); closeModal(); render(); };
  }

  if(addBtn) addBtn.addEventListener('click', openCreate);
  render();
}

/* Initialisation */
document.addEventListener('DOMContentLoaded', ()=>{
  setupSidebarHover();
  setupLogo();
  setActiveNav();
  setupTopbar();
  wireLogout();
  if(document.body.dataset.page==='products') initProducts();
  if(document.body.dataset.page==='logout'  && typeof confirmLogout==='function') confirmLogout();
});

/* Example promotions grid (left as-is from your original) */
const promotions = [
  { id:'ramen1', name:'Shin Ramyun', category:'ramen-bundle', img:'images/shin-ramyun.png', price:30,   stock:10, description: ['4 x Shin Cup', '1 x Kimchi'] },
  { id:'shabu1', name:'Shabu Bundle (Beef)', category:'shabu', img:'images/shabu-beef.png', price:2000, stock:0,  description: ['Shabu Balls', 'Prawn Balls', 'Vegetables'] }
];

function renderPromotions(category='all'){
  const grid = document.getElementById('promoGrid');
  if(!grid) return;
  grid.innerHTML = '';
  promotions.filter(p=> category==='all' || p.category===category)
            .forEach(p=>{
    const card = document.createElement('div');
    card.className = 'promo-item';
    card.dataset.id = p.id;
    card.innerHTML = `
      <img src="${p.img}" alt="${p.name}">
      <div class="name">${p.name}</div>
      <div class="price">₱ ${p.price.toFixed(2)}</div>
      <div class="stock">${p.stock > 0 ? 'In stock ('+p.stock+')' : 'Out of stock'}</div>
    `;
    card.onclick = ()=> showDetail(p);
    grid.appendChild(card);
  });
}

function showDetail(product){
  const name = document.getElementById('detailName');
  if(!name) return;
  name.textContent = product.name;
  const list = document.getElementById('detailList');
  list.innerHTML = '';
  product.description.forEach(item=>{
    const li = document.createElement('li');
    li.textContent = item;
    list.appendChild(li);
  });
  document.getElementById('detailSubtotal').textContent = `₱ ${product.price.toFixed(2)}`;
  document.getElementById('detailTotal').textContent = `₱ ${product.price.toFixed(2)}`;
  document.getElementById('promoDetail').style.display = 'block';
}

const tabs = document.getElementById('promoTabs');
if(tabs){
  tabs.addEventListener('click', function(e){
    if(!e.target.classList.contains('promo-tab')) return;
    document.querySelectorAll('.promo-tab').forEach(tab=> tab.classList.remove('active'));
    e.target.classList.add('active');
    renderPromotions(e.target.dataset.category);
    document.getElementById('promoDetail').style.display = 'none';
  });
  document.addEventListener('DOMContentLoaded', ()=> renderPromotions());
}