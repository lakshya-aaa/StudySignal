# StudySignal – Independent Indian Education & Examination Information Portal

**StudySignal** is an independent, free-access educational information platform designed to help Indian students, parents and educators find verified information about school boards, competitive examinations, academic syllabi, examination schedules, previous-year question papers, official notifications and admission resources.

StudySignal brings information from multiple official education boards and examination authorities together in one accessible platform.

> **Important Non-Affiliation Notice:** StudySignal is an independent educational information portal. It is not affiliated with, authorized by, sponsored by or endorsed by CBSE, UPMSP, CISCE, BSEB, MSBSHSE, NTA, IITs, JAB, any participating university, the Ministry of Education or the Government of India. Official information remains the responsibility of the respective authorities. StudySignal provides convenient access to publicly available information and links to original official sources.

---

# 1. Supported Education Boards & Examinations

StudySignal currently integrates nine education and examination portals.

## A. School Education Boards

| Board | Full Name | Classes / Examinations |
|---|---|---|
| CBSE | Central Board of Secondary Education | Class 10 and Class 12 |
| UP Board | Uttar Pradesh Madhyamik Shiksha Parishad (UPMSP) | High School and Intermediate |
| CISCE | Council for the Indian School Certificate Examinations | ICSE Class 10 and ISC Class 12 |
| Bihar Board | Bihar School Examination Board (BSEB) | Matriculation and Intermediate |
| Maharashtra Board | Maharashtra State Board of Secondary and Higher Secondary Education (MSBSHSE) | SSC and HSC |

## B. National Competitive Examinations

| Examination | Conducting Authority / Responsible Body | Purpose |
|---|---|---|
| JEE Main | National Testing Agency (NTA) | Engineering entrance |
| JEE Advanced | IIT organising institute under JAB | IIT admissions |
| NEET UG | National Testing Agency (NTA) | Medical undergraduate entrance |
| CUET UG | National Testing Agency (NTA) | Undergraduate university admissions |

**Important:** JEE Main and JEE Advanced are maintained as separate examination portals because they have different examination authorities, eligibility requirements and admission processes.

---

# 2. Main Features

## School Board Resources

- Board-specific portals.
- Class 10 and Class 12 hubs.
- Official syllabus directories.
- Subject-wise syllabus information.
- Official sample and model papers.
- Verified previous-year question papers, where officially available.
- Question bank directories and availability trackers.
- Examination date sheets.
- Official circulars and notifications.
- Results and official result portal links.
- Board-specific information and announcements.

## Competitive Examination Resources

Dedicated portals for:

- JEE Main
- JEE Advanced
- NEET UG
- CUET UG

Available resource categories include:

- Official examination syllabus.
- Examination pattern.
- Eligibility criteria.
- Information bulletins.
- Important examination dates.
- Official previous-year question papers.
- Admit card information.
- Exam city intimation information.
- Official answer keys.
- Results.
- Counselling and admission information.
- Notifications and corrections.
- Participating university information for CUET UG.

Resource availability varies by examination and academic session.

## Search & Discovery

- Unified search across supported boards and examinations.
- Board-specific and examination-specific filtering.
- Subject and resource category filtering.
- Direct access to official resource documents.
- Search results separated by the relevant board or examination.

## Unified Examination Calendar – Planned

A centralized examination calendar is planned to bring together important dates from all nine portals.

Planned capabilities:

- School board examination schedules.
- Competitive examination schedules.
- Registration deadlines.
- Application correction windows.
- Admit card announcements.
- Examination dates.
- Answer key releases.
- Results and counselling milestones.
- Monthly calendar and chronological list views.
- Filters by board, examination and event category.
- Examination countdowns.

The calendar will use verified official examination information. It will not display invented or unannounced dates as confirmed events.

---

# 3. Official Information & Verification Policy

StudySignal prioritizes factual accuracy and source authenticity.

Only information supported by the respective board, examination authority or an authorized official government source should be presented as official.

### Resource verification

Every listed resource should be checked for:

- Authenticity of the publishing authority.
- Correct board or examination.
- Relevant class, subject or examination paper.
- Academic session or examination year.
- Working official source URL.
- Valid document or PDF, where applicable.
- Last verification date.

### Strict resource classification

StudySignal distinguishes between:

1. Actual Previous-Year Question Papers (PYQs).
2. Official Sample Papers.
3. Official Model Papers.
4. Official Question Banks.
5. Official Mock Tests and Practice Materials.

These categories must never be incorrectly combined.

For example, model question papers must not be presented as actual previous-year examination papers.

