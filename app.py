"""
StudySignal - Independent CBSE Education Information Portal
Phase 1 Core Flask Application
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
                "status": "Coming Soon",
                "status_code": "coming_soon",
                "status_label": "Coming Soon",
                "url": None,
                "is_clickable": False,
                "badge_class": "badge-status-soon",
                "description": "BSEB Matric and Intermediate official examination alerts, model question papers, and syllabus tracking scheduled on roadmap.",
                "actions": []
            },
            {
                "id": "msbshse",
                "name": "Maharashtra Board (MSBSHSE)",
                "full_name": "Maharashtra State Board of Secondary and Higher Secondary Education",
                "scope": "State Board • SSC (10th) & HSC (12th)",
                "status": "Coming Soon",
                "status_code": "coming_soon",
                "status_label": "Coming Soon",
                "url": None,
                "is_clickable": False,
                "badge_class": "badge-status-soon",
                "description": "Maharashtra State Board SSC and HSC curriculum guides, evaluation structures, and timetable notifications in planning.",
                "actions": []
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

    all_featured_syllabus = cbse_featured + up_featured + icse_featured

    # 4. Circulars across supported boards
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

    latest_circulars = cbse_circulars + up_circulars + icse_circulars

    # 5. Date Sheets
    cbse_datesheets = get_datesheets()
    up_datesheets = get_up_datesheets()
    icse_datesheets = get_icse_datesheets()

    # 6. Boards Directory
    boards_and_exams = get_boards_and_exams()

    return render_template(
        "index.html",
        class_10_featured=class_10_featured,
        class_12_featured=class_12_featured,
        cbse_featured_syllabus=cbse_featured,
        up_featured_syllabus=up_featured,
        icse_featured_syllabus=icse_featured,
        all_featured_syllabus=all_featured_syllabus,
        latest_circulars=latest_circulars,
        cbse_circulars=cbse_circulars,
        up_circulars=up_circulars,
        icse_circulars=icse_circulars,
        datesheets=cbse_datesheets,
        up_datesheets=up_datesheets,
        icse_datesheets=icse_datesheets,
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

@app.route("/search")
def search():
    query = request.args.get("q", "").strip().lower()
    filter_class = request.args.get("class", "all")
    filter_subject = request.args.get("subject", "all")
    filter_category = request.args.get("category", "all")
    filter_year = request.args.get("year", "all")

    syllabus_items = get_all_syllabus()
    circular_items = get_circulars()
    datesheets_data = get_datesheets()
    icse_syllabus_items = get_all_icse_syllabus()
    icse_circular_items = get_icse_circulars()

    results = []

    # 1. Search in Syllabus (CBSE & ICSE)
    if filter_category in ("all", "syllabus"):
        for s in syllabus_items:
            matches_query = (
                not query
                or query in s.get("subject", "").lower()
                or query in s.get("code", "").lower()
                or query in s.get("title", "").lower()
                or query in s.get("description", "").lower()
            )
            matches_class = (filter_class == "all" or s.get("class") == filter_class)
            matches_subj = (filter_subject == "all" or filter_subject.lower() in s.get("subject", "").lower())
            matches_year = (filter_year == "all" or s.get("academic_year") == filter_year)

            if matches_query and matches_class and matches_subj and matches_year:
                results.append({
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

        for s in icse_syllabus_items:
            matches_query = (
                not query
                or query in s.get("subject", "").lower()
                or query in s.get("code", "").lower()
                or query in s.get("title", "").lower()
                or query in s.get("description", "").lower()
            )
            matches_class = (filter_class == "all" or s.get("class") == filter_class)
            matches_subj = (filter_subject == "all" or filter_subject.lower() in s.get("subject", "").lower())
            matches_year = (filter_year == "all" or s.get("academic_year") == filter_year)

            if matches_query and matches_class and matches_subj and matches_year:
                results.append({
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

    # 2. Search in Circulars (CBSE & CISCE)
    if filter_category in ("all", "circular", "exam_notice"):
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
            )
            matches_class = (filter_class == "all" or filter_class in c.get("class_target", "") or "All" in c.get("class_target", ""))
            matches_subj = (filter_subject == "all")  # Circulars are usually board-wide
            matches_year = (filter_year == "all" or c.get("academic_year") == filter_year or "Multi-Year" in str(c.get("academic_year", "")))

            if matches_query and matches_class and matches_subj and matches_year:
                results.append({
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

        for c in icse_circular_items:
            matches_query = (
                not query
                or query in c.get("title", "").lower()
                or query in c.get("summary", "").lower()
                or query in c.get("circular_no", "").lower()
                or query in c.get("category", "").lower()
            )
            matches_class = (filter_class == "all" or filter_class in c.get("class_target", "") or "All" in c.get("class_target", ""))
            matches_subj = (filter_subject == "all")
            matches_year = (filter_year == "all" or c.get("academic_year") == filter_year or "Multi-Year" in str(c.get("academic_year", "")))

            if matches_query and matches_class and matches_subj and matches_year:
                results.append({
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

    # 3. Search in Datesheets
    if filter_category in ("all", "datesheet"):
        if getattr(Config, "SHOW_DEMO_DATA", True):
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

    # If AJAX request, return JSON
    if request.headers.get("X-Requested-With") == "XMLHttpRequest" or request.args.get("format") == "json":
        return jsonify({
            "count": len(results),
            "results": results
        })

    # Unique subject list for dropdown filter
    all_subjects = sorted(list(set([s.get("subject") for s in syllabus_items if s.get("subject")] + [s.get("subject") for s in icse_syllabus_items if s.get("subject")])))

    return render_template(
        "search.html",
        results=results,
        query=query,
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
            "Please refer directly to official board contacts at cbse.gov.in."
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
