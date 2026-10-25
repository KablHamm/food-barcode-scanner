# Food Barcode Scanner → Home Assistant

A mobile-first web app that scans food barcodes with your phone camera, looks up
the product name (via Open Food Facts), and adds it to a list in Home Assistant.

## Files
- `index.html` — the whole app (single file, no build step)
- `server.py` — optional HTTPS dev server for testing on your phone
- `.certs/` — auto-generated self-signed certificate (created by server.py)

## Quick start (local testing on your PC)
Camera works on `localhost` over plain HTTP:

```powershell
cd "food-barcode-scanner"
python -m http.server 8000
# open http://localhost:8000 on this PC
```

To test on your phone (same Wi-Fi), use the HTTPS server so the camera is
allowed:

```powershell
cd "food-barcode-scanner"
python server.py            # serves on https://<your-pc-ip>:8443
```

Open the printed `Phone:` URL on your phone. Accept the self-signed certificate
warning (Advanced → Proceed). The phone and PC must be on the same network.

## Install from GitHub (recommended for phones)
This repo ships a GitHub Actions workflow that publishes the app to **GitHub Pages**
automatically, giving you a permanent HTTPS URL you can install from.

### One-time setup
1. Create a new (empty) repository on GitHub, e.g. `food-barcode-scanner`.
2. Upload all files from this folder to it (drag-and-drop on the GitHub web UI, or
   use git). Make sure the `.github/workflows/deploy.yml` file is included.
3. In the repo: **Settings → Pages → Source → "GitHub Actions"**.
4. Push/commit to `main` (or `master`). The workflow runs and deploys.
5. Your app is now at `https://<your-username>.github.io/food-barcode-scanner/`.

### Install on your phone
Open that URL in your phone browser, then:
- **Android (Chrome):** ⋮ → "Add to Home screen" (or "Install app")
- **iPhone (Safari):** Share (□↑) → "Add to Home Screen"

The service worker caches the app shell, so it opens instantly and works offline
(the camera + scans still need the page loaded; HA/Open Food Facts calls need
network).

### Updating
Edit files, commit/push — GitHub Pages redeploys automatically.

## Production: serve from Home Assistant (recommended)
If your Home Assistant is reachable over HTTPS, drop `index.html` into HA's
`www` folder:

1. Copy `index.html` to `/config/www/food-scanner.html` (via Samba, SSH, or the
   File Editor add-on).
2. Restart HA (or just reload).
3. Open `https://<your-ha>:8123/local/food-scanner.html` on your phone.
4. (Optional) Add to your phone home screen for an app-like feel.

## Home Assistant setup
### 1. Create a list to add items to
- **Todo (recommended):** Settings → Devices & Services → Add Integration →
  "Todo" is built in. A `todo.shopping_list` entity is usually auto-created by
  the Shopping list integration. Or create one via Helpers.
- **Shopping list (legacy):** Settings → Devices & Services → Add Integration →
  "Shopping list". Exposes `shopping_list.add_item`.

### 2. Create a Long-Lived Access Token
Profile (bottom-left avatar) → Security → Long-Lived Access Tokens → Create.
Copy the token into the app's Settings.

### 3. Allow CORS (required for browser → HA calls)
In `/config/configuration.yaml`, under `http:`, add:

```yaml
http:
  cors_allowed_origins:
    - "*"
```

(Or list your specific origin, e.g. `https://homeassistant.local:8123`.)
Restart Home Assistant. Without this, the browser blocks the requests.

### 4. Configure the app
Open the app → ⚙️ Settings:
- Home Assistant URL: `https://homeassistant.local:8123` (no trailing slash)
- Long-Lived Access Token: paste token
- List type: Todo (recommended) or Shopping list
- Todo entity ID: `todo.shopping_list` (find yours in Developer Tools → States)
- Test connection → should say "Connected to Home Assistant ✓"
- Save

## Usage
1. Point the camera at a food barcode. The app beeps/vibrates on a successful scan.
2. A card appears with the product name, brand, image, and quantity stepper.
3. Adjust quantity, tap **Add to list** (or Skip).
4. Items are added to your HA list and recorded in History (📋).

Manual entry (⌨️) lets you type a barcode if the camera can't read it.

## Notes & troubleshooting
- Barcodes must be in Open Food Facts to get a real product name; unknown codes
  are added as `Unknown product (<barcode>)` so you can still track them.
- Camera requires HTTPS on phones (or localhost on PC). Use `server.py` or serve
  from HA over HTTPS.
- Mixed content: if the app is served over HTTPS, your Home Assistant URL must
  also be HTTPS (browsers block HTTPS→HTTP calls). Serve the app from HA itself
  or put HA behind HTTPS (DuckDNS / Let's Encrypt / nginx).
- If scans repeat, the app has a 2.5s cooldown per identical barcode.
- Torch/flashlight toggle is browser-dependent; not all devices expose it.
- Quantities: by default the quantity is appended to the item name
  (`Milk x2`). Toggle "Add quantity to item name" in settings to disable.

## Privacy
All processing happens in your browser. The only network calls are to
Open Food Facts (product lookup) and your own Home Assistant instance.
No data is sent anywhere else.
