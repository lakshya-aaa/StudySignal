"""
StudySignal - Multi-Board Education Information Portal
Core Flask Application covering CBSE, CISCE (ICSE/ISC), UP Board (UPMSP),
Bihar Board (BSEB), and Maharashtra Board (MSBSHSE).
"""

import os
import json
from datetime import datetime
from flask import Flask, render_template, request, jsonify, abort, make_response, send_from_directory, redirect
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Data loader helpers
def load_json_data(filename):
    file_path = os.path.join(app.root_path, "data", filename)
    if not os.path.exists(file_path):
        return []
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_all_syllabus():
    return load_json_data("syllabus.json")

def get_all_pyqs():
    return load_json_data("pyq.json")

def get_datesheets():
    data = load_json_data("datesheets.json")
    if not getattr(Config, "SHOW_DEMO_DATA", True) and isinstance(data, dict) and "classes" in data:
        for cls_key in data["classes"]:
            data["classes"][cls_key]["schedule_items"] = []
            data["classes"][cls_key]["is_demo_schedule"] = False
    return data

def get_circulars():
    items = load_json_data("circulars.json")
    if not getattr(Config, "SHOW_DEMO_DATA", True):
        items = [c for c in items if not (c.get("is_demo") or c.get("verification_status") == "demo")]

    def sort_circular_key(c):
        # 1. Pinned notices first (if any)
        is_pinned = 1 if c.get("is_pinned") else 0
        # 2. Valid iso_date sorted descending (has_iso = 1 before 0)
        iso = c.get("iso_date") or ""
        has_iso = 1 if iso else 0
        # 3. For undated items, secondary sort on last_verified
        fallback_date = c.get("last_verified") or ""
        return (is_pinned, has_iso, iso, fallback_date)

    return sorted(items, key=sort_circular_key, reverse=True)

# ICSE & ISC data loader helpers
def get_all_icse_syllabus():
    return load_json_data("icse_syllabus.json")

def get_all_icse_pyqs():
    return load_json_data("icse_pyq.json")

def get_icse_datesheets():
    return load_json_data("icse_datesheets.json")

def get_icse_circulars():
    items = load_json_data("icse_circulars.json")
    def sort_circular_key(c):
        iso = c.get("iso_date") or ""
        fallback_date = c.get("last_verified") or ""
        return (iso, fallback_date)
    return sorted(items, key=sort_circular_key, reverse=True)

# UP Board (UPMSP) data loader helpers
def get_all_up_syllabus():
    return load_json_data("up_syllabus.json")

def get_up_datesheets():
    return load_json_data("up_datesheets.json")

def get_up_circulars():
    return load_json_data("up_circulars.json")

def get_all_up_sample_papers():
    return load_json_data("up_sample_papers.json")

def get_up_question_bank():
    return load_json_data("up_question_bank.json")

# Bihar Board (BSEB) data loader helpers
def get_bseb_syllabus():
    return load_json_data("bseb_syllabus.json")

def get_all_bseb_sample_papers():
    return load_json_data("bseb_sample_papers.json")

def get_bseb_datesheets():
    return load_json_data("bseb_datesheets.json")

def get_bseb_circulars():
    items = load_json_data("bseb_circulars.json")
    if not isinstance(items, list):
        return []
    def sort_circular_key(c):
        iso = c.get("iso_date") or ""
        fallback_date = c.get("last_verified") or ""
        return (iso, fallback_date)
    return sorted(items, key=sort_circular_key, reverse=True)

# Maharashtra Board (MSBSHSE) data loader helpers
def get_maha_syllabus():
    return load_json_data("maha_syllabus.json")

def get_all_maha_pyqs():
    return load_json_data("maha_pyq.json")

def get_maha_datesheets():
    return load_json_data("maha_datesheets.json")

def get_maha_question_bank():
    return load_json_data("maha_question_bank.json")

def get_maha_circulars():
    data = load_json_data("maha_circulars.json")
    if not isinstance(data, dict):
        return {"circulars": [], "publications": []}
    circs = data.get("circulars", [])
    pubs = data.get("publications", [])
    sorted_circs = sorted(
        circs,
        key=lambda c: (c.get("iso_date") or "", c.get("last_verified") or ""),
        reverse=True
    )
    return {"circulars": sorted_circs, "publications": pubs}

def get_boards_and_exams():
    """Directory of educational boards and competitive entrance exams on StudySignal."""
    return {
        "boards": [
            {
                "id": "cbse",
                "name": "CBSE",
                "full_name": "Central Board of Secondary Education",
                "scope": "National Board • Secondary & Senior Secondary",
                "status": "Active",
                "status_code": "active",
                "status_label": "Active",
                "url": "/cbse",
                "is_clickable": True,
                "badge_class": "badge-status-active",
                "description": "Comprehensive verified coverage for CBSE Class 10 and Class 12 curriculum, subject syllabi, official date sheets, circulars, and PYQ library (2014–2025).",
                "actions": [
                    {"label": "Class 10 Hub", "url": "/cbse/class-10"},
                    {"label": "Class 12 Hub", "url": "/cbse/class-12"},
                    {"label": "PYQ Library (2014-25)", "url": "/cbse/pyq"},
                    {"label": "Syllabus Directory", "url": "/cbse/syllabus"},
                    {"label": "Date Sheets", "url": "/cbse/datesheets"}
                ]
            },
            {
                "id": "icse",
                "name": "ICSE",
                "full_name": "Council for the Indian School Certificate Examinations (CISCE)",
                "scope": "National Board • ICSE (Class 10) & ISC (Class 12)",
                "status": "Active",
                "status_code": "active",
                "status_label": "Active",
                "url": "/icse",
                "is_clickable": True,
                "badge_class": "badge-status-active",
                "description": "Comprehensive verified coverage for ICSE (Class 10) and ISC (Class 12) curriculum, subject regulations, official examination datesheets, circulars, and PYQ library (2017–2027).",
                "actions": [
                    {"label": "Class 10 Hub", "url": "/icse/class-10"},
                    {"label": "Class 12 Hub", "url": "/icse/class-12"},
                    {"label": "PYQ Library (2017-27)", "url": "/icse/pyq"},
                    {"label": "Syllabus Directory", "url": "/icse/syllabus"},
                    {"label": "Date Sheets", "url": "/icse/datesheets"},
                    {"label": "Circulars & Notices", "url": "/icse/circulars"}
                ]
            },
            {
                "id": "up-board",
                "name": "UP Board",
                "full_name": "Uttar Pradesh Madhyamik Shiksha Parishad (UPMSP)",
                "scope": "State Board • High School (10th) & Intermediate (12th)",
                "status": "Active",
                "status_code": "active",
                "status_label": "Active",
                "url": "/up-board",
                "is_clickable": True,
                "badge_class": "badge-status-active",
                "description": "Comprehensive UP Board resources for High School (Class 10) and Intermediate (Class 12), including syllabus, official examination timetable, 23 verified sample papers, circulars and a dedicated Question Bank tracker.",
                "actions": [
                    {"label": "High School (Class 10) Hub", "url": "/up-board/class-10"},
                    {"label": "Intermediate (Class 12) Hub", "url": "/up-board/class-12"},
                    {"label": "Official Sample Papers (23)", "url": "/up-board/sample-papers"},
                    {"label": "Syllabus Directory", "url": "/up-board/syllabus"},
                    {"label": "Question Bank Tracker", "url": "/up-board/question-bank"},
                    {"label": "Examination Timetable", "url": "/up-board/datesheets"},
                    {"label": "Circulars & Notices", "url": "/up-board/circulars"}
                ]
            },
            {
                "id": "bseb",
                "name": "Bihar Board (BSEB)",
                "full_name": "Bihar School Examination Board",
                "scope": "State Board • Matric (10th) & Intermediate (12th)",
                "status": "Active",
                "status_code": "active",
                "status_label": "Active",
                "url": "/bihar-board",
                "is_clickable": True,
                "badge_class": "badge-status-active",
                "description": "Official Bihar Board resources for Matriculation (Class 10) and Intermediate (Class 12): consolidated syllabus PDFs & division regulations, 57 verified official 2026 Model Question Papers, 2027 timetable status tracker, circulars, and result & OFSS portals.",
                "actions": [
                    {"label": "Matric (Class 10) Hub", "url": "/bihar-board/class-10"},
                    {"label": "Intermediate (Class 12) Hub", "url": "/bihar-board/class-12"},
                    {"label": "Model Question Papers (57)", "url": "/bihar-board/sample-papers"},
                    {"label": "Syllabus & Regulations", "url": "/bihar-board/syllabus"},
                    {"label": "2027 Timetable Tracker", "url": "/bihar-board/datesheets"},
                    {"label": "Circulars & Directives", "url": "/bihar-board/circulars"},
                    {"label": "Results & Services", "url": "/bihar-board/results"}
                ]
            },
            {
                "id": "msbshse",
                "name": "Maharashtra Board (MSBSHSE)",
                "full_name": "Maharashtra State Board of Secondary and Higher Secondary Education",
                "scope": "State Board • SSC (10th) & HSC (12th)",
                "status": "Active",
                "status_code": "active",
                "status_label": "Active",
                "url": "/maharashtra-board",
                "is_clickable": True,
                "badge_class": "badge-status-active",
                "description": "Official Maharashtra Board portal covering SSC (Std. 10) & HSC (Std. 12) confirmed Feb–Mar 2027 timetables, 132 PYQ rows (332 official PDFs), 114 SSC & 132 HSC subject code catalogue, SCERT Prashnapedhi Question Banks, circulars, and guidance handbooks.",
                "actions": [
                    {"label": "SSC (Std. 10) Hub", "url": "/maharashtra-board/class-10"},
                    {"label": "HSC (Std. 12) Hub", "url": "/maharashtra-board/class-12"},
                    {"label": "Feb–Mar 2027 Timetable", "url": "/maharashtra-board/datesheets"},
                    {"label": "PYQ Library (332 PDFs)", "url": "/maharashtra-board/pyq"},
                    {"label": "Syllabus & Subject Codes", "url": "/maharashtra-board/syllabus"},
                    {"label": "SCERT Question Bank", "url": "/maharashtra-board/question-bank"},
                    {"label": "Circulars & Publications", "url": "/maharashtra-board/circulars"},
                    {"label": "Results & e-Marksheet", "url": "/maharashtra-board/results"}
                ]
            }
        ],
        "competitive_exams": [
            {
                "id": "jee",
                "name": "JEE",
                "full_name": "Joint Entrance Examination (Main & Advanced)",
                "scope": "National Engineering Entrance • NTA / IITs",
                "status": "Coming Soon",
                "status_code": "coming_soon",
                "status_label": "Coming Soon",
                "url": None,
                "is_clickable": False,
                "badge_class": "badge-status-soon",
                "description": "Official NTA information bulletin tracking, syllabus topic weightage, and entrance session updates in preparation.",
                "actions": []
            },
            {
                "id": "neet",
                "name": "NEET",
                "full_name": "National Eligibility cum Entrance Test (UG)",
                "scope": "National Medical Entrance • NTA",
                "status": "Coming Soon",
                "status_code": "coming_soon",
                "status_label": "Coming Soon",
                "url": None,
                "is_clickable": False,
                "badge_class": "badge-status-soon",
                "description": "Undergraduate medical entrance eligibility guidelines, official NMC/NTA curriculum outlines, and exam alerts planned.",
                "actions": []
            },
            {
                "id": "cuet",
                "name": "CUET",
                "full_name": "Common University Entrance Test (UG)",
                "scope": "Central & State University Admissions • NTA",
                "status": "Coming Soon",
                "status_code": "coming_soon",
                "status_label": "Coming Soon",
                "url": None,
                "is_clickable": False,
                "badge_class": "badge-status-soon",
                "description": "Undergraduate domain subjects and general test syllabus mapping scheduled for university entrance aspirants.",
                "actions": []
            }
        ]
    }

def get_public_base_url():
    """Return the canonical production origin, ensuring localhost/127.0.0.1 never leaks into public metadata."""
    base = Config.BASE_URL
    if not base or "127.0.0.1" in base or "localhost" in base:
        return getattr(Config, "PRODUCTION_BASE_URL", "https://exampulse-india.onrender.com").rstrip("/")
    return base.rstrip("/")

