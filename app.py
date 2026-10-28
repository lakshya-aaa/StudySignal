"""
ExamPulse India - Independent CBSE Education Information Portal
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
        "default_og_image_alt": getattr(Config, "DEFAULT_OG_IMAGE_ALT", "ExamPulse India - Independent Educational Information Portal for CBSE Class 10 (Secondary) and Class 12 (Senior Secondary) Curriculum, Date Sheets, and Official Notices"),
        "disclaimer_text": Config.OFFICIAL_DISCLAIMER,
        "official_urls": Config.OFFICIAL_URLS,
        "current_academic_year": getattr(Config, "CURRENT_ACADEMIC_YEAR", "2026-27"),
        "show_demo_data": getattr(Config, "SHOW_DEMO_DATA", True),
        "ad_config": Config.ADS,
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
    syllabus_items = [s for s in get_all_syllabus() if s.get("session_type", "current") == "current"]
    datesheets = get_datesheets()
    circulars = get_circulars()
    
    # Top subjects for quick highlights
    class_10_featured = [s for s in syllabus_items if s.get("class") == "10"][:4]
    class_12_featured = [s for s in syllabus_items if s.get("class") == "12"][:4]
    latest_circulars = circulars[:4]
    
    return render_template(
        "index.html",
        class_10_featured=class_10_featured,
        class_12_featured=class_12_featured,
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
    selected_year = request.args.get("year", "all")
    search_q = request.args.get("q", "").strip().lower()

    items = get_all_syllabus()

    if selected_class != "all":
        items = [s for s in items if s.get("class") == selected_class]
    if selected_stream != "all":
        items = [s for s in items if selected_stream.lower() in s.get("stream", "").lower()]
    if selected_year != "all":
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
        if not subject_id.endswith("-2027") and not subject_id.endswith("-2025"):
            matched = next((s for s in items if s.get("id") == f"{subject_id}-2027"), None)
        elif subject_id.endswith("-2027"):
            matched = next((s for s in items if s.get("id") == subject_id.replace("-2027", "")), None)
    if not matched:
        abort(404)
    
    # Related subjects in same class and same session type
    related = [s for s in items if s.get("class") == matched.get("class") and s.get("session_type") == matched.get("session_type") and s.get("id") != matched.get("id")][:4]

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

    results = []

    # 1. Search in Syllabus
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
                    "type": "Syllabus",
                    "badge_color": "primary",
                    "title": s.get("title"),
                    "subtitle": f"Class {s.get('class')} | Code: {s.get('code')} | {s.get('academic_year_label', s.get('academic_year'))}",
                    "description": s.get("description"),
                    "url": f"/cbse/syllabus/{s.get('id')}",
                    "official_pdf": s.get("official_url"),
                    "is_official": s.get("verification_status") == "verified_official",
                    "verification_status": s.get("verification_status", "verified_official"),
                    "last_verified": s.get("last_verified")
                })

    # 2. Search in Circulars
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
                    "type": f"Circular ({c.get('category')})",
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
    all_subjects = sorted(list(set(s.get("subject") for s in syllabus_items)))

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
        {"loc": f"{base}/cbse/class-10", "priority": "0.9", "changefreq": "daily"},
        {"loc": f"{base}/cbse/class-12", "priority": "0.9", "changefreq": "daily"},
        {"loc": f"{base}/cbse/syllabus", "priority": "0.8", "changefreq": "weekly"},
        {"loc": f"{base}/cbse/datesheets", "priority": "0.9", "changefreq": "daily", "lastmod": ds_lastmod},
        {"loc": f"{base}/cbse/circulars", "priority": "0.8", "changefreq": "daily", "lastmod": circ_lastmod},
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