### Unavailable resources

If a board or examination authority does not provide a particular resource:

- Do not fabricate an entry.
- Do not substitute unofficial documents.
- Clearly indicate that the resource is unavailable or awaiting official release.
- Do not publish unverified download links.

### Official source links

All documents and important announcements should link to their original official sources wherever possible.

StudySignal is an information and discovery platform, not an examination authority.

---

# 4. Project Architecture & Folder Structure

The project is built using Flask and Python, with JSON-based data storage and reusable Jinja2 templates.

```text
D:\exampulseindia\
│
├── app.py
├── config.py
├── requirements.txt
├── README.md
├── test_app.py
│
├── data/
│   ├── syllabus.json
│   ├── datesheets.json
│   ├── circulars.json
│   │
│   ├── bseb_sample_papers.json
│   ├── bseb_datesheets.json
│   ├── bseb_syllabus.json
│   ├── bseb_circulars.json
│   │
│   ├── maha_datesheets.json
│   ├── maha_pyq.json
│   ├── maha_question_bank.json
│   ├── maha_syllabus.json
│   ├── maha_circulars.json
│   │
│   ├── jee_main.json
│   ├── jee_advanced.json
│   ├── neet_ug.json
│   └── cuet_ug.json
│
├── static/
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   └── main.js
│   │
│   ├── images/
│   │   ├── boards/
│   │   │   ├── cbse-logo.png
│   │   │   ├── upmsp-logo.png
│   │   │   ├── cisce-logo.png
│   │   │   ├── bseb-logo.png
│   │   │   └── msbshse-logo.png
│   │   │
│   │   ├── exams/
│   │   │   ├── nta-logo.png
│   │   │   └── jee-adv-logo.png
│   │   │
│   │   └── favicon.svg
│   │
│   └── robots.txt
│
└── templates/
    ├── base.html
    ├── index.html
    ├── boards.html
    ├── class_hub.html
    ├── icse_class_hub.html
    ├── upmsp_class_hub.html
    ├── bseb.html
    ├── bseb_class_hub.html
    ├── maha.html
    ├── maha_class_hub.html
    │
    ├── exams/
    │   ├── _subnav.html
    │   ├── hub.html
    │   ├── syllabus.html
    │   ├── exam_pattern.html
    │   ├── eligibility.html
    │   ├── important_dates.html
    │   ├── information_bulletin.html
    │   ├── pyq.html
    │   ├── portal_tracker.html
    │   ├── notifications.html
    │   ├── counselling.html
    │   └── universities.html
    │
    ├── components/
    │   ├── ad_slot.html
    │   ├── breadcrumb.html
    │   └── notice_banner.html
    │
    ├── search.html
    ├── about.html
    ├── contact.html
    ├── privacy.html
    ├── terms.html
    ├── disclaimer.html
    ├── 404.html
    └── 500.html
```

**Note:** This is a high-level representation of the main project structure. Refer to the actual project directory for the complete and current list of data files, templates and assets.

---

# 5. Local Development Setup

The project can be run locally using Python and Flask.

### Step 1: Open PowerShell

```powershell
cd D:\exampulseindia
```

### Step 2: Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### Step 3: Start the Flask application

```powershell
python app.py
```

### Step 4: Open StudySignal

Visit:

```text
http://127.0.0.1:5000
```

Stop the development server using:

```text
CTRL + C
```

---

# 6. Dependencies

The application uses Python and Flask.

Install all dependencies using:

```powershell
python -m pip install -r requirements.txt
```

The production application uses Gunicorn as its WSGI server.

Keep `requirements.txt` updated whenever new dependencies are introduced.

---

# 7. Production Deployment – Render

StudySignal can be deployed as a Flask web service on Render.

### Render Configuration

| Setting | Value |
|---|---|
| Environment | Python |
| Branch | main |
| Build Command | `pip install -r requirements.txt` |
| Start Command | `gunicorn --bind 0.0.0.0:$PORT app:app` |

### Environment Variables

Recommended configuration:

```text
PYTHON_VERSION=3.11.9
SECRET_KEY=your-secure-secret-key
```

Optional:

```text
BASE_URL=https://your-domain.com
SHOW_DEMO_DATA=False
```

Use the actual deployed domain for `BASE_URL` when required by the application configuration.

Do not expose secret keys or credentials in the repository.

### Deployment Workflow

1. Make and test changes locally.
2. Review modified files.
3. Run the automated test suite.
4. Commit changes to Git.
5. Push to the configured GitHub branch.
6. Check the Render deployment.
7. Verify the live website.