# Context processor for templates
@app.context_processor
def inject_globals():
    public_base = get_public_base_url()
    return {
        "site_name": Config.SITE_NAME,
        "site_tagline": Config.SITE_TAGLINE,
        "site_description": Config.SITE_DESCRIPTION,
        "base_url": Config.BASE_URL,
        "canonical_base_url": public_base,
        "production_base_url": getattr(Config, "PRODUCTION_BASE_URL", "https://exampulse-india.onrender.com"),
        "default_og_image": getattr(Config, "DEFAULT_OG_IMAGE", f"{public_base}/static/images/og-preview.png"),
        "default_og_image_alt": getattr(Config, "DEFAULT_OG_IMAGE_ALT", "StudySignal - Independent Educational Information Portal for CBSE Class 10 (Secondary) and Class 12 (Senior Secondary) Curriculum, Date Sheets, and Official Notices"),
        "disclaimer_text": Config.OFFICIAL_DISCLAIMER,
        "official_urls": Config.OFFICIAL_URLS,
        "current_academic_year": getattr(Config, "CURRENT_ACADEMIC_YEAR", "2026-27"),
        "show_demo_data": getattr(Config, "SHOW_DEMO_DATA", True),
        "ad_config": Config.ADS,
        "boards_and_exams": get_boards_and_exams(),
        "current_year": datetime.now().year,
        "today_str": datetime.now().strftime("%d %B %Y")
    }

# Trailing-slash normalization (Safe 301 Canonical Redirect)
@app.before_request
def normalize_trailing_slash():
    path = request.path
    if request.method in ("GET", "HEAD") and path != "/" and path.endswith("/"):
        clean_path = path.rstrip("/")
        if request.query_string:
            target = f"{clean_path}?{request.query_string.decode('utf-8')}"
        else:
            target = clean_path
        return redirect(target, code=301)

# ----------------- Core Routes -----------------

@app.route("/")
def index():
    # 1. CBSE Syllabus highlights
    cbse_items = [s for s in get_all_syllabus() if s.get("session_type", "current") == "current"]
    class_10_featured = [dict(s) for s in cbse_items if s.get("class") == "10"][:2]
    class_12_featured = [dict(s) for s in cbse_items if s.get("class") == "12"][:2]
    cbse_featured = class_10_featured + class_12_featured
    for s in cbse_featured:
        s["board"] = "CBSE"
        s["board_badge"] = "CBSE"
        s["board_key"] = "cbse"
        s["official_host"] = "cbseacademic.nic.in"
        s["detail_url"] = f"/cbse/syllabus/{s.get('id')}"

    # 2. UP Board Syllabus highlights
    up_all = get_all_up_syllabus()
    up_featured = [dict(s) for s in up_all if s.get("code") in ["901", "928", "151", "152"]][:4]
    for s in up_featured:
        s["board"] = "UP Board"
        s["board_badge"] = "UP Board"
        s["board_key"] = "up-board"
        s["official_host"] = "upmsp.edu.in"
        s["detail_url"] = "/up-board/syllabus"

    # 3. CISCE Syllabus highlights
    icse_all = get_all_icse_syllabus()
    icse_featured = [dict(s) for s in icse_all if s.get("code") in ["01", "51", "861", "862"]][:4]
    for s in icse_featured:
        s["board"] = "CISCE"
        s["board_badge"] = "CISCE"
        s["board_key"] = "cisce"
        s["official_host"] = "cisce.org"
        s["detail_url"] = f"/icse/syllabus/{s.get('id')}"

    # 4. Bihar Board (BSEB) Syllabus & Regulation highlights
    bseb_syl_data = get_bseb_syllabus()
    bseb_featured_raw = bseb_syl_data.get("featured_items", []) if isinstance(bseb_syl_data, dict) else []
    bseb_featured = [dict(s) for s in bseb_featured_raw][:4]
    for s in bseb_featured:
        s["board"] = "Bihar Board"
        s["board_badge"] = "Bihar Board"
        s["board_key"] = "bseb"
        s["official_host"] = "biharboardonline.com"
        s["detail_url"] = "/bihar-board/syllabus"

    # 5. Maharashtra Board (MSBSHSE) Syllabus & Framework highlights
    maha_syl_data = get_maha_syllabus()
    maha_featured_raw = maha_syl_data.get("featured_items", []) if isinstance(maha_syl_data, dict) else []
    maha_featured = [dict(s) for s in maha_featured_raw][:4]
    for s in maha_featured:
        s["board"] = "Maharashtra Board"
        s["board_badge"] = "Maharashtra Board"
        s["board_key"] = "msbshse"
        s["official_host"] = "books.ebalbharati.in" if "ebalbharati" in s.get("official_url", "") else "maa.ac.in / mahahsscboard.in"
        s["detail_url"] = "/maharashtra-board/syllabus"

    all_featured_syllabus = cbse_featured + up_featured + icse_featured + bseb_featured + maha_featured

    # 6. Circulars across supported boards
    cbse_circulars = [dict(c) for c in get_circulars()[:4]]
    for c in cbse_circulars:
        c["board"] = "CBSE"
        c["board_badge"] = "CBSE"
        c["board_key"] = "cbse"
        c["official_host"] = "cbseacademic.nic.in / cbse.gov.in"

    up_circulars = [dict(c) for c in get_up_circulars()[:3]]
    for c in up_circulars:
        c["board"] = "UP Board"
        c["board_badge"] = "UPMSP"
        c["board_key"] = "up-board"
        c["official_host"] = "upmsp.edu.in"

    icse_circulars = [dict(c) for c in get_icse_circulars()[:3]]
    for c in icse_circulars:
        c["board"] = "CISCE"
        c["board_badge"] = "CISCE"
        c["board_key"] = "cisce"
        c["official_host"] = "cisce.org"

    bseb_circulars = [dict(c) for c in get_bseb_circulars()[:3]]
    for c in bseb_circulars:
        c["board"] = "Bihar Board"
        c["board_badge"] = "BSEB"
        c["board_key"] = "bseb"
        c["official_host"] = "biharboardonline.com"

    maha_circ_bundle = get_maha_circulars()
    maha_circulars = [dict(c) for c in maha_circ_bundle.get("circulars", [])[:3]]
    for c in maha_circulars:
        c["board"] = "Maharashtra Board"
        c["board_badge"] = "MSBSHSE"
        c["board_key"] = "msbshse"
        c["official_host"] = "mahahsscboard.in"

    latest_circulars = cbse_circulars + up_circulars + icse_circulars + bseb_circulars + maha_circulars

    # 7. Date Sheets
    cbse_datesheets = get_datesheets()
    up_datesheets = get_up_datesheets()
    icse_datesheets = get_icse_datesheets()
    bseb_datesheets = get_bseb_datesheets()
    maha_datesheets = get_maha_datesheets()

    # 8. Boards Directory
    boards_and_exams = get_boards_and_exams()

    return render_template(
        "index.html",
        class_10_featured=class_10_featured,
        class_12_featured=class_12_featured,
        cbse_featured_syllabus=cbse_featured,
        up_featured_syllabus=up_featured,
        icse_featured_syllabus=icse_featured,
        bseb_featured_syllabus=bseb_featured,
        maha_featured_syllabus=maha_featured,
        all_featured_syllabus=all_featured_syllabus,
        latest_circulars=latest_circulars,
        cbse_circulars=cbse_circulars,
        up_circulars=up_circulars,
        icse_circulars=icse_circulars,
        bseb_circulars=bseb_circulars,
        maha_circulars=maha_circulars,
        datesheets=cbse_datesheets,
        up_datesheets=up_datesheets,
        icse_datesheets=icse_datesheets,
        bseb_datesheets=bseb_datesheets,
        maha_datesheets=maha_datesheets,
        boards_and_exams=boards_and_exams
    )

@app.route("/cbse")
def cbse_hub():
    """CBSE Board Examination Hub."""
    all_syllabus = get_all_syllabus()
    syllabus_items = [s for s in all_syllabus if s.get("session_type", "current") == "current"]
    datesheets = get_datesheets()
    circulars = get_circulars()
    featured_syllabus = syllabus_items[:6]
    latest_circulars = circulars[:4]
    return render_template(
        "cbse.html",
        featured_syllabus=featured_syllabus,
        latest_circulars=latest_circulars,
        datesheets=datesheets
    )

@app.route("/cbse/class-10")
def class_10():
    all_syllabus = get_all_syllabus()
    syllabus_items = [s for s in all_syllabus if s.get("class") == "10" and s.get("session_type", "current") == "current"]
    datesheets = get_datesheets().get("classes", {}).get("10", {})
    circulars = [c for c in get_circulars() if "10" in c.get("class_target", "") or "All" in c.get("class_target", "")]
    
    return render_template(
        "class_hub.html",
        class_num="10",
        class_title="CBSE Class 10 (Secondary)",
        syllabus_items=syllabus_items,
        datesheets=datesheets,
        circulars=circulars
    )

@app.route("/cbse/class-12")
def class_12():
    all_syllabus = get_all_syllabus()
    all_12 = [s for s in all_syllabus if s.get("class") == "12" and s.get("session_type", "current") == "current"]
    datesheets = get_datesheets().get("classes", {}).get("12", {})
    circulars = [c for c in get_circulars() if "12" in c.get("class_target", "") or "All" in c.get("class_target", "")]
    
    # Stream grouping
    science_subjects = [s for s in all_12 if "Science" in s.get("stream", "")]
    commerce_subjects = [s for s in all_12 if "Commerce" in s.get("stream", "")]
    arts_subjects = [s for s in all_12 if "Arts" in s.get("stream", "")]
    other_subjects = [s for s in all_12 if s not in science_subjects and s not in commerce_subjects and s not in arts_subjects]

    return render_template(
        "class_hub.html",
        class_num="12",
        class_title="CBSE Class 12 (Senior Secondary)",
        syllabus_items=all_12,
        science_subjects=science_subjects,
        commerce_subjects=commerce_subjects,
        arts_subjects=arts_subjects,
        other_subjects=other_subjects,
        datesheets=datesheets,
        circulars=circulars
    )

@app.route("/cbse/syllabus")
def syllabus_index():
    selected_class = request.args.get("class", "all")
    selected_stream = request.args.get("stream", "all")
    selected_year = request.args.get("year", "2026-27")
    search_q = request.args.get("q", "").strip().lower()

    items = get_all_syllabus()

    if selected_class != "all":
        items = [s for s in items if s.get("class") == selected_class]
    if selected_stream != "all":
        items = [s for s in items if selected_stream.lower() in s.get("stream", "").lower()]
    if selected_year != "all" and selected_year != "2026-27":
        items = [s for s in items if s.get("academic_year") == selected_year]
    if search_q:
        items = [
            s for s in items
            if search_q in s.get("subject", "").lower()
            or search_q in s.get("code", "").lower()
            or search_q in s.get("description", "").lower()
        ]

    return render_template(
        "syllabus.html",
        syllabus_items=items,
        selected_class=selected_class,
        selected_stream=selected_stream,
        selected_year=selected_year,
        search_q=search_q
    )

@app.route("/cbse/syllabus/<subject_id>")
def syllabus_detail(subject_id):
    items = get_all_syllabus()
    matched = next((s for s in items if s.get("id") == subject_id), None)
    if not matched:
        if not subject_id.endswith("-2027"):
            matched = next((s for s in items if s.get("id") == f"{subject_id}-2027"), None)
        elif subject_id.endswith("-2027"):
            matched = next((s for s in items if s.get("id") == subject_id.replace("-2027", "")), None)
    if not matched:
        abort(404)
    
    # Related subjects in same class
    related = [s for s in items if s.get("class") == matched.get("class") and s.get("id") != matched.get("id")][:4]

    return render_template(
        "syllabus_detail.html",
        item=matched,
        related=related
    )

@app.route("/cbse/datesheets")
def datesheets_view():
    data = get_datesheets()
    selected_class = request.args.get("class", "all")
    return render_template(
        "datesheets.html",
        data=data,
        selected_class=selected_class
    )

@app.route("/cbse/circulars")
def circulars_view():
    all_circulars = get_circulars()
    category = request.args.get("category", "all")
    selected_class = request.args.get("class", "all")
    search_q = request.args.get("q", "").strip().lower()

    filtered = all_circulars
    if category != "all":
        filtered = [c for c in filtered if c.get("category", "").lower() == category.lower()]
    if selected_class != "all":
        filtered = [c for c in filtered if selected_class in c.get("class_target", "") or "All" in c.get("class_target", "")]
    if search_q:
        filtered = [
            c for c in filtered
            if search_q in c.get("title", "").lower()
            or search_q in c.get("summary", "").lower()
            or search_q in c.get("circular_no", "").lower()
        ]

    return render_template(
        "circulars.html",
        circulars=filtered,
        category=category,
        selected_class=selected_class,
        search_q=search_q
    )

