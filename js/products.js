(function(){
"use strict";
let products=[],site={},currentCategory='All',term='',priorFocus;
const $=s=>document.querySelector(s);
function el(tag,className,text){const out=document.createElement(tag);if(className)out.className=className;if(text!==undefined)out.textContent=text;return out;}
function money(value){return value===null||value===undefined||value===''?'Price on enquiry':'Rs. '+Number(value).toLocaleString('en-LK');}
function whatsApp(number,product){const digits=String(number||'94713433403').replace(/\D/g,'');let text=`Hello Greshy Likes Herbal, I would like to enquire about ${product.name}`;if(product.size)text+=` (${product.size})`;if(product.price!==null&&product.price!==undefined&&product.price!=='')text+=` — Rs. ${Number(product.price).toLocaleString('en-LK')}`;return `https://wa.me/${digits}?text=${encodeURIComponent(text+'. Please share availability and ordering details.')}`;}
function imageView(p){const box=el('div','product-image');if(p.images?.length){const pic=el('img');pic.src=p.images[0];pic.alt=p.name+' product photograph';pic.loading='lazy';pic.decoding='async';box.append(pic);}else box.append(el('div','product-placeholder','GRESHY LIKES'));
const label=el('span','product-eyebrow',p.priceCategory||p.category);box.append(label);
const button=el('button','product-image-button');button.type='button';button.setAttribute('aria-label','View details for '+p.name);button.addEventListener('click',()=>openModal(p));box.append(button);box.append(el('span','product-detail-cta','Discover product →'));return box;}
function card(p){const article=el('article','product-card');article.append(imageView(p));const info=el('div','product-info');
info.append(el('div','product-subcategory',p.size||'Greshy Likes Herbal'));
const title=el('h3'),titleButton=el('button','',p.name);titleButton.type='button';titleButton.addEventListener('click',()=>openModal(p));title.append(titleButton);info.append(title);
info.append(el('p','product-description',p.description||'Contact us to learn more about this product.'));
const detailsLink=el('a','product-page-link','View product page ↗');detailsLink.href='products/'+encodeURIComponent(p.id)+'.html';info.append(detailsLink);
const bottom=el('div','product-info-bottom'),left=el('div');left.append(el('p','product-price',money(p.price)));left.append(el('div','product-size',p.availability==='coming_soon'?'Coming soon':p.size||'Size on enquiry'));bottom.append(left);
if(p.availability==='coming_soon'){bottom.append(el('span','product-order','Coming soon'));}else{
const order=el('a','product-order','Enquire ↗');order.href=whatsApp(site.whatsapp,p);order.target='_blank';order.rel='noopener';order.setAttribute('aria-label','Enquire about '+p.name+' on WhatsApp');bottom.append(order);}
info.append(bottom);article.append(info);return article;}
function render(){
  const signature=products.filter(p=>p.section==='signature');
  const more=products.filter(p=>p.section!=='signature');
  const matches=more.filter(p=>(currentCategory==='All'||p.category===currentCategory)&&(!term||`${p.name} ${p.description||''} ${p.priceCategory||''} ${p.category}`.toLowerCase().includes(term)));
  $('#signatureGrid').replaceChildren(...signature.map(card));
  $('#signatureCount').textContent=String(signature.length).padStart(2,'0')+' SIGNATURE FRAGRANCES';
  $('.signature-section').hidden=signature.length===0;
  $('#productGrid').replaceChildren(...matches.map(card));
  $('#moreCount').textContent=matches.length+' '+(matches.length===1?'product':'products');
  $('#productEmpty').hidden=matches.length!==0;
}
function openModal(p){priorFocus=document.activeElement;const modal=$('#productModal');$('#modalName').textContent=p.name;$('#modalCategory').textContent=p.priceCategory||p.category;$('#modalDescription').textContent=p.description||'Contact us to learn more about this product.';$('#modalSize').textContent=p.size?'Size: '+p.size:'';$('#modalPrice').textContent=money(p.price);$('#modalAvailability').textContent=({'enquire':'Contact us to confirm availability','in_stock':'Available to order','out_of_stock':'Currently unavailable','coming_soon':'Coming soon'})[p.availability]||'Please enquire';
const img=$('#modalImage'),placeholder=$('#modalPlaceholder');img.hidden=!p.images?.length;placeholder.hidden=!!p.images?.length;if(p.images?.length){img.src=p.images[0];img.alt=p.name+' product image';}
const order=$('#modalOrder');order.hidden=p.availability==='coming_soon';order.href=whatsApp(site.whatsapp,p);order.textContent=p.availability==='out_of_stock'?'Ask about availability ↗':'Enquire on WhatsApp ↗';modal.hidden=false;document.body.classList.add('modal-open');$('#modalClose').focus();}
function closeModal(){document.body.classList.remove('modal-open');$('#productModal').hidden=true;priorFocus?.focus();}
function buildCategories(){const categories=['All',...new Set(products.filter(p=>p.section!=='signature').map(p=>p.category).filter(Boolean))];const parent=$('#filterPills');parent.replaceChildren(...categories.map(category=>{const b=el('button','pill'+(category==='All'?' active':''),category==='All'?'All other products':category);b.type='button';b.dataset.category=category;b.setAttribute('aria-pressed',category==='All'?'true':'false');b.addEventListener('click',()=>{currentCategory=category;parent.querySelectorAll('button').forEach(btn=>{btn.classList.toggle('active',btn===b);btn.setAttribute('aria-pressed',String(btn===b));});render();});return b;}));}
function initProducts(data,settings){products=(data||[]).filter(p=>p.published!==false);site=settings||{};buildCategories();render();
$('#productSearch').addEventListener('input',e=>{term=e.target.value.trim().toLowerCase();render();});
$('#modalClose').addEventListener('click',closeModal);document.querySelector('[data-close-modal]').addEventListener('click',closeModal);
document.addEventListener('keydown',e=>{if($('#productModal').hidden)return;if(e.key==='Escape')closeModal();if(e.key==='Tab'){const controls=[...$('#productModal').querySelectorAll('button:not([hidden]),a:not([hidden])')];const active=controls.filter(x=>!x.hidden);if(!active.length)return;if(e.shiftKey&&document.activeElement===active[0]){e.preventDefault();active[active.length-1].focus();}else if(!e.shiftKey&&document.activeElement===active[active.length-1]){e.preventDefault();active[0].focus();}}});}
window.GreshyProducts={initProducts};
})();
