# Greshy Likes Herbal — Auto-Updating Static Website

**One catalogue. Automatic product pages. Search-engine-friendly static HTML.**

The public website uses ordinary HTML, CSS and JavaScript. There is **no website database, login or backend**. Product details are stored in a single editable catalogue: `data/products.js`.

## Quick start — Windows (recommended)

1. Extract the ZIP, keeping every folder in place.
2. Install **Python 3** if not already installed (select **Add Python to PATH** during setup). No Python packages or Node.js are needed.
3. Double-click **`START_AUTO_UPDATE.bat`** and leave its terminal window open while editing.
4. The local content editor will open at **http://127.0.0.1:8765/tools/edit-content.html**. If it does not open automatically, open that address in Chrome or Edge.
5. The editor connects to the local updater automatically. No folder selection is needed. If you open the editor directly as a file, use **Connect website folder** as an alternative.
6. Edit Royal Bloom (or any product) and click **Save product changes**. For brand and contact edits, click **Save website changes**. Use **Publish changes to local website** to save both forms together. The updated `data/products.js` will be saved and the updater will automatically rebuild *all* SEO HTML pages, related-product listings, collection pages, sitemap and `dist/`.
7. Refresh **http://127.0.0.1:8765/products/royal-bloom.html** to view changes. The homepage is at **http://127.0.0.1:8765/**. The updater now also rewrites the visible text inside the actual `index.html` source from `data/site.js`, so View Source and search engines see the new text.

**Works without folder access too:** Use the editor's **Download products.js** or **Download site.js** buttons, and replace the matching file inside `data/`. While the updater is running, the new pages are still generated automatically.

**If Python isn't installed:** `index.html` can be opened as a normal static website, and product pages will read current product details on refresh with JavaScript. However, the fully crawlable HTML and SEO metadata need the generator to run locally or on your Git-connected hosting provider.

## What's automatic, and what isn't?

| Change | Local homepage or product display | Search-engine HTML, meta tags, JSON-LD, sitemap | Public website |
|---|---|---|---|
| Edit `data/products.js` | Refresh to see changes | Auto-rebuild **while `START_AUTO_UPDATE.bat` is running** | Only after you deploy updated files |
| Edit `data/site.js` | Refresh to see changes | Same automatic rebuild | Only after deployment |
| Commit updated catalogue to connected Netlify or GitHub Pages | Rebuilt during hosting deployment | Rebuilt automatically by provided configuration | Auto-published after successful build |
| Upload files manually to shared/cPanel hosting | Refresh after upload | Upload regenerated `dist/` output | Manually upload to hosting |

**Editing directly on the live website cannot update hosted files:** static hosting needs uploaded files or a connected Git workflow. This package does not contain a cloud CMS or administrator login.

## Publish online — three ways

### Netlify + Git repository (automatic deployments)

1. Upload the complete **source project** to a GitHub repository (including `netlify.toml`, `scripts/`, `data/`, etc.).
2. In Netlify, import that repository. The included `netlify.toml` already sets:
   - Build command: `python3 scripts/build_site.py`
   - Publish directory: `dist`
3. Connect and verify your domain in Netlify (HTTPS and DNS must also be set up).
4. Whenever you push `data/products.js` or `data/site.js` to the repository, Netlify generates and publishes the new HTML, JSON-LD and sitemap without a manual rebuild.

### GitHub Pages (automatic deployments)

1. Upload the full source project to a GitHub repository on the `main` branch.
2. In **Settings → Pages → Build and deployment**, choose **GitHub Actions**.
3. The included `.github/workflows/deploy.yml` automatically builds and deploys when relevant files change on `main`.
4. Configure the site's **custom domain** and DNS. The canonical URLs currently use `https://www.greshylikes.com/`. If your actual domain differs, change `DOMAIN` in `scripts/rebuild_seo.py` and the homepage canonical tag before publishing.
5. To make future updates, commit/push the edited catalogue or site data. The action regenerates the site automatically.

**Note:** The GitHub workflow uploads the `dist/` directory and does not deploy local editing tools. GitHub Pages default `github.io` project URLs will not match the `www.greshylikes.com` canonicals unless the intended domain is connected.

### Ordinary static / cPanel hosting (manual uploads)

1. Keep `START_AUTO_UPDATE.bat` running while editing, or run `BUILD_WEBSITE.bat` after edits.
2. Upload the **contents inside** `dist/` to the web root (`public_html` or equivalent).
3. Do **not** upload `tools/`, `scripts/`, `.github/`, or the build BAT files to the public web root.
4. When you change a product later, regenerate `dist/` and upload its changed contents again. Shared hosting cannot see changes on your own computer automatically.