@app.route("/cbse/pyq")
def pyq_index():
    all_papers = get_all_pyqs()
    selected_class = request.args.get("class", "all").strip()
    selected_subject = request.args.get("subject", "all").strip()
    selected_year = request.args.get("year", "all").strip()
    selected_availability = request.args.get("availability", "all").strip()
    search_q = request.args.get("q", "").strip().lower()

    # Dynamic options for filter dropdowns
    available_years = sorted(list(set(p.get("exam_year", "") for p in all_papers if p.get("exam_year"))), reverse=True)
    available_subjects = sorted(list(set(p.get("subject", "") for p in all_papers if p.get("subject"))))

    filtered = all_papers

    if selected_class != "all":
        filtered = [p for p in filtered if str(p.get("class")) == selected_class]
    if selected_subject != "all":
        filtered = [p for p in filtered if p.get("subject", "").lower() == selected_subject.lower()]
    if selected_year != "all":
        filtered = [p for p in filtered if str(p.get("exam_year")) == selected_year]
    if selected_availability == "available":
        filtered = [p for p in filtered if p.get("is_available") is True]
    elif selected_availability == "unavailable":
        filtered = [p for p in filtered if not p.get("is_available")]
    if search_q:
        filtered = [
            p for p in filtered
            if search_q in p.get("subject", "").lower()
            or search_q in p.get("code", "").lower()
            or search_q in p.get("title", "").lower()
            or search_q in p.get("description", "").lower()
        ]

    # Sort papers by exam_year desc, then class asc, then subject asc
    def sort_pyq_key(p):
        year = p.get("exam_year", "0")
        cls = p.get("class", "0")
        subj = p.get("subject", "")
        return (year, cls, subj)

    filtered_sorted = sorted(filtered, key=sort_pyq_key, reverse=True)

    return render_template(
        "pyq.html",
        pyq_items=filtered_sorted,
        selected_class=selected_class,
        selected_subject=selected_subject,
        selected_year=selected_year,
        selected_availability=selected_availability,
        search_q=search_q,
        available_years=available_years,
        available_subjects=available_subjects,
        total_count=len(all_papers)
    )

@app.route("/pyq")
def pyq_redirect():
    target = "/cbse/pyq"
    if request.query_string:
        target += f"?{request.query_string.decode('utf-8')}"
    return redirect(target, code=301)

@app.route("/boards")
def boards_hub():
    """Directory and status overview of all educational boards and competitive entrance exams."""
    directory = get_boards_and_exams()
    return render_template(
        "boards.html",
        boards=directory["boards"],
        competitive_exams=directory["competitive_exams"]
    )

# ----------------- ICSE & ISC Routes -----------------

@app.route("/icse")
def icse_hub():
    """ICSE & ISC Board Examination Hub."""
    syllabus_items = get_all_icse_syllabus()
    datesheets = get_icse_datesheets()
    circulars = get_icse_circulars()
    featured_syllabus = syllabus_items[:6]
    latest_circulars = circulars[:4]
    return render_template(
        "icse.html",
        featured_syllabus=featured_syllabus,
        latest_circulars=latest_circulars,
        datesheets=datesheets
    )

@app.route("/icse/class-10")
def icse_class_10():
    all_syllabus = get_all_icse_syllabus()
    syllabus_items = [s for s in all_syllabus if s.get("class") == "10"]
    datesheets = get_icse_datesheets().get("classes", {}).get("10", {})
    circulars = [c for c in get_icse_circulars() if "10" in c.get("class_target", "") or "All" in c.get("class_target", "")]
    return render_template(
        "icse_class_hub.html",
        class_num="10",
        course_name="ICSE",
        class_title="ICSE Class 10 (Secondary)",
        official_portal_url="https://cisce.org/regulations-and-syllabuses/",
        syllabus_items=syllabus_items,
        datesheets=datesheets,
        circulars=circulars
    )

@app.route("/icse/class-12")
def icse_class_12():
    all_syllabus = get_all_icse_syllabus()
    all_12 = [s for s in all_syllabus if s.get("class") == "12"]
    datesheets = get_icse_datesheets().get("classes", {}).get("12", {})
    circulars = [c for c in get_icse_circulars() if "12" in c.get("class_target", "") or "All" in c.get("class_target", "")]
    science_subjects = [s for s in all_12 if "Science" in s.get("stream", "")]
    commerce_subjects = [s for s in all_12 if "Commerce" in s.get("stream", "")]
    arts_subjects = [s for s in all_12 if "Arts" in s.get("stream", "")]
    other_subjects = [s for s in all_12 if s not in science_subjects and s not in commerce_subjects and s not in arts_subjects]
    return render_template(
        "icse_class_hub.html",
        class_num="12",
        course_name="ISC",
        class_title="ISC Class 12 (Higher Secondary)",
        official_portal_url="https://cisce.org/regulations-and-syllabuses-isc/",
        syllabus_items=all_12,
        science_subjects=science_subjects,
        commerce_subjects=commerce_subjects,
        arts_subjects=arts_subjects,
        other_subjects=other_subjects,
        datesheets=datesheets,
        circulars=circulars
    )

@app.route("/icse/syllabus")
def icse_syllabus_index():
    selected_class = request.args.get("class", "all")
    selected_stream = request.args.get("stream", "all")
    search_q = request.args.get("q", "").strip().lower()

    items = get_all_icse_syllabus()
    if selected_class != "all":
        items = [s for s in items if s.get("class") == selected_class]
    if selected_stream != "all":
        items = [s for s in items if selected_stream.lower() in s.get("stream", "").lower()]
    if search_q:
        items = [
            s for s in items
            if search_q in s.get("subject", "").lower()
            or search_q in s.get("code", "").lower()
            or search_q in s.get("description", "").lower()
        ]
    return render_template(
        "icse_syllabus.html",
        syllabus_items=items,
        selected_class=selected_class,
        selected_stream=selected_stream,
        selected_year="2026-27",
        search_q=search_q,
        is_isc_view=False
    )

@app.route("/isc/syllabus")
def isc_syllabus_index():
    selected_stream = request.args.get("stream", "all")
    search_q = request.args.get("q", "").strip().lower()

    items = [s for s in get_all_icse_syllabus() if s.get("class") == "12"]
    if selected_stream != "all":
        items = [s for s in items if selected_stream.lower() in s.get("stream", "").lower()]
    if search_q:
        items = [
            s for s in items
            if search_q in s.get("subject", "").lower()
            or search_q in s.get("code", "").lower()
            or search_q in s.get("description", "").lower()
        ]
    return render_template(
        "icse_syllabus.html",
        syllabus_items=items,
        selected_class="12",
        selected_stream=selected_stream,
        selected_year="2026-27",
        search_q=search_q,
        is_isc_view=True
    )

@app.route("/icse/syllabus/<subject_id>")
def icse_syllabus_detail(subject_id):
    items = get_all_icse_syllabus()
    matched = next((s for s in items if s.get("id") == subject_id), None)
    if not matched:
        if not subject_id.endswith("-2027"):
            matched = next((s for s in items if s.get("id") == f"{subject_id}-2027"), None)
        elif subject_id.endswith("-2027"):
            matched = next((s for s in items if s.get("id") == subject_id.replace("-2027", "")), None)
    if not matched:
        abort(404)
    related = [s for s in items if s.get("class") == matched.get("class") and s.get("id") != matched.get("id")][:4]
    return render_template(
        "icse_subject_detail.html",
        item=matched,
        related=related
    )

@app.route("/icse/datesheets")
def icse_datesheets_view():
    data = get_icse_datesheets()
    selected_class = request.args.get("class", "all")
    return render_template(
        "icse_datesheets.html",
        data=data,
        selected_class=selected_class
    )

@app.route("/icse/circulars")
def icse_circulars_view():
    all_circulars = get_icse_circulars()
    category = request.args.get("category", "all")
    selected_class = request.args.get("class", "all")
    search_q = request.args.get("q", "").strip().lower()

    filtered = all_circulars
    if category != "all":
        filtered = [c for c in filtered if c.get("category", "").lower() == category.lower()]
    if selected_class != "all":
        filtered = [c for c in filtered if selected_class in c.get("class_target", "") or "All" in c.get("class_target", "")]
    if search_q:
        filtered = [
            c for c in filtered
            if search_q in c.get("title", "").lower()
            or search_q in c.get("summary", "").lower()
            or search_q in c.get("circular_no", "").lower()
        ]
    return render_template(
        "icse_circulars.html",
        circulars=filtered,
        category=category,
        selected_class=selected_class,
        search_q=search_q
    )

@app.route("/icse/pyq")
def icse_pyq_index():
    all_papers = get_all_icse_pyqs()
    selected_class = request.args.get("class", "all").strip()
    selected_subject = request.args.get("subject", "all").strip()
    selected_year = request.args.get("year", "all").strip()
    selected_availability = request.args.get("availability", "all").strip()
    search_q = request.args.get("q", "").strip().lower()

    available_years = sorted(list(set(p.get("exam_year", "") for p in all_papers if p.get("exam_year"))), reverse=True)
    available_subjects = sorted(list(set(p.get("subject", "") for p in all_papers if p.get("subject"))))

    filtered = all_papers
    if selected_class != "all":
        filtered = [p for p in filtered if str(p.get("class")) == selected_class]
    if selected_subject != "all":
        filtered = [p for p in filtered if p.get("subject", "").lower() == selected_subject.lower()]
    if selected_year != "all":
        filtered = [p for p in filtered if str(p.get("exam_year")) == selected_year]
    if selected_availability == "available":
        filtered = [p for p in filtered if p.get("is_available") is True]
    elif selected_availability == "unavailable":
        filtered = [p for p in filtered if not p.get("is_available")]
    if search_q:
        filtered = [
            p for p in filtered
            if search_q in p.get("subject", "").lower()
            or search_q in p.get("code", "").lower()
            or search_q in p.get("title", "").lower()
            or search_q in p.get("description", "").lower()
        ]

    def sort_pyq_key(p):
        year = p.get("exam_year", "0")
        cls = p.get("class", "0")
        subj = p.get("subject", "")
        return (year, cls, subj)

    filtered_sorted = sorted(filtered, key=sort_pyq_key, reverse=True)

    return render_template(
        "icse_pyq.html",
        pyq_items=filtered_sorted,
        selected_class=selected_class,
        selected_subject=selected_subject,
        selected_year=selected_year,
        selected_availability=selected_availability,
        search_q=search_q,
        available_years=available_years,
        available_subjects=available_subjects,
        total_count=len(all_papers)
    )

# ----------------- UP Board (UPMSP) Routes -----------------

@app.route("/up-board")
def up_board_hub():
    """UP Board (UPMSP) Examination Hub - Active."""
    datesheets = get_up_datesheets()
    all_syllabus = get_all_up_syllabus()
    all_circulars = get_up_circulars()
    all_sample_papers = get_all_up_sample_papers()
    question_bank = get_up_question_bank()
    return render_template(
        "upmsp.html",
        datesheets=datesheets,
        featured_syllabus=all_syllabus[:6],
        latest_circulars=all_circulars[:4],
        featured_sample_papers=all_sample_papers[:6],
        question_bank=question_bank
    )

@app.route("/up-board/class-10")
def up_board_class_10():
    """UP Board High School (Class 10) Hub."""
    datesheets = get_up_datesheets().get("classes", {}).get("10", {})
    all_syllabus = [s for s in get_all_up_syllabus() if s.get("class") == "10"]
    circulars = [c for c in get_up_circulars() if "10" in c.get("class_target", "") or "All" in c.get("class_target", "")]
    sample_papers = [p for p in get_all_up_sample_papers() if p.get("class") == "10"]
    question_bank_class = get_up_question_bank().get("classes", {}).get("10", {})
    return render_template(
        "upmsp_class_hub.html",
        class_num="10",
        course_name="High School",
        course_name_hindi="हाई स्कूल",
        class_title="UP Board High School (Class 10)",
        class_title_hindi="उत्तर प्रदेश माध्यमिक शिक्षा परिषद् - हाईस्कूल (कक्षा 10)",
        datesheets=datesheets,
        syllabus_items=all_syllabus,
        circulars=circulars,
        sample_papers=sample_papers,
        question_bank=question_bank_class
    )

@app.route("/up-board/class-12")
def up_board_class_12():
    """UP Board Intermediate (Class 12) Hub."""
    datesheets = get_up_datesheets().get("classes", {}).get("12", {})
    all_syllabus = [s for s in get_all_up_syllabus() if s.get("class") == "12"]
    circulars = [c for c in get_up_circulars() if "12" in c.get("class_target", "") or "All" in c.get("class_target", "")]
    sample_papers = [p for p in get_all_up_sample_papers() if p.get("class") == "12"]
    question_bank_class = get_up_question_bank().get("classes", {}).get("12", {})
    return render_template(
        "upmsp_class_hub.html",
        class_num="12",
        course_name="Intermediate",
        course_name_hindi="इण्टरमीडिएट",
        class_title="UP Board Intermediate (Class 12)",
        class_title_hindi="उत्तर प्रदेश माध्यमिक शिक्षा परिषद् - इण्टरमीडिएट (कक्षा 12)",
        datesheets=datesheets,
        syllabus_items=all_syllabus,
        circulars=circulars,
        sample_papers=sample_papers,
        question_bank=question_bank_class
    )

