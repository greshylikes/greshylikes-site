/* Product page live data: one catalogue also drives product pages after refresh.
   The static build still regenerates SEO metadata/JSON-LD for search engines. */
(() => {
  'use strict';
  const article = document.querySelector('.sub-product[data-product-id]');
  if (!article) return;
  const product = (window.GRESHY_PRODUCTS || []).find(p => p.id === article.dataset.productId);
  if (!product || product.published === false) {
    const order = document.querySelector('#pageWhatsapp');
    if (order) order.remove();
    document.querySelector('#pageAvailability').textContent = 'Please check our current catalogue';
    return;
  }
  const site = window.GRESHY_SITE || {};
  const set = (id, value) => {
    const node = document.getElementById(id);
    if (node) node.textContent = value;
  };
  const money = p => {
    const prices = [];
    if (p.price !== '' && p.price != null) prices.push('LKR ' + Number(p.price).toLocaleString('en-LK', {maximumFractionDigits: 2}));
    if (p.priceUsd !== '' && p.priceUsd != null) prices.push('USD ' + Number(p.priceUsd).toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 2}));
    return prices.join(' / ') || 'Price on enquiry';
  };
  const description = product.description || 'Contact us to learn more about this product.';
  const status = {
    in_stock: 'Available to order',
    out_of_stock: 'Currently unavailable',
    coming_soon: 'Coming soon',
    enquire: 'Please enquire to confirm availability'
  };
  set('pageName', product.name);
  set('pageCategory', (product.category || 'Product') + ' · GRESHY LIKES HERBAL');
  set('pagePrice', money(product));
  set('pageDescription', description);
  set('pageSize', product.size || 'Contact us for details');
  set('pageAvailability', status[product.availability] || 'Please enquire');

  const imageBox = document.querySelector('#pageImage');
  if (imageBox) {
    imageBox.replaceChildren();
    const source = product.images?.[0];
    if (source) {
      const img = document.createElement('img');
      img.src = '../' + source.replace(/^\/+/, '');
      img.alt = product.name + ' by Greshy Likes Herbal';
      img.width = 800;
      img.height = 600;
      imageBox.append(img);
    } else {
      const placeholder = document.createElement('div');
      placeholder.className = 'sub-no-photo';
      const heading = document.createElement('span');
      heading.textContent = product.name;
      const note = document.createElement('small');
      note.textContent = 'Product photograph coming soon';
      placeholder.append(heading, note);
      imageBox.append(placeholder);
    }
  }

  let order = document.querySelector('#pageWhatsapp');
  if (product.availability === 'coming_soon') {
    order?.remove();
  } else {
    if (!order) {
      order = document.createElement('a');
      order.className = 'sub-button';
      order.id = 'pageWhatsapp';
      const back = article.querySelector('.sub-secondary');
      back?.before(order);
    }
    const number = String(site.whatsapp || '94713433403').replace(/\D/g, '');
    let msg = 'Hello Greshy Likes Herbal, I would like to enquire about ' + product.name;
    if (product.size) msg += ' (' + product.size + ')';
    msg += '. Please confirm availability and ordering details.';
    order.href = 'https://wa.me/' + number + '?text=' + encodeURIComponent(msg);
    order.target = '_blank';
    order.rel = 'noopener';
    order.textContent = 'Enquire on WhatsApp ↗';
  }
})();
