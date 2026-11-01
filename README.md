# StudySignal - Independent CBSE Education Information Portal

**StudySignal** is an independent, free-access educational information portal created to provide Indian students, parents, and educators with clean, clutter-free, and verified information regarding Central Board of Secondary Education (CBSE) Class 10 (Secondary) and Class 12 (Senior Secondary) curricula, examination schedules, and academic circulars.

> **Important Non-Affiliation Notice:** StudySignal is an independent initiative and is **NOT** affiliated with, authorized by, or endorsed by the Central Board of Secondary Education (CBSE), Ministry of Education, or Government of India. Official CBSE information is hosted at [cbse.gov.in](https://www.cbse.gov.in) and [cbseacademic.nic.in](https://cbseacademic.nic.in).

---

## 📁 Project Architecture & Folder Structure

```
d:\exampulseindia\
│
├── app.py                      # Main Flask application and URL routing
├── config.py                   # Central configuration (Site metadata, Ad slots, Official links)
├── requirements.txt            # Python dependencies (Flask >= 3.0.0)
├── test_app.py                 # Automated test suite (regression, audit & deployment tests)
├── README.md                   # Beginner guide and documentation
│
├── data/
│   ├── syllabus.json           # CBSE Class 10 & 12 subject syllabus with verified official PDF links
│   ├── datesheets.json         # Exam schedules with official portal notices & labeled demo data
│   └── circulars.json          # Verified CBSE notifications and clearly labeled demo announcements
│
├── static/
│   ├── css/
│   │   └── style.css           # Responsive, mobile-first CSS (tricolor accent, cards, clean typography)
│   ├── js/
│   │   └── main.js             # Vanilla JS for mobile menu drawer, live filters & copy links
│   ├── images/
│   │   └── favicon.svg         # SVG favicon for the portal
│   └── robots.txt              # robots.txt pointing to dynamic sitemap
│
└── templates/
    ├── base.html               # Master layout with SEO meta, navbar, ad slots, footer, disclaimer
    ├── index.html              # Homepage (hero search, class hubs, featured syllabus, updates)
    ├── class_hub.html          # Dedicated CBSE Class 10 & 12 hubs (stream tabs, complete syllabus, guidelines)
    ├── syllabus.html           # Subject-wise syllabus catalog with Class, Stream, Year, and Query filters
    ├── syllabus_detail.html    # Single subject view with marks weightage, duration, and direct PDF download
    ├── datesheets.html         # Exam date sheets page with official CBSE status and labeled demo timetables
    ├── circulars.html          # CBSE circulars & updates feed with category filtering (Academic, Exam, Admin)
    ├── search.html             # Multi-filter search (by class, subject, category, and academic year)
    ├── about.html              # About StudySignal (Mission, Scope, Editorial integrity)
    ├── contact.html            # Contact & broken link reporting form
    ├── privacy.html            # Privacy Policy (Cookie disclosure, AdSense third-party compliance)
    ├── terms.html              # Terms and Conditions of website usage
    ├── disclaimer.html         # Comprehensive Legal Non-Affiliation Disclaimer
    ├── 404.html                # Custom 404 Not Found error page
    ├── 500.html                # Custom 500 Internal Server Error page
    └── components/
        ├── ad_slot.html        # Reusable, configurable advertising placement component
        ├── breadcrumb.html     # Accessible breadcrumb navigation
        └── notice_banner.html  # Non-affiliation and official advisory banner
```

---

## 🚀 How to Run the Website (Exact Commands)

This setup is compatible with free-tier tools and zero paid APIs. Python 3 is already installed on your system.

### Step 1: Open Terminal / PowerShell in the Project Directory
Make sure your working directory is `D:\exampulseindia`:
```powershell
cd D:\exampulseindia
```

### Step 2: Install Dependencies
Install Flask (lightweight, standard web framework):
```powershell
python -m pip install -r requirements.txt
```

### Step 3: Start the Website
Run the application:
```powershell
python app.py
```

You will see output similar to:
```
 * Serving Flask app 'app'
 * Debug mode: on
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### Step 4: Open in Your Browser
Open your browser and navigate to:
```
http://127.0.0.1:5000
```

---

## 🌐 Deploying on Render (Free Web Service)

StudySignal is production-ready for deployment on Render's free tier using Gunicorn WSGI.

### Render Dashboard Settings:
1. **Environment:** `Python`
2. **Region:** Choose the region nearest to India (e.g. `Singapore` or `Frankfurt`)
3. **Branch:** `main`
4. **Build Command:**
   ```bash
   pip install -r requirements.txt
   ```
5. **Start Command:**
   ```bash
   gunicorn --bind 0.0.0.0:$PORT app:app
   ```
   *(Note: `gunicorn app:app` is also supported as `gunicorn.conf.py` automatically binds to `$PORT`)*

### Environment Variables (Optional):
- `PYTHON_VERSION`: `3.11.9` (or `3.10` / `3.12`)
- `SECRET_KEY`: Set your custom production secret key
- `BASE_URL`: Leave blank or set to your custom domain (auto-detects `RENDER_EXTERNAL_URL`)
- `SHOW_DEMO_DATA`: `False` (when ready to hide demo timetable rows in live production)

---

## 🧪 Running Automated Tests

To verify all unit, audit, regression, and deployment tests:
```powershell
python -m unittest -v test_app.py
```
Expected output:
```
Ran 40+ tests in ~0.26s
OK
```

---

## ⚙️ Configuration & Customization Guide

### 1. Reusable Advertising Placements
Ad placements are centrally controlled in `config.py`:
```python
ADS = {
    "enabled": False,  # Master toggle: kept False until site approval
    "slots": {
        "header_leaderboard": {"enabled": True, "width": 728, "height": 90},
        "sidebar_box": {"enabled": True, "width": 300, "height": 250},
        "in_content_banner": {"enabled": True, "width": 728, "height": 90},
        "footer_banner": {"enabled": True, "width": 728, "height": 90}
    }
}
```
To insert real Google AdSense scripts or sponsor banners, open `templates/components/ad_slot.html` and replace the placeholder markup with your ad code.

### 2. Updating CBSE Syllabus Documents
Edit `data/syllabus.json`. Each entry holds:
- `class`: "10" or "12"
- `subject`: Subject name
- `code`: Official CBSE 3-digit subject code
- `official_url`: Direct verified URL to the syllabus PDF on `cbseacademic.nic.in`
- `exam_structure`: Theory marks, practical marks, duration

### 3. Date Sheets & Demo Labeling
Edit `data/datesheets.json`. In accordance with our policy, whenever the official date sheet is not yet published by the CBSE Examination Controller on `cbse.gov.in`, every sample timetable row is strictly marked with:
`[Demo Data / Placeholder: Official timetable to be announced by CBSE on cbse.gov.in]`

---

## 📋 What You Should Test Next

1. **Desktop & Mobile Navigation:** Resize your browser window below 768px and click the hamburger menu button in the top right to verify the slide-down mobile menu.
2. **Subject Syllabus Filter:** Go to `/cbse/syllabus`, use the Class, Stream, or Year dropdowns, and test the live search box.
3. **Class 12 Stream Tabs:** Go to `/cbse/class-12` and click between **Science Stream**, **Commerce Stream**, and **Arts / Humanities** tabs to see stream filtering in action.
4. **Unified Search:** Go to `/search` and search for "Mathematics", "Physics", or filter by category "Exam Date Sheets".
5. **Direct Official PDF Downloads:** Click any "Official PDF ↗" button to verify that it directly opens authentic CBSE syllabus documents from `cbseacademic.nic.in`.
6. **Contact Page:** Go to `/contact` to review the transparent message delivery advisory and official board contact directions.
7. **SEO Endpoints:** Visit `/robots.txt` and `/sitemap.xml` directly in your browser.
8. **Ad Toggle:** Open `config.py`, verify `ADS["enabled"]` is `False`, and confirm that advertising units remain hidden in production.