@app.route("/up-board/datesheets")
def up_board_datesheets_view():
    """UP Board Examination Schedule & Timetable Status."""
    datesheets = get_up_datesheets()
    selected_class = request.args.get("class", "all")
    return render_template(
        "upmsp_datesheets.html",
        datesheets=datesheets,
        selected_class=selected_class
    )

@app.route("/up-board/syllabus")
def up_board_syllabus_index():
    """UP Board Subject Syllabus Directory."""
    selected_class = request.args.get("class", "all")
    search_q = request.args.get("q", "").strip().lower()
    items = get_all_up_syllabus()
    if selected_class != "all":
        items = [s for s in items if s.get("class") == selected_class]
    if search_q:
        items = [s for s in items if search_q in s.get("subject", "").lower() or search_q in s.get("code", "").lower()]
    return render_template(
        "upmsp_syllabus.html",
        syllabus_items=items,
        selected_class=selected_class,
        search_q=search_q
    )

@app.route("/up-board/circulars")
def up_board_circulars_view():
    """UP Board Official Circulars & Notices."""
    selected_class = request.args.get("class", "all")
    circulars = get_up_circulars()
    if selected_class != "all":
        circulars = [c for c in circulars if selected_class in c.get("class_target", "") or "All" in c.get("class_target", "")]
    return render_template(
        "upmsp_circulars.html",
        circulars=circulars,
        selected_class=selected_class
    )

@app.route("/up-board/sample-papers")
@app.route("/up-board/model-papers")
def up_board_sample_papers_index():
    """UP Board Official Sample Papers / Model Papers Directory."""
    selected_class = request.args.get("class", "all")
    search_q = request.args.get("q", "").strip().lower()
    items = get_all_up_sample_papers()
    if selected_class != "all":
        items = [p for p in items if p.get("class") == selected_class]
    if search_q:
        items = [
            p for p in items
            if search_q in p.get("subject", "").lower()
            or search_q in p.get("code", "").lower()
            or search_q in p.get("title", "").lower()
        ]
    return render_template(
        "upmsp_sample_papers.html",
        sample_papers=items,
        selected_class=selected_class,
        search_q=search_q
    )

@app.route("/up-board/question-bank")
def up_board_question_bank_view():
    """UP Board Official Question Bank Directory & Status Tracker."""
    qb_data = get_up_question_bank()
    return render_template(
        "upmsp_question_bank.html",
        question_bank=qb_data
    )

# ----------------- Bihar Board (BSEB) Routes -----------------
# Note: /bihar-board/pyq MUST NOT exist (returns 404).

@app.route("/bihar-board")
def bseb_hub():
    """Bihar Board (BSEB) Examination Hub."""
    datesheets = get_bseb_datesheets()
    syllabus_data = get_bseb_syllabus()
    all_papers = get_all_bseb_sample_papers()
    all_circulars = get_bseb_circulars()

    featured_codes = ["101", "110", "112", "117", "118", "220"]
    featured_sample_papers = [p for p in all_papers if str(p.get("code")) in featured_codes][:6]
    if len(featured_sample_papers) < 6:
        featured_sample_papers = all_papers[:6]

    return render_template(
        "bseb.html",
        datesheets=datesheets,
        syllabus_data=syllabus_data,
        featured_sample_papers=featured_sample_papers,
        total_model_papers=len(all_papers),
        latest_circulars=all_circulars[:5]
    )

@app.route("/bihar-board/class-10")
def bseb_class_10():
    """Bihar Board Matriculation (Class 10) Hub."""
    datesheets = get_bseb_datesheets()
    class_ds = datesheets.get("classes", {}).get("10", {}) if isinstance(datesheets, dict) else {}
    syllabus_data = get_bseb_syllabus()
    pdfs_raw = syllabus_data.get("official_pdfs", []) if isinstance(syllabus_data, dict) else []
    syllabus_pdfs = [p for p in pdfs_raw if p.get("class") in ("10", "9")]
    curriculum_struct = syllabus_data.get("curriculum_structure", {}).get("10", {}) if isinstance(syllabus_data, dict) else {}
    sample_papers = [p for p in get_all_bseb_sample_papers() if str(p.get("class")) == "10"]
    circulars = [c for c in get_bseb_circulars() if "10" in c.get("class_target", "") or "All" in c.get("class_target", "")]

    return render_template(
        "bseb_class_hub.html",
        class_num="10",
        course_name="Matriculation",
        course_name_hindi="मैट्रिक (कक्षा 10)",
        class_title="Bihar Board Class 10 (Matriculation)",
        class_title_hindi="बिहार विद्यालय परीक्षा समिति (BSEB) - वार्षिक माध्यमिक परीक्षा (कक्षा 10)",
        datesheets=datesheets,
        class_ds=class_ds,
        syllabus_pdfs=syllabus_pdfs,
        curriculum_struct=curriculum_struct,
        sample_papers=sample_papers,
        circulars=circulars
    )

@app.route("/bihar-board/class-12")
def bseb_class_12():
    """Bihar Board Intermediate (+2 Class 12) Hub."""
    datesheets = get_bseb_datesheets()
    class_ds = datesheets.get("classes", {}).get("12", {}) if isinstance(datesheets, dict) else {}
    syllabus_data = get_bseb_syllabus()
    pdfs_raw = syllabus_data.get("official_pdfs", []) if isinstance(syllabus_data, dict) else []
    syllabus_pdfs = [p for p in pdfs_raw if p.get("class") == "12"]
    curriculum_struct = syllabus_data.get("curriculum_structure", {}).get("12", {}) if isinstance(syllabus_data, dict) else {}
    sample_papers = [p for p in get_all_bseb_sample_papers() if str(p.get("class")) == "12"]
    circulars = [c for c in get_bseb_circulars() if "12" in c.get("class_target", "") or "All" in c.get("class_target", "")]

    return render_template(
        "bseb_class_hub.html",
        class_num="12",
        course_name="Intermediate",
        course_name_hindi="इण्टरमीडिएट (+2 कक्षा 12)",
        class_title="Bihar Board Class 12 (Intermediate +2)",
        class_title_hindi="बिहार विद्यालय परीक्षा समिति (BSEB) - इण्टरमीडिएट परीक्षा (कक्षा 12)",
        datesheets=datesheets,
        class_ds=class_ds,
        syllabus_pdfs=syllabus_pdfs,
        curriculum_struct=curriculum_struct,
        sample_papers=sample_papers,
        circulars=circulars
    )

@app.route("/bihar-board/syllabus")
def bseb_syllabus_index():
    """Bihar Board Consolidated Syllabus PDFs & Passing Regulations."""
    selected_class = request.args.get("class", "all").strip()
    syllabus_data = get_bseb_syllabus()
    official_pdfs = syllabus_data.get("official_pdfs", []) if isinstance(syllabus_data, dict) else []
    curriculum_structure = syllabus_data.get("curriculum_structure", {}) if isinstance(syllabus_data, dict) else {}

    if selected_class != "all":
        filtered_pdfs = [p for p in official_pdfs if str(p.get("class")) == selected_class]
    else:
        filtered_pdfs = official_pdfs

    return render_template(
        "bseb_syllabus.html",
        syllabus_data=syllabus_data,
        official_pdfs=filtered_pdfs,
        all_pdfs_count=len(official_pdfs),
        curriculum_structure=curriculum_structure,
        selected_class=selected_class
    )

@app.route("/bihar-board/sample-papers")
@app.route("/bihar-board/model-papers")
def bseb_sample_papers_index():
    """Bihar Board Official 2026 Model Question Papers (57 Verified Papers — Sample Pattern Only, Not PYQs)."""
    selected_class = request.args.get("class", "all").strip()
    selected_stream = request.args.get("stream", "all").strip()
    search_q = request.args.get("q", "").strip().lower()

    all_papers = get_all_bseb_sample_papers()
    available_streams = sorted(list(set(p.get("stream", "") for p in all_papers if p.get("stream"))))

    filtered = all_papers
    if selected_class != "all":
        filtered = [p for p in filtered if str(p.get("class")) == selected_class]
    if selected_stream != "all":
        filtered = [p for p in filtered if selected_stream.lower() in p.get("stream", "").lower()]
    if search_q:
        filtered = [
            p for p in filtered
            if search_q in p.get("subject", "").lower()
            or search_q in p.get("code", "").lower()
            or search_q in p.get("raw_label", "").lower()
            or search_q in p.get("title", "").lower()
            or search_q in p.get("stream", "").lower()
        ]

    return render_template(
        "bseb_sample_papers.html",
        sample_papers=filtered,
        total_count=len(all_papers),
        selected_class=selected_class,
        selected_stream=selected_stream,
        available_streams=available_streams,
        search_q=search_q
    )

@app.route("/bihar-board/question-bank")
def bseb_question_bank_view():
    """Bihar Board Question Bank Availability Tracker (Transparently Not Provided on Official BSEB Portal)."""
    return render_template(
        "bseb_question_bank.html",
        total_model_papers=len(get_all_bseb_sample_papers())
    )

@app.route("/bihar-board/date-sheet")
@app.route("/bihar-board/datesheets")
def bseb_datesheets_view():
    """Bihar Board 2027 Examination Timetable Status & Verified 2026 Reference Programmes."""
    datesheets = get_bseb_datesheets()
    selected_class = request.args.get("class", "all").strip()
    return render_template(
        "bseb_datesheets.html",
        datesheets=datesheets,
        selected_class=selected_class
    )

@app.route("/bihar-board/circulars")
def bseb_circulars_view():
    """Bihar Board Official Circulars, Directives & Top 20 Percentile Scholarship Notices."""
    all_circulars = get_bseb_circulars()
    category = request.args.get("category", "all").strip()
    selected_class = request.args.get("class", "all").strip()
    search_q = request.args.get("q", "").strip().lower()

    available_categories = sorted(list(set(c.get("category", "") for c in all_circulars if c.get("category"))))

    filtered = all_circulars
    if category != "all":
        filtered = [c for c in filtered if c.get("category", "").lower() == category.lower()]
    if selected_class != "all":
        filtered = [c for c in filtered if selected_class in c.get("class_target", "") or "All" in c.get("class_target", "")]
    if search_q:
        filtered = [
            c for c in filtered
            if search_q in c.get("title", "").lower()
            or search_q in c.get("summary", "").lower()
            or search_q in c.get("circular_no", "").lower()
        ]

    return render_template(
        "bseb_circulars.html",
        circulars=filtered,
        total_count=len(all_circulars),
        available_categories=available_categories,
        category=category,
        selected_class=selected_class,
        search_q=search_q
    )

@app.route("/bihar-board/results")
def bseb_results_view():
    """Bihar Board Official Results, Scholarship Top 20% Cut-off Lists & OFSS Admissions Portal Directory."""
    all_circulars = get_bseb_circulars()
    scholarship_circulars = [c for c in all_circulars if c.get("category") == "Scholarships & Results"]
    service_circulars = [c for c in all_circulars if c.get("category") == "Student Services"]
    return render_template(
        "bseb_results.html",
        scholarship_circulars=scholarship_circulars,
        service_circulars=service_circulars
    )

# ----------------- Maharashtra Board (MSBSHSE) Routes -----------------

def _normalize_maha_class(cls_val):
    val = (cls_val or "all").strip().lower()
    if val in ("10", "ssc"):
        return "10"
    if val in ("12", "hsc"):
        return "12"
    return "all"

@app.route("/maharashtra-board")
def maha_hub():
    """Maharashtra Board (MSBSHSE) Examination Hub."""
    datesheets = get_maha_datesheets()
    syllabus_data = get_maha_syllabus()
    pyqs = get_all_maha_pyqs()
    pyq_total_pdfs = sum(len(p.get("pdfs", [])) for p in pyqs)
    qbank_data = get_maha_question_bank()
    circ_bundle = get_maha_circulars()
    latest_circulars = circ_bundle.get("circulars", [])[:5]
    publications = circ_bundle.get("publications", [])[:4]

    return render_template(
        "maha.html",
        datesheets=datesheets,
        syllabus_data=syllabus_data,
        pyq_total_rows=len(pyqs),
        pyq_total_pdfs=pyq_total_pdfs,
        qbank_data=qbank_data,
        latest_circulars=latest_circulars,
        publications=publications
    )

