# Aiden Lapierre portfolio

A static editorial portfolio for photography, Model United Nations, technology, academics and other interests.

## Open the website

After cloning this repository, run python3 build.py to generate dist/. Open dist/index.html directly in a browser. All navigation uses relative links. The downloadable ZIP also includes prebuilt pages.

For a local server, install Python 3.10 or newer, open a terminal in this folder and run:

    python3 -m http.server 8000 --directory dist

Visit http://localhost:8000. On Windows, use py instead of python3 if needed.

## Edit and rebuild

1. Edit content/portfolio.json.
2. Place images and documents inside assets/.
3. Run python3 build.py.
4. Run python3 check.py.
5. Refresh the browser.

No packages need installation. Python builds the pages and is not needed on the deployed server. The checking script also uses Node to validate JavaScript syntax. The website itself has no runtime dependencies.

## Files

content/portfolio.json holds editable records.
build.py contains shared layouts and page templates.
assets/style.css holds the design system and responsive rules.
assets/gallery.js handles the menu and native-dialog viewer.
dist/ contains the deployable site.
CONTENT-GUIDE.md explains editing.
DESIGN-RESEARCH.md records research and design decisions.
CONTENT-NEEDED.md lists missing material.
QA.md records checks and verification limits.
check.py checks links, metadata, content and image generation.

## Deploy

Upload the contents of dist/ to a static host. No backend, secrets or server application is needed. If the host builds from source, set the build command to python3 build.py and the publish directory to dist. The host must support Python for that option.

Update siteUrl in the JSON to your deployment's absolute HTTPS URL before rebuilding. Include any subdirectory path. Set siteUrl to an empty string if the final address is unknown, which omits canonical tags and sitemap generation.

GitHub Pages deployment is prepared for realadlsmart-cpu/aiden-lapierre-portfolio. Choose Settings > Pages > Source > GitHub Actions. The included workflow builds, checks and deploys each main-branch update.

## Accessibility and images

The site uses semantic navigation, a skip link and visible focus. The viewer supports Enter/Space to open, left/right keys, Previous/Next, Escape and restored focus. Images preserve native ratios, use explicit dimensions, lazy loading and optional responsive variants. The featured homepage photo loads eagerly.

Export resized WebP or JPEG images. Image conversion is not automatic. Supply descriptive alt text. No analytics, cookies, external fonts or third-party scripts are included.

Contact details appear only after you approve an address and set contact.approved to true. This is your editorial publishing switch.