# Flo Label Multiplier

Upload a shipping-label PDF (one label per page), enter **Qty per label**, and download a new PDF where every page is repeated in sequence.

Example: 3 pages, Qty = 2 → `L1, L1, L2, L2, L3, L3` (6 pages).

## Project structure

```
flo-label-multiplier/
├── app.py               # Flask backend (PDF duplication logic)
├── templates/
│   └── index.html       # Frontend UI (HTML + CSS + JS)
├── requirements.txt     # Python dependencies
├── render.yaml          # Optional Render Blueprint config
├── .python-version      # Python version for Render
├── .gitignore
└── README.md
```

---

## 1. Run it locally in VS Code

1. Install **Python 3.10+** (python.org) and **Git** (git-scm.com) if you don't have them.
2. Unzip the project and open the `flo-label-multiplier` folder in VS Code (**File → Open Folder**).
3. Open the terminal: **Terminal → New Terminal**.
4. Create and activate a virtual environment:

   **Windows (PowerShell)**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```
   If PowerShell blocks the script, run once:
   `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` and try again.

   **Mac / Linux**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

5. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
6. Run the app:
   ```bash
   python app.py
   ```
7. Open **http://localhost:5000** in your browser, upload a PDF and test.
8. Stop the server with `Ctrl + C`.

---

## 2. Push the code to GitHub

1. Go to https://github.com/new and create a new repository, e.g. `flo-label-multiplier`
   (Private is fine; leave "Add README" **unchecked**).
2. In the VS Code terminal (inside the project folder):
   ```bash
   git init
   git add .
   git commit -m "Initial commit: Flo Label Multiplier"
   git branch -M main
   git remote add origin https://github.com/<your-username>/flo-label-multiplier.git
   git push -u origin main
   ```
   The `.gitignore` keeps `venv/` and any PDFs out of the repo.

---

## 3. Deploy on Render

1. Sign in at https://dashboard.render.com (sign in with GitHub is easiest).
2. Click **New + → Web Service**.
3. Connect your GitHub account if asked, and select the `flo-label-multiplier` repo.
   (For a private repo, give Render access to it under "Configure GitHub App".)
4. Fill the settings:

   | Setting          | Value |
   |------------------|-------|
   | Name             | `flo-label-multiplier` |
   | Region           | Singapore (closest to India) |
   | Branch           | `main` |
   | Root Directory   | *(leave blank)* |
   | Runtime / Language | `Python 3` |
   | Build Command    | `pip install -r requirements.txt` |
   | Start Command    | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120` |
   | Instance Type    | Free (or Starter for no sleep) |

5. Under **Advanced → Environment Variables**, add:
   `PYTHON_VERSION` = `3.12.7`
6. (Optional) Under **Advanced → Health Check Path**, enter `/healthz`.
7. Click **Create Web Service**. Watch the logs — the build takes 1–3 minutes.
   When you see `Your service is live`, open the URL shown at the top
   (e.g. `https://flo-label-multiplier.onrender.com`).

### Alternative: deploy with the Blueprint (render.yaml)
**New + → Blueprint** → select the repo → Render reads `render.yaml` and fills
everything in automatically → **Apply**.

---

## 4. Updating the app later

Edit the code in VS Code, then:
```bash
git add .
git commit -m "Describe your change"
git push
```
Render auto-deploys every push to `main`.

---

## Notes

- **Free plan sleeps** after ~15 minutes of no traffic; the first visit after that takes ~30–60 seconds to wake up. Use the Starter plan if the warehouse team needs it instant.
- Files are processed in memory and never saved on the server.
- Limits: max upload 50 MB, Qty 1–50. Change `MAX_UPLOAD_MB` / `MAX_QTY` at the top of `app.py`.
- Page sizes are preserved exactly (4x6 labels stay 4x6).
- PDFs protected with an empty password (common with marketplace labels) are handled; truly password-locked PDFs show an error.