@app.route("/maharashtra-board/class-10")
def maha_class_10():
    """Maharashtra Board SSC (Std. 10) Hub."""
    datesheets = get_maha_datesheets()
    class_ds = datesheets.get("classes", {}).get("10", {}) if isinstance(datesheets, dict) else {}
    syllabus_data = get_maha_syllabus()
    subjects = syllabus_data.get("ssc_subjects", []) if isinstance(syllabus_data, dict) else []
    frameworks = syllabus_data.get("curriculum_frameworks", []) if isinstance(syllabus_data, dict) else []
    pyqs = [p for p in get_all_maha_pyqs() if str(p.get("class")) == "10"]
    pyq_pdf_count = sum(len(p.get("pdfs", [])) for p in pyqs)
    qbank_data = get_maha_question_bank()
    qbank_items = qbank_data.get("classes", {}).get("10", {}).get("items", []) if isinstance(qbank_data, dict) else []
    drive_folders = qbank_data.get("drive_folders_2024_25", []) if isinstance(qbank_data, dict) else []
    circ_bundle = get_maha_circulars()
    circulars = [c for c in circ_bundle.get("circulars", []) if "10" in c.get("class_target", "") or "SSC" in c.get("class_target", "")]
    publications = [p for p in circ_bundle.get("publications", []) if "10" in p.get("class_target", "") or "SSC" in p.get("class_target", "")]

    return render_template(
        "maha_class_hub.html",
        class_num="10",
        course_name="SSC",
        course_name_mr="माध्यमिक शालान्त प्रमाणपत्र परीक्षा (इयत्ता १० वी)",
        class_title="Maharashtra Board SSC (Std. 10)",
        class_title_mr="महाराष्ट्र राज्य माध्यमिक व उच्च माध्यमिक शिक्षण मंडळ - SSC (Std. 10)",
        datesheets=datesheets,
        class_ds=class_ds,
        subjects=subjects,
        curriculum_frameworks=frameworks,
        syllabus_note=syllabus_data.get("metadata", {}).get("transparency_note", "") if isinstance(syllabus_data, dict) else "",
        pyq_rows=pyqs,
        pyq_pdf_count=pyq_pdf_count,
        qbank_items=qbank_items,
        drive_folders=drive_folders,
        circulars=circulars,
        publications=publications
    )

@app.route("/maharashtra-board/class-12")
def maha_class_12():
    """Maharashtra Board HSC (Std. 12) Hub."""
    datesheets = get_maha_datesheets()
    class_ds = datesheets.get("classes", {}).get("12", {}) if isinstance(datesheets, dict) else {}
    syllabus_data = get_maha_syllabus()
    subjects = syllabus_data.get("hsc_subjects", []) if isinstance(syllabus_data, dict) else []
    frameworks = syllabus_data.get("curriculum_frameworks", []) if isinstance(syllabus_data, dict) else []
    pyqs = [p for p in get_all_maha_pyqs() if str(p.get("class")) == "12"]
    pyq_pdf_count = sum(len(p.get("pdfs", [])) for p in pyqs)
    qbank_data = get_maha_question_bank()
    qbank_items = qbank_data.get("classes", {}).get("12", {}).get("items", []) if isinstance(qbank_data, dict) else []
    drive_folders = qbank_data.get("drive_folders_2024_25", []) if isinstance(qbank_data, dict) else []
    circ_bundle = get_maha_circulars()
    circulars = [c for c in circ_bundle.get("circulars", []) if "12" in c.get("class_target", "") or "HSC" in c.get("class_target", "")]
    publications = [p for p in circ_bundle.get("publications", []) if "12" in p.get("class_target", "") or "HSC" in p.get("class_target", "")]

    return render_template(
        "maha_class_hub.html",
        class_num="12",
        course_name="HSC",
        course_name_mr="उच्च माध्यमिक प्रमाणपत्र परीक्षा (इयत्ता १२ वी)",
        class_title="Maharashtra Board HSC (Std. 12)",
        class_title_mr="महाराष्ट्र राज्य माध्यमिक व उच्च माध्यमिक शिक्षण मंडळ - HSC (Std. 12)",
        datesheets=datesheets,
        class_ds=class_ds,
        subjects=subjects,
        curriculum_frameworks=frameworks,
        syllabus_note=syllabus_data.get("metadata", {}).get("transparency_note", "") if isinstance(syllabus_data, dict) else "",
        pyq_rows=pyqs,
        pyq_pdf_count=pyq_pdf_count,
        qbank_items=qbank_items,
        drive_folders=drive_folders,
        circulars=circulars,
        publications=publications
    )

@app.route("/maharashtra-board/syllabus")
def maha_syllabus_index():
    """Maharashtra Board Syllabus & Official Subject Code Catalogue (SSC 114 + HSC 132 + SCERT Frameworks)."""
    selected_class = _normalize_maha_class(request.args.get("class", "all"))
    selected_category = request.args.get("category", "all").strip()
    search_q = request.args.get("q", "").strip().lower()

    syllabus_data = get_maha_syllabus()
    frameworks = syllabus_data.get("curriculum_frameworks", []) if isinstance(syllabus_data, dict) else []
    ssc_all = syllabus_data.get("ssc_subjects", []) if isinstance(syllabus_data, dict) else []
    hsc_all = syllabus_data.get("hsc_subjects", []) if isinstance(syllabus_data, dict) else []

    ssc_categories = sorted(list(set(s.get("category", "") for s in ssc_all if s.get("category"))))
    hsc_categories = sorted(list(set(s.get("category", "") for s in hsc_all if s.get("category"))))
    all_categories = sorted(list(set(ssc_categories + hsc_categories)))

    def filter_subjects(subj_list):
        out = subj_list
        if selected_category != "all":
            out = [s for s in out if s.get("category", "").lower() == selected_category.lower()]
        if search_q:
            out = [
                s for s in out
                if search_q in s.get("subject", "").lower()
                or search_q in s.get("subject_mr", "").lower()
                or search_q in str(s.get("code", "")).lower()
                or search_q in s.get("category", "").lower()
            ]
        return out

    ssc_subjects = filter_subjects(ssc_all) if selected_class in ("all", "10") else []
    hsc_subjects = filter_subjects(hsc_all) if selected_class in ("all", "12") else []

    return render_template(
        "maha_syllabus.html",
        metadata=syllabus_data.get("metadata", {}) if isinstance(syllabus_data, dict) else {},
        curriculum_frameworks=frameworks,
        ssc_subjects=ssc_subjects,
        hsc_subjects=hsc_subjects,
        ssc_total=len(ssc_all),
        hsc_total=len(hsc_all),
        available_categories=all_categories,
        selected_class=selected_class,
        selected_category=selected_category,
        search_q=search_q
    )

@app.route("/maharashtra-board/pyq")
def maha_pyq_index():
    """Maharashtra Board Official Past Board Question Papers (132 Rows / 332 Medium PDFs)."""
    all_rows = get_all_maha_pyqs()
    selected_class = _normalize_maha_class(request.args.get("class", "all"))
    selected_session = request.args.get("session", "all").strip()
    selected_subject = request.args.get("subject", "all").strip()
    selected_medium = request.args.get("medium", "all").strip()
    search_q = request.args.get("q", "").strip().lower()

    available_sessions = sorted(list(set(r.get("session", "") for r in all_rows if r.get("session"))), reverse=True)
    available_subjects = sorted(list(set(r.get("subject", "") for r in all_rows if r.get("subject"))))
    mediums_set = set()
    total_pdfs = 0
    for r in all_rows:
        pdfs = r.get("pdfs", [])
        total_pdfs += len(pdfs)
        for pdf in pdfs:
            if pdf.get("medium"):
                mediums_set.add(pdf.get("medium"))
    available_mediums = sorted(list(mediums_set))

    filtered = all_rows
    if selected_class != "all":
        filtered = [r for r in filtered if str(r.get("class")) == selected_class]
    if selected_session != "all":
        filtered = [r for r in filtered if r.get("session", "").lower() == selected_session.lower()]
    if selected_subject != "all":
        filtered = [r for r in filtered if r.get("subject", "").lower() == selected_subject.lower()]
    if selected_medium != "all":
        filtered = [
            r for r in filtered
            if any(pdf.get("medium", "").lower() == selected_medium.lower() for pdf in r.get("pdfs", []))
        ]
    if search_q:
        filtered = [
            r for r in filtered
            if search_q in r.get("subject", "").lower()
            or search_q in str(r.get("code", "")).lower()
            or search_q in r.get("session", "").lower()
            or search_q in r.get("type", "").lower()
            or any(search_q in pdf.get("medium", "").lower() for pdf in r.get("pdfs", []))
        ]

    filtered_pdfs_count = sum(len(r.get("pdfs", [])) for r in filtered)

    return render_template(
        "maha_pyq.html",
        pyq_items=filtered,
        total_rows=len(all_rows),
        total_pdfs=total_pdfs,
        filtered_pdfs_count=filtered_pdfs_count,
        available_sessions=available_sessions,
        available_subjects=available_subjects,
        available_mediums=available_mediums,
        selected_class=selected_class,
        selected_session=selected_session,
        selected_subject=selected_subject,
        selected_medium=selected_medium,
        search_q=search_q
    )

@app.route("/maharashtra-board/sample-papers")
def maha_sample_papers_view():
    """Maharashtra Board Sample Papers Transparency & Official Publications Guide."""
    circ_bundle = get_maha_circulars()
    publications = circ_bundle.get("publications", [])
    pyqs = get_all_maha_pyqs()
    return render_template(
        "maha_sample_papers.html",
        publications=publications,
        pyq_total_rows=len(pyqs),
        pyq_total_pdfs=sum(len(p.get("pdfs", [])) for p in pyqs)
    )

@app.route("/maharashtra-board/question-bank")
def maha_question_bank_view():
    """Maharashtra SCERT Official Question Bank (Prashnapedhi) Directory."""
    qb_data = get_maha_question_bank()
    selected_class = _normalize_maha_class(request.args.get("class", "all"))
    search_q = request.args.get("q", "").strip().lower()

    drive_folders = qb_data.get("drive_folders_2024_25", []) if isinstance(qb_data, dict) else []
    c10_all = qb_data.get("classes", {}).get("10", {}).get("items", []) if isinstance(qb_data, dict) else []
    c12_all = qb_data.get("classes", {}).get("12", {}).get("items", []) if isinstance(qb_data, dict) else []

    def filter_qb(items):
        if not search_q:
            return items
        return [
            i for i in items
            if search_q in i.get("subject", "").lower()
            or search_q in i.get("medium", "").lower()
            or search_q in i.get("batch", "").lower()
        ]

    c10_items = filter_qb(c10_all) if selected_class in ("all", "10") else []
    c12_items = filter_qb(c12_all) if selected_class in ("all", "12") else []

    return render_template(
        "maha_question_bank.html",
        metadata=qb_data.get("metadata", {}) if isinstance(qb_data, dict) else {},
        drive_folders=drive_folders,
        c10_items=c10_items,
        c12_items=c12_items,
        c10_total=len(c10_all),
        c12_total=len(c12_all),
        selected_class=selected_class,
        search_q=search_q
    )

@app.route("/maharashtra-board/date-sheet")
@app.route("/maharashtra-board/datesheets")
def maha_datesheets_view():
    """Maharashtra Board Confirmed Feb–Mar 2027 Examination Time Table (SSC & HSC)."""
    datesheets = get_maha_datesheets()
    selected_class = _normalize_maha_class(request.args.get("class", "all"))
    return render_template(
        "maha_datesheets.html",
        datesheets=datesheets,
        selected_class=selected_class
    )

@app.route("/maharashtra-board/circulars")
def maha_circulars_view():
    """Maharashtra Board Official Circulars, Hall Ticket / Result Notices & Publications."""
    bundle = get_maha_circulars()
    all_circulars = bundle.get("circulars", [])
    publications = bundle.get("publications", [])
    category = request.args.get("category", "all").strip()
    selected_class = _normalize_maha_class(request.args.get("class", "all"))
    search_q = request.args.get("q", "").strip().lower()

    available_categories = sorted(list(set(c.get("category", "") for c in all_circulars if c.get("category"))))

    filtered = all_circulars
    if category != "all":
        filtered = [c for c in filtered if c.get("category", "").lower() == category.lower()]
    if selected_class == "10":
        filtered = [c for c in filtered if "10" in c.get("class_target", "") or "SSC" in c.get("class_target", "")]
    elif selected_class == "12":
        filtered = [c for c in filtered if "12" in c.get("class_target", "") or "HSC" in c.get("class_target", "")]
    if search_q:
        filtered = [
            c for c in filtered
            if search_q in c.get("title", "").lower()
            or search_q in c.get("summary", "").lower()
            or search_q in c.get("circular_no", "").lower()
        ]

    return render_template(
        "maha_circulars.html",
        circulars=filtered,
        publications=publications,
        total_count=len(all_circulars),
        available_categories=available_categories,
        category=category,
        selected_class=selected_class,
        search_q=search_q
    )

@app.route("/maharashtra-board/results")
def maha_results_view():
    """Maharashtra Board Results, Verification & e-Marksheet Verification Portals."""
    bundle = get_maha_circulars()
    result_circulars = [c for c in bundle.get("circulars", []) if "Result" in c.get("category", "") or "marksheet" in c.get("id", "")]
    return render_template(
        "maha_results.html",
        result_circulars=result_circulars
    )