If automatic deployment is enabled, Render should deploy after a successful push to the configured branch.

---

# 8. Automated Testing

StudySignal includes an automated regression and integration test suite in:

```text
test_app.py
```

Run all tests using:

```powershell
python -m unittest -v test_app.py
```

The test suite covers areas such as:

- School board portal routes.
- Competitive examination routes.
- Board and examination registries.
- Homepage and navigation integration.
- Data integrity.
- PYQ classification.
- Search functionality.
- Canonical URLs.
- Sitemap generation.
- Official resource availability handling.
- Logo assets and template rendering.
- Regression protection for existing portals.

**Latest reported test result:** 104 tests passed.

Run the tests again after every substantial development change. The test count and result in this README should be updated when the suite changes.

---

# 9. SEO and Discoverability

StudySignal includes SEO-related functionality such as:

- Page-specific titles and descriptions.
- Canonical URLs.
- XML sitemap.
- Robots.txt.
- Open Graph metadata.
- Responsive page layouts.
- Search-friendly content organization.
- Internal linking between relevant boards and examinations.

Important endpoints:

```text
/robots.txt
/sitemap.xml
```

Ensure newly added pages are included in the sitemap where appropriate.

Do not index duplicate, retired or unavailable resource routes.

---

# 10. Advertising & Monetization

StudySignal is designed with configurable advertising placements.

Advertising can be controlled centrally through `config.py`.

Example configuration:

```python
ADS = {
    "enabled": False,
    "slots": {
        "header_leaderboard": {
            "enabled": True,
            "width": 728,
            "height": 90
        },
        "sidebar_box": {
            "enabled": True,
            "width": 300,
            "height": 250
        },
        "in_content_banner": {
            "enabled": True,
            "width": 728,
            "height": 90
        },
        "footer_banner": {
            "enabled": True,
            "width": 728,
            "height": 90
        }
    }
}
```

The master advertising switch is currently configured to remain disabled until the relevant advertising provider approvals and production configuration are completed.

Reusable advertising markup is located in:

```text
templates/components/ad_slot.html
```

Before enabling advertising:

- Obtain approval from the selected advertising provider.
- Configure the actual advertising code.
- Maintain the required privacy and cookie disclosures.
- Follow applicable advertising policies.
- Avoid intrusive placements that interfere with students accessing educational information.

---

# 11. Important Development Guidelines

All future StudySignal development must follow these principles:

1. Preserve existing working functionality.
2. Keep board-specific and examination-specific data separate.
3. Use official sources for factual educational information.
4. Never fabricate syllabus entries, examination dates or document links.
5. Never label model papers as PYQs.
6. Clearly identify resources awaiting official release.
7. Reuse existing templates and components where possible.
8. Maintain responsive mobile and desktop layouts.
9. Update automated tests whenever functionality changes.
10. Do not commit, push or deploy unless explicitly instructed.

StudySignal should remain scalable so additional Indian state boards and competitive examinations can be integrated without rebuilding the existing architecture.

---

# 12. Future Development Roadmap

Planned enhancements include:

- Unified Examination Calendar covering all supported boards and examinations.
- Additional Indian state education boards.
- More national and university entrance examinations.
- Personalized examination and academic updates.
- Examination countdowns and important-date reminders.
- Improved search and discovery.
- Additional verified official education resources.
- Performance and accessibility improvements.

These are development plans and should not be represented as already available features.

---

# 13. Official Portals & Source Links

## School Boards

| Authority | Official Website |
|---|---|
| CBSE | https://www.cbse.gov.in/ |
| CBSE Academic | https://cbseacademic.nic.in/ |
| UPMSP | https://upmsp.edu.in/ |
| CISCE | https://cisce.org/ |
| BSEB | https://biharboardonline.bihar.gov.in/ |
| MSBSHSE | https://mahahsscboard.in/ |

## Competitive Examinations

| Examination | Official Website |
|---|---|
| JEE Main | https://jeemain.nta.nic.in/ |
| JEE Advanced | https://jeeadv.ac.in/ |
| NEET UG | https://neet.nta.nic.in/ |
| CUET UG | https://cuet.nta.nic.in/ |
| National Testing Agency | https://nta.ac.in/ |

Official source URLs and document availability should be rechecked periodically.

---

# About StudySignal

StudySignal aims to make Indian education and examination information easier to discover, understand and access.

By bringing together multiple school boards and national entrance examinations, StudySignal provides students with a centralized starting point for finding official educational resources.

**StudySignal – One Platform. Multiple Boards. Multiple Examinations. Verified Information.**