## File structure

```text
Greshy_Likes_Auto_SEO_Website/
├── index.html                   Public homepage
├── data/
│   ├── products.js              ← ONE product catalogue; edit here
│   └── site.js                  ← Brand wording, logo, WhatsApp and SEO settings
├── products/                    ← Auto-generated individual HTML pages
├── perfumes/                    ← Auto-generated category page
├── personal-care/               ← Auto-generated category page
├── car-fragrance/               ← Auto-generated category page
├── sitemap.xml                  ← Auto-generated URL list
├── robots.txt                   ← Search crawler instructions
├── js/                          Website JavaScript (includes product-live.js)
├── css/                         Website styling
├── assets/images/               Product photography
├── tools/edit-content.html      Local offline product editor
├── scripts/
│   ├── rebuild_seo.py           Page + SEO generator (Python standard library)
│   ├── build_site.py            Generator + safe deployment-folder exporter
│   └── watch_and_build.py       Watches data and starts local preview/editor
├── START_AUTO_UPDATE.bat        Double-click on Windows to edit + auto-rebuild
├── BUILD_WEBSITE.bat            Manual build / regenerate deployment folder
├── netlify.toml                 Netlify build instructions
├── .github/workflows/deploy.yml GitHub Pages CI deployment
├── dist/                        ← Upload/publish THIS folder's contents
└── SEO_GUIDE.md                 Search optimization notes
```

## Editing a product

Edit **Royal Bloom** in the content editor, or open `data/products.js` and change its `price`, `description`, `size`, `images` or `availability`. The ID `royal-bloom` must remain stable so its URL stays `/products/royal-bloom.html`.

- **Signature Perfumes:** 10 perfume products in the first collection; other six products in the second collection.
- **Pricing tiers:** optional. Personal care products may have prices without a perfume pricing category.
- **Product images:** click **Upload image** in the editor and choose a PNG, JPG, WebP or GIF (up to 10 MB). The photo is copied into `assets/images/`, its path is filled automatically, and a preview appears. Click **Save product changes** or **Publish changes to local website** to update the catalogue and include the photo in `dist/`. Existing photos can still be selected from the path field. Uploads require the local updater or a connected website folder.
- **Published products:** setting `published: false` removes the dedicated page, related links, and sitemap URL on the next build.
- **Product categories:** the generator supplies category pages for Perfumes, Personal Care, and Car Fragrance. New categories still appear as homepage filters, but may require an additional SEO category template.

## Notes

- The live product page includes a lightweight browser script that reads the latest `data/products.js` as a convenience. The **automatic build** separately writes static HTML and structured data for search engines. Do not rely on browser-only updates as your SEO publishing workflow.
- Keep product availability honest: no products were marked in stock without confirmation. Missing photographs remain placeholders.
- When changing the business domain, edit the `DOMAIN` constant in `scripts/rebuild_seo.py` and homepage canonical URL before building.
- Review your Privacy/Terms pages and use Google Search Console after the site is actually published.

## Automatic homepage source updates

When you change `data/site.js`, the builder now regenerates **both the browser display and the homepage `index.html` source**, including the hero, headings, brand text, contact links, photo paths and SEO metadata. No need to edit `index.html` manually.

1. Start `START_AUTO_UPDATE.bat` and leave it running.
2. Edit `data/site.js` (or save through the connected content editor).
3. The watcher detects the change and rebuilds `index.html` plus `dist/index.html`.
4. Refresh the page. If hosted publicly, publish the updated `dist/` or push to your connected Git hosting provider.

Your public static hosting cannot detect changes made only on your PC. For automatic public deployment, push source changes to your configured Netlify or GitHub Pages build.

## Save and publish from the editor

While `START_AUTO_UPDATE.bat` is running, Save writes the corresponding file in `data/` and rebuilds the homepage, product and category pages, sitemap, and `dist/` before confirming success. New products appear when their **Display this product on the website** checkbox is checked and you save. Removing a product also saves and rebuilds. Publish saves both product and website forms and prepares the local `dist/` output; public deployment still requires uploading `dist/` or pushing to your configured Git host. Refresh open website tabs after saving.

Product descriptions: edit **Short description** for homepage cards, collection cards and the product popup. The existing **Long description** is used on the full product page.

Prices: edit **Price in LKR** and **Price in USD** independently in Products & Prices. Both entered prices appear together. A blank currency price is omitted; when both are blank, customers see “Price on enquiry”. USD values are not automatically converted.