# ----------------- Unified Multi-Board Search -----------------

def _normalize_search_board(board_val):
    val = (board_val or "all").strip().lower()
    if val in ("cbse",):
        return "cbse"
    if val in ("cisce", "icse", "isc"):
        return "cisce"
    if val in ("up-board", "upmsp", "up"):
        return "up-board"
    if val in ("bihar-board", "bseb", "bihar"):
        return "bihar-board"
    if val in ("maharashtra-board", "msbshse", "maharashtra"):
        return "maharashtra-board"
    return "all"

@app.route("/search")
def search():
    query = request.args.get("q", "").strip().lower()
    filter_board = _normalize_search_board(request.args.get("board", "all"))
    filter_class = request.args.get("class", "all")
    filter_subject = request.args.get("subject", "all")
    filter_category = request.args.get("category", "all")
    filter_year = request.args.get("year", "all")

    syllabus_items = get_all_syllabus()
    circular_items = get_circulars()
    datesheets_data = get_datesheets()
    icse_syllabus_items = get_all_icse_syllabus()
    icse_circular_items = get_icse_circulars()
    up_syllabus_items = get_all_up_syllabus()
    up_circular_items = get_up_circulars()
    up_sample_papers = get_all_up_sample_papers()

    bseb_syl_data = get_bseb_syllabus()
    bseb_pdfs = bseb_syl_data.get("official_pdfs", []) if isinstance(bseb_syl_data, dict) else []
    bseb_sample_papers = get_all_bseb_sample_papers()
    bseb_circular_items = get_bseb_circulars()

    maha_syl_data = get_maha_syllabus()
    maha_frameworks = maha_syl_data.get("curriculum_frameworks", []) if isinstance(maha_syl_data, dict) else []
    maha_ssc = maha_syl_data.get("ssc_subjects", []) if isinstance(maha_syl_data, dict) else []
    maha_hsc = maha_syl_data.get("hsc_subjects", []) if isinstance(maha_syl_data, dict) else []
    maha_pyqs = get_all_maha_pyqs()
    maha_qbank = get_maha_question_bank()
    maha_circ_bundle = get_maha_circulars()

    results = []

    # 1. Search in Syllabus (CBSE, CISCE, UP Board, BSEB, MSBSHSE)
    if filter_category in ("all", "syllabus"):
        if filter_board in ("all", "cbse"):
            for s in syllabus_items:
                matches_query = (
                    not query
                    or query in s.get("subject", "").lower()
                    or query in s.get("code", "").lower()
                    or query in s.get("title", "").lower()
                    or query in s.get("description", "").lower()
                    or "cbse" in query
                )
                matches_class = (filter_class == "all" or s.get("class") == filter_class)
                matches_subj = (filter_subject == "all" or filter_subject.lower() in s.get("subject", "").lower())
                matches_year = (filter_year == "all" or s.get("academic_year") == filter_year)

                if matches_query and matches_class and matches_subj and matches_year:
                    results.append({
                        "board": "CBSE",
                        "type": "CBSE Syllabus",
                        "badge_color": "primary",
                        "title": s.get("title"),
                        "subtitle": f"CBSE Class {s.get('class')} | Code: {s.get('code')} | {s.get('academic_year_label', s.get('academic_year'))}",
                        "description": s.get("description"),
                        "url": f"/cbse/syllabus/{s.get('id')}",
                        "official_pdf": s.get("official_url"),
                        "is_official": s.get("verification_status") == "verified_official",
                        "verification_status": s.get("verification_status", "verified_official"),
                        "last_verified": s.get("last_verified")
                    })

        if filter_board in ("all", "cisce"):
            for s in icse_syllabus_items:
                matches_query = (
                    not query
                    or query in s.get("subject", "").lower()
                    or query in s.get("code", "").lower()
                    or query in s.get("title", "").lower()
                    or query in s.get("description", "").lower()
                    or "icse" in query or "isc" in query or "cisce" in query
                )
                matches_class = (filter_class == "all" or s.get("class") == filter_class)
                matches_subj = (filter_subject == "all" or filter_subject.lower() in s.get("subject", "").lower())
                matches_year = (filter_year == "all" or s.get("academic_year") == filter_year)

                if matches_query and matches_class and matches_subj and matches_year:
                    results.append({
                        "board": "CISCE",
                        "type": f"{s.get('course', 'ICSE')} Syllabus",
                        "badge_color": "info",
                        "title": s.get("title"),
                        "subtitle": f"{s.get('course', 'ICSE')} Class {s.get('class')} | Code: {s.get('code')} | {s.get('academic_year_label', s.get('academic_year'))}",
                        "description": s.get("description"),
                        "url": f"/icse/syllabus/{s.get('id')}",
                        "official_pdf": s.get("official_url"),
                        "is_official": s.get("verification_status") == "verified_official",
                        "verification_status": s.get("verification_status", "verified_official"),
                        "last_verified": s.get("last_verified")
                    })

        if filter_board in ("all", "up-board"):
            for s in up_syllabus_items:
                matches_query = (
                    not query
                    or query in s.get("subject", "").lower()
                    or query in s.get("code", "").lower()
                    or query in s.get("title", "").lower()
                    or query in s.get("description", "").lower()
                    or "up board" in query or "upmsp" in query
                )
                matches_class = (filter_class == "all" or str(s.get("class")) == filter_class)
                matches_subj = (filter_subject == "all" or filter_subject.lower() in s.get("subject", "").lower())
                matches_year = (filter_year == "all" or s.get("academic_session") == filter_year or s.get("academic_year") == filter_year)

                if matches_query and matches_class and matches_subj and matches_year:
                    results.append({
                        "board": "UP Board (UPMSP)",
                        "type": "UP Board Syllabus",
                        "badge_color": "primary",
                        "title": s.get("title") or f"UP Board Class {s.get('class')} {s.get('subject')}",
                        "subtitle": f"UPMSP Class {s.get('class')} ({s.get('course')}) | Code: {s.get('code')} | {s.get('academic_session', '2026-27')}",
                        "description": s.get("description") or f"Official UPMSP syllabus PDF for {s.get('subject')}.",
                        "url": f"/up-board/syllabus?class={s.get('class')}",
                        "official_pdf": s.get("official_url"),
                        "is_official": s.get("verification_status") == "verified_official",
                        "verification_status": s.get("verification_status", "verified_official"),
                        "last_verified": s.get("last_verified")
                    })

        if filter_board in ("all", "bihar-board"):
            for s in bseb_pdfs:
                matches_query = (
                    not query
                    or query in s.get("subject", "").lower()
                    or query in s.get("title", "").lower()
                    or query in s.get("description", "").lower()
                    or query in s.get("course", "").lower()
                    or "bihar" in query or "bseb" in query or "matric" in query or "intermediate" in query
                )
                matches_class = (filter_class == "all" or str(s.get("class")) == filter_class)
                matches_subj = (filter_subject == "all" or filter_subject.lower() in s.get("subject", "").lower() or filter_subject.lower() in s.get("description", "").lower())
                matches_year = (filter_year == "all" or filter_year in str(s.get("academic_year", "")) or filter_year in str(s.get("academic_session", "")))

                if matches_query and matches_class and matches_subj and matches_year:
                    results.append({
                        "board": "Bihar Board (BSEB)",
                        "type": "Bihar Board Syllabus",
                        "badge_color": "info",
                        "title": s.get("title"),
                        "subtitle": f"BSEB Class {s.get('class')} | {s.get('course')} | {s.get('file_size')}",
                        "description": s.get("description"),
                        "url": f"/bihar-board/syllabus?class={s.get('class')}",
                        "official_pdf": s.get("official_url"),
                        "is_official": True,
                        "verification_status": "verified_official",
                        "last_verified": s.get("last_verified")
                    })

        if filter_board in ("all", "maharashtra-board"):
            for fw in maha_frameworks:
                matches_query = (
                    not query
                    or query in fw.get("title", "").lower()
                    or query in fw.get("authority", "").lower()
                    or "maharashtra" in query or "msbshse" in query or "scert" in query or "balbharati" in query or "scf" in query
                )
                matches_subj = (filter_subject == "all")
                matches_year = (filter_year in ("all", "2026-27"))
                if matches_query and matches_subj and matches_year:
                    results.append({
                        "board": "SCERT Maharashtra / Balbharati",
                        "type": "Maharashtra Curriculum Framework",
                        "badge_color": "info",
                        "title": fw.get("title"),
                        "subtitle": f"{fw.get('authority')} | Scope: {fw.get('class_scope')}",
                        "description": "Verified Maharashtra State curriculum framework / Balbharati official textbook portal referenced on StudySignal.",
                        "url": "/maharashtra-board/syllabus",
                        "official_pdf": fw.get("official_url"),
                        "is_official": True,
                        "verification_status": "verified_official",
                        "last_verified": fw.get("last_verified")
                    })

            for cls_num, course_lbl, subj_list in [("10", "SSC", maha_ssc), ("12", "HSC", maha_hsc)]:
                if filter_class != "all" and filter_class != cls_num:
                    continue
                for subj in subj_list:
                    matches_query = (
                        not query
                        or query in subj.get("subject", "").lower()
                        or query in subj.get("subject_mr", "").lower()
                        or query in str(subj.get("code", "")).lower()
                        or query in subj.get("category", "").lower()
                        or "maharashtra" in query or "msbshse" in query or course_lbl.lower() in query
                    )
                    matches_subj = (filter_subject == "all" or filter_subject.lower() in subj.get("subject", "").lower())
                    matches_year = (filter_year in ("all", "2026-27"))
                    if matches_query and matches_subj and matches_year:
                        results.append({
                            "board": "Maharashtra Board (MSBSHSE)",
                            "type": f"MSBSHSE {course_lbl} Subject Code",
                            "badge_color": "primary",
                            "title": f"{course_lbl} Std. {cls_num} – {subj.get('subject')} ({subj.get('subject_mr')})",
                            "subtitle": f"MSBSHSE Code: {subj.get('code')} | Category: {subj.get('category')}",
                            "description": "Verified official MSBSHSE subject code entry. Individual subject syllabusPdf attachments are not uploaded on mahahsscboard.in; refer to SCERT frameworks and Balbharati textbooks.",
                            "url": f"/maharashtra-board/syllabus?class={cls_num}&q={subj.get('code')}",
                            "official_pdf": None,
                            "is_official": True,
                            "verification_status": "verified_official",
                            "last_verified": "2026-11-10"
                        })

    # 2. Search in Model Question Papers / Sample Papers (UP Board & Bihar Board)
    if filter_category in ("all", "model_paper"):
        if filter_board in ("all", "up-board"):
            for p in up_sample_papers:
                matches_query = (
                    not query
                    or query in p.get("subject", "").lower()
                    or query in str(p.get("code", "")).lower()
                    or query in p.get("title", "").lower()
                    or "up board" in query or "upmsp" in query or "model" in query or "sample" in query
                )
                matches_class = (filter_class == "all" or str(p.get("class")) == filter_class)
                matches_subj = (filter_subject == "all" or filter_subject.lower() in p.get("subject", "").lower())
                matches_year = (filter_year == "all" or filter_year in str(p.get("academic_session", "")))
                if matches_query and matches_class and matches_subj and matches_year:
                    results.append({
                        "board": "UP Board (UPMSP)",
                        "type": "UP Board Sample Paper",
                        "badge_color": "info",
                        "title": p.get("title") or f"UP Board Class {p.get('class')} {p.get('subject')} Sample Paper",
                        "subtitle": f"Code: {p.get('code')} | {p.get('course')} | Session: {p.get('academic_session', '2026-27')}",
                        "description": f"Official UPMSP specimen/sample paper ({p.get('max_marks', '')} marks).",
                        "url": f"/up-board/sample-papers?class={p.get('class')}",
                        "official_pdf": p.get("download_url") or p.get("view_url"),
                        "is_official": True,
                        "verification_status": "verified_official",
                        "last_verified": p.get("last_verified")
                    })

        if filter_board in ("all", "bihar-board"):
            for p in bseb_sample_papers:
                matches_query = (
                    not query
                    or query in p.get("subject", "").lower()
                    or query in str(p.get("code", "")).lower()
                    or query in p.get("title", "").lower()
                    or query in p.get("stream", "").lower()
                    or "bihar" in query or "bseb" in query or "model" in query or "sample" in query
                )
                matches_class = (filter_class == "all" or str(p.get("class")) == filter_class)
                matches_subj = (filter_subject == "all" or filter_subject.lower() in p.get("subject", "").lower())
                matches_year = (filter_year == "all" or "2026" in filter_year)
                if matches_query and matches_class and matches_subj and matches_year:
                    results.append({
                        "board": "Bihar Board (BSEB)",
                        "type": "BSEB Model Paper (Not PYQ)",
                        "badge_color": "info",
                        "title": p.get("title"),
                        "subtitle": f"{p.get('course')} | Code: {p.get('code')} | {p.get('stream')} | {p.get('file_size')}",
                        "description": f"{p.get('paper_badge')} — Verified directly from biharboardonline.com.",
                        "url": f"/bihar-board/sample-papers?class={p.get('class')}&q={p.get('code')}",
                        "official_pdf": p.get("download_url"),
                        "is_official": True,
                        "verification_status": "verified_official",
                        "last_verified": p.get("last_verified")
                    })

    # 3. Search in Past Board Question Papers / PYQs (Maharashtra Board & ICSE when specifically requested or all)
    if filter_category in ("all", "pyq"):
        if filter_board in ("all", "maharashtra-board"):
            for r in maha_pyqs:
                matches_query = (
                    not query
                    or query in r.get("subject", "").lower()
                    or query in str(r.get("code", "")).lower()
                    or query in r.get("session", "").lower()
                    or query in r.get("type", "").lower()
                    or "maharashtra" in query or "msbshse" in query or "pyq" in query
                )
                matches_class = (filter_class == "all" or str(r.get("class")) == filter_class)
                matches_subj = (filter_subject == "all" or filter_subject.lower() in r.get("subject", "").lower())
                matches_year = (filter_year == "all" or filter_year in r.get("session", ""))
                if matches_query and matches_class and matches_subj and matches_year:
                    pdfs = r.get("pdfs") or []
                    first_pdf = pdfs[0] if pdfs else {}
                    med_list = ", ".join(pdf.get("medium", "") for pdf in pdfs) if pdfs else "Not currently hosted on archive"
                    results.append({
                        "board": "Maharashtra Board (MSBSHSE)",
                        "type": f"MSBSHSE {r.get('type')} PYQ ({r.get('session')})",
                        "badge_color": "primary",
                        "title": f"MSBSHSE {r.get('course')} – {r.get('subject')} ({r.get('session')})",
                        "subtitle": f"Code: {r.get('code')} | Paper {r.get('paper')} | Mediums: {med_list}",
                        "description": "Official Maharashtra State Board past examination question paper hosted on mahahsscboard.in." if pdfs else "Listed on mahahsscboard.in past paper directory; PDF attachment not currently hosted on official server.",
                        "url": f"/maharashtra-board/pyq?class={r.get('class')}&q={r.get('code')}",
                        "official_pdf": first_pdf.get("url") if pdfs else None,
                        "is_official": bool(pdfs),
                        "verification_status": "verified_official" if pdfs else "unverified",
                        "last_verified": r.get("last_verified")
                    })

    # 4. Search in SCERT Maharashtra Question Bank (Prashnapedhi)
    if filter_category in ("all", "question_bank"):
        if filter_board in ("all", "maharashtra-board") and isinstance(maha_qbank, dict):
            for cls_num in ("10", "12"):
                if filter_class != "all" and filter_class != cls_num:
                    continue
                for qb in maha_qbank.get("classes", {}).get(cls_num, {}).get("items", []):
                    matches_query = (
                        not query
                        or query in qb.get("subject", "").lower()
                        or query in qb.get("medium", "").lower()
                        or "scert" in query or "question bank" in query or "prashnapedhi" in query or "maharashtra" in query
                    )
                    matches_subj = (filter_subject == "all" or filter_subject.lower() in qb.get("subject", "").lower())
                    matches_year = (filter_year == "all")
                    if matches_query and matches_subj and matches_year:
                        results.append({
                            "board": "SCERT Maharashtra",
                            "type": "SCERT Question Bank (Prashnapedhi)",
                            "badge_color": "success",
                            "title": f"{qb.get('course')} – {qb.get('subject')} ({qb.get('medium')})",
                            "subtitle": f"SCERT Maharashtra (maa.ac.in) | {qb.get('batch')} | {qb.get('file_size')}",
                            "description": "Official SCERT Maharashtra Prashnapedhi practice question bank PDF.",
                            "url": f"/maharashtra-board/question-bank?class={cls_num}",
                            "official_pdf": qb.get("download_url"),
                            "is_official": True,
                            "verification_status": "verified_official",
                            "last_verified": qb.get("last_verified")
                        })

    # 5. Search in Circulars (CBSE, CISCE, UP Board, BSEB, MSBSHSE)
    if filter_category in ("all", "circular", "exam_notice"):
        if filter_board in ("all", "cbse"):
            for c in circular_items:
                is_demo = c.get("is_demo") or c.get("verification_status") == "demo"
                if not getattr(Config, "SHOW_DEMO_DATA", True) and is_demo:
                    continue

                matches_query = (
                    not query
                    or query in c.get("title", "").lower()
                    or query in c.get("summary", "").lower()
                    or query in c.get("circular_no", "").lower()
                    or query in c.get("category", "").lower()
                    or "cbse" in query
                )
                matches_class = (filter_class == "all" or filter_class in c.get("class_target", "") or "All" in c.get("class_target", ""))
                matches_subj = (filter_subject == "all")  # Circulars are usually board-wide
                matches_year = (filter_year == "all" or c.get("academic_year") == filter_year or "Multi-Year" in str(c.get("academic_year", "")))

                if matches_query and matches_class and matches_subj and matches_year:
                    results.append({
                        "board": "CBSE",
                        "type": f"CBSE Circular ({c.get('category')})",
                        "badge_color": "warning" if is_demo else "success",
                        "title": c.get("title"),
                        "subtitle": f"{c.get('circular_no')} | Target: {c.get('class_target')} | Published: {c.get('published_date', 'Continuous')}",
                        "description": c.get("summary"),
                        "url": c.get("official_url"),
                        "official_pdf": c.get("official_url") if c.get("official_url", "").endswith(".pdf") else None,
                        "is_official": not is_demo and c.get("verification_status") == "verified_official",
                        "verification_status": c.get("verification_status", "unverified"),
                        "demo_label": c.get("demo_label") if is_demo else None,
                        "last_verified": c.get("last_verified")
                    })

        if filter_board in ("all", "cisce"):
            for c in icse_circular_items:
                matches_query = (
                    not query
                    or query in c.get("title", "").lower()
                    or query in c.get("summary", "").lower()
                    or query in c.get("circular_no", "").lower()
                    or query in c.get("category", "").lower()
                    or "icse" in query or "isc" in query or "cisce" in query
                )
                matches_class = (filter_class == "all" or filter_class in c.get("class_target", "") or "All" in c.get("class_target", ""))
                matches_subj = (filter_subject == "all")
                matches_year = (filter_year == "all" or c.get("academic_year") == filter_year or "Multi-Year" in str(c.get("academic_year", "")))

                if matches_query and matches_class and matches_subj and matches_year:
                    results.append({
                        "board": "CISCE",
                        "type": f"CISCE Notice ({c.get('category')})",
                        "badge_color": "success",
                        "title": c.get("title"),
                        "subtitle": f"{c.get('circular_no')} | Target: {c.get('class_target')} | Published: {c.get('published_date', 'Continuous')}",
                        "description": c.get("summary"),
                        "url": c.get("official_url") or "/icse/circulars",
                        "official_pdf": c.get("official_url") if c.get("official_url", "").endswith(".pdf") else None,
                        "is_official": c.get("verification_status") == "verified_official",
                        "verification_status": c.get("verification_status", "verified_official"),
                        "demo_label": None,
                        "last_verified": c.get("last_verified")
                    })

        if filter_board in ("all", "up-board"):
            for c in up_circular_items:
                matches_query = (
                    not query
                    or query in c.get("title", "").lower()
                    or query in c.get("summary", "").lower()
                    or query in c.get("circular_no", "").lower()
                    or "up board" in query or "upmsp" in query
                )
                matches_class = (filter_class == "all" or filter_class in c.get("class_target", "") or "All" in c.get("class_target", ""))
                matches_subj = (filter_subject == "all")
                matches_year = (filter_year == "all" or filter_year in str(c.get("academic_year", "")))

                if matches_query and matches_class and matches_subj and matches_year:
                    results.append({
                        "board": "UP Board (UPMSP)",
                        "type": f"UP Board Notice ({c.get('category', 'Official')})",
                        "badge_color": "success",
                        "title": c.get("title"),
                        "subtitle": f"{c.get('circular_no')} | Target: {c.get('class_target')} | Published: {c.get('published_date')}",
                        "description": c.get("summary"),
                        "url": "/up-board/circulars",
                        "official_pdf": c.get("official_url"),
                        "is_official": True,
                        "verification_status": "verified_official",
                        "last_verified": c.get("last_verified")
                    })

        if filter_board in ("all", "bihar-board"):
            for c in bseb_circular_items:
                matches_query = (
                    not query
                    or query in c.get("title", "").lower()
                    or query in c.get("summary", "").lower()
                    or query in c.get("circular_no", "").lower()
                    or query in c.get("category", "").lower()
                    or "bihar" in query or "bseb" in query
                )
                matches_class = (filter_class == "all" or filter_class in c.get("class_target", "") or "All" in c.get("class_target", ""))
                matches_subj = (filter_subject == "all")
                matches_year = (filter_year == "all" or filter_year in str(c.get("academic_year", "")))

                if matches_query and matches_class and matches_subj and matches_year:
                    results.append({
                        "board": "Bihar Board (BSEB)",
                        "type": f"BSEB Circular ({c.get('category')})",
                        "badge_color": "success",
                        "title": c.get("title"),
                        "subtitle": f"{c.get('circular_no')} | Target: {c.get('class_target')} | Published: {c.get('published_date')}",
                        "description": c.get("summary"),
                        "url": "/bihar-board/circulars",
                        "official_pdf": c.get("official_url"),
                        "is_official": True,
                        "verification_status": "verified_official",
                        "last_verified": c.get("last_verified")
                    })

        if filter_board in ("all", "maharashtra-board"):
            for c in maha_circ_bundle.get("circulars", []):
                matches_query = (
                    not query
                    or query in c.get("title", "").lower()
                    or query in c.get("summary", "").lower()
                    or query in c.get("circular_no", "").lower()
                    or query in c.get("category", "").lower()
                    or "maharashtra" in query or "msbshse" in query
                )
                matches_class = (
                    filter_class == "all"
                    or filter_class in c.get("class_target", "")
                    or (filter_class == "10" and "SSC" in c.get("class_target", ""))
                    or (filter_class == "12" and "HSC" in c.get("class_target", ""))
                )
                matches_subj = (filter_subject == "all")
                matches_year = (filter_year == "all" or filter_year in str(c.get("academic_year", "")))

                if matches_query and matches_class and matches_subj and matches_year:
                    results.append({
                        "board": "Maharashtra Board (MSBSHSE)",
                        "type": f"MSBSHSE Notice ({c.get('category')})",
                        "badge_color": "success",
                        "title": c.get("title"),
                        "subtitle": f"{c.get('circular_no')} | Target: {c.get('class_target')} | Published: {c.get('published_date')}",
                        "description": c.get("summary"),
                        "url": "/maharashtra-board/circulars",
                        "official_pdf": c.get("official_url"),
                        "is_official": True,
                        "verification_status": "verified_official",
                        "last_verified": c.get("last_verified")
                    })

    # 6. Search in Datesheets
    if filter_category in ("all", "datesheet"):
        if filter_board in ("all", "cbse") and getattr(Config, "SHOW_DEMO_DATA", True):
            for cls_key, cls_info in datesheets_data.get("classes", {}).items():
                if filter_class != "all" and filter_class != cls_key:
                    continue
                for item in cls_info.get("schedule_items", cls_info.get("items", [])):
                    matches_query = (
                        not query
                        or query in item.get("subject", "").lower()
                        or query in item.get("subject_code", "").lower()
                        or query in item.get("notes", "").lower()
                    )
                    matches_subj = (filter_subject == "all" or filter_subject.lower() in item.get("subject", "").lower())
                    if matches_query and matches_subj:
                        is_demo = item.get("verification_status") == "demo" or cls_info.get("verification_status") == "demo"
                        results.append({
                            "board": "CBSE",
                            "type": "Exam Date Sheet",
                            "badge_color": "warning" if is_demo else "info",
                            "title": f"Class {cls_key} - {item.get('subject')} (Code: {item.get('subject_code')})",
                            "subtitle": f"{item.get('exam_date')} | Session: {item.get('timing')}",
                            "description": f"{cls_info.get('demo_label', 'Sample')} - Check cbse.gov.in for confirmed dates",
                            "url": "/cbse/datesheets",
                            "official_pdf": cls_info.get("official_link"),
                            "is_official": False,
                            "verification_status": "demo" if is_demo else "unverified",
                            "demo_label": cls_info.get("demo_label") if is_demo else None
                        })

        if filter_board in ("all", "maharashtra-board"):
            maha_ds = get_maha_datesheets()
            if isinstance(maha_ds, dict):
                for cls_key in ("10", "12"):
                    if filter_class != "all" and filter_class != cls_key:
                        continue
                    cls_info = maha_ds.get("classes", {}).get(cls_key, {})
                    for item in cls_info.get("schedule_items", []):
                        matches_query = (
                            not query
                            or query in item.get("first_half", "").lower()
                            or query in item.get("second_half", "").lower()
                            or query in item.get("date", "").lower()
                            or "maharashtra" in query or "msbshse" in query or "timetable" in query
                        )
                        matches_subj = (
                            filter_subject == "all"
                            or filter_subject.lower() in item.get("first_half", "").lower()
                            or filter_subject.lower() in item.get("second_half", "").lower()
                        )
                        matches_year = (filter_year in ("all", "2026-27"))
                        if matches_query and matches_subj and matches_year:
                            results.append({
                                "board": "Maharashtra Board (MSBSHSE)",
                                "type": f"MSBSHSE 2027 Timetable ({'SSC' if cls_key == '10' else 'HSC'})",
                                "badge_color": "success",
                                "title": f"MSBSHSE {'SSC (Std. 10)' if cls_key == '10' else 'HSC (Std. 12)'} Exam — {item.get('date')} ({item.get('day')})",
                                "subtitle": f"First Half: {item.get('first_half')} | Second Half: {item.get('second_half')}",
                                "description": "Confirmed Feb–Mar 2027 Maharashtra Board examination timetable.",
                                "url": f"/maharashtra-board/datesheets?class={cls_key}",
                                "official_pdf": cls_info.get("pdf_en") or cls_info.get("pdf_gen_en"),
                                "is_official": True,
                                "verification_status": "verified_official",
                                "last_verified": maha_ds.get("last_checked")
                            })

    # If AJAX request, return JSON
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.args.get("format") == "json":
        return jsonify({
            "count": len(results),
            "results": results
        })

    # Unique subject list for dropdown filter
    all_subjects = sorted(list(set(
        [s.get("subject") for s in syllabus_items if s.get("subject")]
        + [s.get("subject") for s in icse_syllabus_items if s.get("subject")]
        + [s.get("subject") for s in up_syllabus_items if s.get("subject")]
        + [p.get("subject") for p in bseb_sample_papers if p.get("subject")]
        + [p.get("subject") for p in maha_pyqs if p.get("subject")]
    )))

    return render_template(
        "search.html",
        results=results,
        query=query,
        filter_board=filter_board,
        filter_class=filter_class,
        filter_subject=filter_subject,
        filter_category=filter_category,
        filter_year=filter_year,
        all_subjects=all_subjects
    )

