(function(){
'use strict';
const $=s=>document.querySelector(s);
function setText(id,txt){const el=document.getElementById(id);if(el&&typeof txt==='string')el.textContent=txt;}
function setImg(id,path){if(path){const img=document.getElementById(id);if(img)img.src=path;}}
// For titles, separate emphasized words with | and use a new line character for a line break.
function setTitle(id,txt){if(typeof txt!=='string')return;const target=document.getElementById(id);if(!target)return;target.replaceChildren();let emphasized=false;for(const segment of txt.split('|')){const bits=segment.split('\n');bits.forEach((bit,i)=>{if(i>0)target.append(document.createElement('br'));if(bit){if(emphasized){const em=document.createElement('em');em.textContent=bit;target.append(em);}else target.append(document.createTextNode(bit));}});emphasized=!emphasized;}}
function setSite(site){setText('brandDisplay',site.brand?.toUpperCase().replace(/ HERBAL$/,'')||'GRESHY LIKES');setText('footerBrandDisplay',site.brand?.toUpperCase().replace(/ HERBAL$/,'')||'GRESHY LIKES');setText('footerTagline',site.tagline);setText('headerTagline',site.tagline);setText('heroTagline',site.tagline);
['introText','collectionText','moreText','giftText','contactText','heroText','storyText'].forEach(id=>setText(id,site[id]));
['heroTitle','introTitle','collectionTitle','moreTitle','giftTitle','storyTitle','contactTitle'].forEach(id=>setTitle(id,site[id]));
setText('heroEyebrow',site.heroEyebrow);setText('storyEyebrow',site.storyEyebrow);setText('contactLocation',site.location);setText('footerLocation',site.location);setText('contactEmailText',site.email);
setImg('brandSymbolImage',site.logo);setImg('footerLogo',site.logo);setImg('heroImage',site.heroImage);setImg('storyImage',site.storyImage);setImg('featureImage',site.featureImage);
const digits=String(site.whatsapp||'94713433403').replace(/\D/g,'');['navWhatsapp','heroWhatsapp','contactWhatsapp','questionWhatsapp','socialFallback'].forEach(id=>{const e=document.getElementById(id);if(e)e.href='https://wa.me/'+digits+'?text='+encodeURIComponent('Hello Greshy Likes Herbal, I would like to enquire about your products.');});
['contactEmail','footerEmail','questionEmail'].forEach(id=>{const e=document.getElementById(id);if(e){e.href='mailto:'+site.email;if(id==='footerEmail')e.textContent=site.email;}});
let visible=0;for(const [key,id] of [['instagram','instagramLink'],['facebook','facebookLink'],['tiktok','tiktokLink']]){const e=document.getElementById(id);if(/^https:\/\//.test(site[key]||'')){e.href=site[key];e.hidden=false;visible++;}else e.hidden=true;}
$('#socialFallback').hidden=false;
if(site.seoTitle)document.title=site.seoTitle;
if(site.seoDescription)document.querySelector('meta[name="description"]').setAttribute('content',site.seoDescription);
}
function nav(){const toggle=$('#menuToggle'),mobile=$('#mobileNav');toggle.addEventListener('click',()=>{mobile.hidden=!mobile.hidden;toggle.setAttribute('aria-expanded',String(!mobile.hidden));});mobile.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{mobile.hidden=true;toggle.setAttribute('aria-expanded','false');}));window.addEventListener('scroll',()=>$('#backToTop').classList.toggle('visible',window.scrollY>700),{passive:true});}
function start(){nav();setText('year',String(new Date().getFullYear()));const site=window.GRESHY_SITE,products=window.GRESHY_PRODUCTS;if(!site||!Array.isArray(products)){document.getElementById('productGrid').textContent='Product information could not be loaded. Check the data files.';return;}setSite(site);window.GreshyProducts.initProducts(products,site);}
start();
})();
