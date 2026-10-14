# SEO and Automatic Updates — Greshy Likes Herbal

The same product information in `data/products.js` powers the homepage and is used to generate every product page. The generator embeds SEO titles, descriptions, canonical links, Open Graph tags, JSON-LD Product markup, product/category links, and the sitemap directly in the HTML.

## How to keep Google's copy correct

1. Edit and save `data/products.js` (or use `tools/edit-content.html`).
2. **Local:** Leave `START_AUTO_UPDATE.bat` running; it automatically regenerates the static pages and `dist/` after file changes.
3. **Git-connected site:** Push the updated catalogue. Netlify (`netlify.toml`) or the included GitHub Pages action runs the build and publishes it automatically.
4. **Manual static hosting:** Upload the regenerated `dist/` contents whenever you update products.

**Why build pages instead of updating only with JavaScript?** Product metadata and structured data are generated into crawlable HTML, so search engines and social media previews receive accurate details without relying on JavaScript execution.

## Publishing checks

- Your preferred canonical domain is set to `https://www.greshylikes.com/` in `scripts/rebuild_seo.py` and the homepage HTML. Verify the domain is owned/connected and that HTTPS works before submitting the sitemap.
- Choose one preferred hostname (`www` or bare domain) and set the host's redirect for the other hostname.
- Submit `https://www.greshylikes.com/sitemap.xml` through [Google Search Console](https://search.google.com/search-console/).
- Test a deployed individual product with [Google Rich Results Test](https://search.google.com/test/rich-results).
- Product availability is omitted from schema if unconfirmed; ratings/reviews and certifications are not invented.
- Generated product pages are removed from the sitemap when `published: false`. Production hosts may need a clean deployment to remove old files, so deploy the complete output directory rather than only adding updated pages.
- Search rankings or rich results are not guaranteed by implementing metadata.

## Troubleshooting

**Price changed on homepage but not in product HTML?** Confirm the watcher terminal is open and reports `Change detected`; otherwise run `BUILD_WEBSITE.bat`. If hosting online, ensure the updated files were deployed.

**Editor only downloads files?** Start `START_AUTO_UPDATE.bat` and open its local editor URL in Chrome or Edge. Click **Connect website folder**; choose the extracted project's main folder. Browsers that lack the File System Access API can still use Download JS + Replace.

**New product doesn't have a page?** Ensure `published` is true, its `id` contains only lowercase letters/digits/hyphens and is unique. The updater will create `/products/YOUR-ID.html` automatically. It also updates the sitemap.

**Need another domain?** Change `DOMAIN` in `scripts/rebuild_seo.py` and the canonical URL in the homepage, then rebuild and deploy. Your site and social sharing tags should agree.