# ----------------- Static / Informational Pages -----------------

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/contact", methods=["GET", "POST"])
def contact():
    submitted = False
    message = None
    if request.method == "POST":
        submitted = True
        # Do not pretend submissions are stored, delivered, or monitored
        message = (
            "Notice: Automated message delivery and storage are currently not configured on this portal. "
            "Your message was not stored or delivered, and no response can be sent. "
            "Please refer directly to official board contacts on CBSE, CISCE, UPMSP, BSEB, or MSBSHSE portals."
        )
    return render_template("contact.html", submitted=submitted, message=message)

@app.route("/privacy-policy")
def privacy_policy():
    return render_template("privacy.html")

@app.route("/terms")
def terms():
    return render_template("terms.html")

@app.route("/disclaimer")
def disclaimer():
    return render_template("disclaimer.html")

# ----------------- SEO & Robots -----------------

@app.route("/robots.txt")
def robots_txt():
    # Production sitemap URL fallback ensures 127.0.0.1 is never exposed to public crawlers
    base = get_public_base_url()
    content = f"""User-agent: *
Allow: /

Sitemap: {base}/sitemap.xml
"""
    response = make_response(content, 200)
    response.headers["Content-Type"] = "text/plain; charset=utf-8"
    return response

@app.route("/googlec86ebbde15f4cbc3.html")
def google_verification():
    return send_from_directory(os.path.join(app.root_path, "static"), "googlec86ebbde15f4cbc3.html")

@app.route("/sitemap.xml")
def sitemap_xml():
    syllabus_items = get_all_syllabus()
    datesheets = get_datesheets()
    circulars = get_circulars()
    base = get_public_base_url()
    
    # Retrieve reliable per-section modification dates where verified
    ds_lastmod = datesheets.get("last_checked") if isinstance(datesheets, dict) else None

    circ_lastmod = None
    for c in circulars:
        if c.get("iso_date"):
            circ_lastmod = c["iso_date"]
            break
        elif c.get("last_verified"):
            circ_lastmod = c["last_verified"]
            break

    maha_ds = get_maha_datesheets()
    maha_lastmod = maha_ds.get("last_checked") if isinstance(maha_ds, dict) else "2026-11-10"
    bseb_ds = get_bseb_datesheets()
    bseb_lastmod = bseb_ds.get("last_checked") if isinstance(bseb_ds, dict) else "2026-11-10"

    pages = [
        {"loc": f"{base}/", "priority": "1.0", "changefreq": "daily"},
        {"loc": f"{base}/cbse", "priority": "0.9", "changefreq": "daily"},
        {"loc": f"{base}/cbse/class-10", "priority": "0.9", "changefreq": "daily"},
        {"loc": f"{base}/cbse/class-12", "priority": "0.9", "changefreq": "daily"},
        {"loc": f"{base}/cbse/syllabus", "priority": "0.8", "changefreq": "weekly"},
        {"loc": f"{base}/cbse/datesheets", "priority": "0.9", "changefreq": "daily", "lastmod": ds_lastmod},
        {"loc": f"{base}/cbse/circulars", "priority": "0.8", "changefreq": "daily", "lastmod": circ_lastmod},
        {"loc": f"{base}/cbse/pyq", "priority": "0.8", "changefreq": "weekly"},
        {"loc": f"{base}/boards", "priority": "0.8", "changefreq": "weekly"},
        {"loc": f"{base}/icse", "priority": "0.9", "changefreq": "daily"},
        {"loc": f"{base}/icse/class-10", "priority": "0.9", "changefreq": "daily"},
        {"loc": f"{base}/icse/class-12", "priority": "0.9", "changefreq": "daily"},
        {"loc": f"{base}/icse/syllabus", "priority": "0.8", "changefreq": "weekly"},
        {"loc": f"{base}/isc/syllabus", "priority": "0.8", "changefreq": "weekly"},
        {"loc": f"{base}/icse/datesheets", "priority": "0.9", "changefreq": "daily"},
        {"loc": f"{base}/icse/circulars", "priority": "0.8", "changefreq": "daily"},
        {"loc": f"{base}/icse/pyq", "priority": "0.8", "changefreq": "weekly"},
        {"loc": f"{base}/up-board", "priority": "0.8", "changefreq": "daily"},
        {"loc": f"{base}/up-board/class-10", "priority": "0.8", "changefreq": "daily"},
        {"loc": f"{base}/up-board/class-12", "priority": "0.8", "changefreq": "daily"},
        {"loc": f"{base}/up-board/datesheets", "priority": "0.8", "changefreq": "daily"},
        {"loc": f"{base}/up-board/syllabus", "priority": "0.7", "changefreq": "weekly"},
        {"loc": f"{base}/up-board/circulars", "priority": "0.7", "changefreq": "daily"},
        {"loc": f"{base}/up-board/sample-papers", "priority": "0.7", "changefreq": "weekly"},
        {"loc": f"{base}/up-board/question-bank", "priority": "0.7", "changefreq": "weekly"},
        {"loc": f"{base}/bihar-board", "priority": "0.8", "changefreq": "daily", "lastmod": bseb_lastmod},
        {"loc": f"{base}/bihar-board/class-10", "priority": "0.8", "changefreq": "daily", "lastmod": bseb_lastmod},
        {"loc": f"{base}/bihar-board/class-12", "priority": "0.8", "changefreq": "daily", "lastmod": bseb_lastmod},
        {"loc": f"{base}/bihar-board/syllabus", "priority": "0.7", "changefreq": "weekly", "lastmod": bseb_lastmod},
        {"loc": f"{base}/bihar-board/sample-papers", "priority": "0.8", "changefreq": "weekly", "lastmod": bseb_lastmod},
        {"loc": f"{base}/bihar-board/question-bank", "priority": "0.6", "changefreq": "monthly", "lastmod": bseb_lastmod},
        {"loc": f"{base}/bihar-board/datesheets", "priority": "0.8", "changefreq": "daily", "lastmod": bseb_lastmod},
        {"loc": f"{base}/bihar-board/circulars", "priority": "0.7", "changefreq": "daily", "lastmod": bseb_lastmod},
        {"loc": f"{base}/bihar-board/results", "priority": "0.7", "changefreq": "weekly", "lastmod": bseb_lastmod},
        {"loc": f"{base}/maharashtra-board", "priority": "0.9", "changefreq": "daily", "lastmod": maha_lastmod},
        {"loc": f"{base}/maharashtra-board/class-10", "priority": "0.8", "changefreq": "daily", "lastmod": maha_lastmod},
        {"loc": f"{base}/maharashtra-board/class-12", "priority": "0.8", "changefreq": "daily", "lastmod": maha_lastmod},
        {"loc": f"{base}/maharashtra-board/syllabus", "priority": "0.8", "changefreq": "weekly", "lastmod": maha_lastmod},
        {"loc": f"{base}/maharashtra-board/pyq", "priority": "0.8", "changefreq": "weekly", "lastmod": maha_lastmod},
        {"loc": f"{base}/maharashtra-board/sample-papers", "priority": "0.7", "changefreq": "monthly", "lastmod": maha_lastmod},
        {"loc": f"{base}/maharashtra-board/question-bank", "priority": "0.8", "changefreq": "weekly", "lastmod": maha_lastmod},
        {"loc": f"{base}/maharashtra-board/datesheets", "priority": "0.9", "changefreq": "daily", "lastmod": maha_lastmod},
        {"loc": f"{base}/maharashtra-board/circulars", "priority": "0.8", "changefreq": "daily", "lastmod": maha_lastmod},
        {"loc": f"{base}/maharashtra-board/results", "priority": "0.7", "changefreq": "weekly", "lastmod": maha_lastmod},
        {"loc": f"{base}/about", "priority": "0.5", "changefreq": "monthly"},
        {"loc": f"{base}/contact", "priority": "0.5", "changefreq": "monthly"},
        {"loc": f"{base}/privacy-policy", "priority": "0.3", "changefreq": "yearly"},
        {"loc": f"{base}/terms", "priority": "0.3", "changefreq": "yearly"},
        {"loc": f"{base}/disclaimer", "priority": "0.5", "changefreq": "monthly"},
    ]

    for item in syllabus_items:
        # Exclude unverified subject records (e.g. cbse-10-ai-2027) from the sitemap
        if item.get("verification_status") == "unverified":
            continue

        is_current = (item.get("session_type") == "current" or item.get("academic_year") == "2026-27")
        priority = "0.7" if is_current else "0.3"
        changefreq = "monthly" if is_current else "yearly"

        page_entry = {
            "loc": f"{base}/cbse/syllabus/{item['id']}",
            "priority": priority,
            "changefreq": changefreq
        }
        if item.get("last_verified"):
            page_entry["lastmod"] = item["last_verified"]

        pages.append(page_entry)

    icse_syllabus_items = get_all_icse_syllabus()
    for item in icse_syllabus_items:
        page_entry = {
            "loc": f"{base}/icse/syllabus/{item['id']}",
            "priority": "0.7",
            "changefreq": "monthly"
        }
        if item.get("last_verified"):
            page_entry["lastmod"] = item["last_verified"]
        pages.append(page_entry)

    xml_lines = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml_lines.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')
    for page in pages:
        xml_lines.append("  <url>")
        xml_lines.append(f"    <loc>{page['loc']}</loc>")
        if page.get("lastmod"):
            xml_lines.append(f"    <lastmod>{page['lastmod']}</lastmod>")
        xml_lines.append(f"    <changefreq>{page['changefreq']}</changefreq>")
        xml_lines.append(f"    <priority>{page['priority']}</priority>")
        xml_lines.append("  </url>")
    xml_lines.append("</urlset>")

    response = make_response("\n".join(xml_lines), 200)
    response.headers["Content-Type"] = "application/xml; charset=utf-8"
    return response

# ----------------- Error Handlers -----------------

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template("500.html"), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    host = "0.0.0.0" if os.environ.get("PORT") else "127.0.0.1"
    debug = os.environ.get("FLASK_DEBUG", "True").lower() in ("true", "1")
    app.run(host=host, port=port, debug=debug)
