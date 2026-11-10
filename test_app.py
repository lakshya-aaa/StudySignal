"""
StudySignal - Automated Test Suite
Phase 1 Content Integrity Audit, Broken Link Regression & Verification Tests.
"""

import json
import os
import unittest
import xml.etree.ElementTree as ET
from app import app
from config import Config

class StudySignalTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_homepage(self):
        """Test homepage loads with 200 OK, brand name, and key sections"""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("StudySignal", html)
        self.assertIn("CBSE Class 10", html)
        self.assertIn("CBSE Class 12", html)
        self.assertIn("Official Advisory", html)
        self.assertIn("cbseacademic.nic.in", html)
        # By default in production, ad placeholders are disabled
        self.assertNotIn("ad-placement-wrapper", html)
        self.assertNotIn("Advertisement", html)

    def test_class_10_hub(self):
        """Test CBSE Class 10 dedicated hub"""
        res = self.client.get("/cbse/class-10")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("CBSE Class 10 (Secondary)", html)
        self.assertIn("Mathematics", html)
        self.assertIn("Science", html)
        self.assertIn("Social Science", html)
        self.assertIn("Official PDF", html)

    def test_class_12_hub(self):
        """Test CBSE Class 12 dedicated hub with streams"""
        res = self.client.get("/cbse/class-12")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("CBSE Class 12 (Senior Secondary)", html)
        self.assertIn("Physics", html)
        self.assertIn("Chemistry", html)
        self.assertIn("Accountancy", html)
        self.assertIn("Science Stream", html)
        self.assertIn("Commerce Stream", html)

    def test_syllabus_index_and_filters(self):
        """Test syllabus catalog and filter queries"""
        # Base syllabus catalog
        res = self.client.get("/cbse/syllabus")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("CBSE Subject-wise Syllabus Directory", html)

        # Filter by Class 10
        res10 = self.client.get("/cbse/syllabus?class=10")
        self.assertEqual(res10.status_code, 200)
        html10 = res10.data.decode("utf-8")
        self.assertIn("Mathematics", html10)

        # Filter by Science Stream
        res_sci = self.client.get("/cbse/syllabus?stream=Science")
        self.assertEqual(res_sci.status_code, 200)
        html_sci = res_sci.data.decode("utf-8")
        self.assertIn("Physics", html_sci)

        # Filter by keyword
        res_q = self.client.get("/cbse/syllabus?q=biology")
        self.assertEqual(res_q.status_code, 200)
        self.assertIn("Biology", res_q.data.decode("utf-8"))

    def test_syllabus_detail(self):
        """Test single subject syllabus complete content view and 404 for removed archive pages"""
        # Historical 2024-25 archive-only page must return 404 (removed from system)
        res_hist = self.client.get("/cbse/syllabus/cbse-10-maths-2025")
        self.assertEqual(res_hist.status_code, 404)

        # Current 2026-27 syllabus
        res_curr = self.client.get("/cbse/syllabus/cbse-10-maths-2027")
        self.assertEqual(res_curr.status_code, 200)
        html_curr = res_curr.data.decode("utf-8")
        self.assertIn("Mathematics", html_curr)
        self.assertIn("041", html_curr)
        self.assertIn("80 Marks", html_curr)
        self.assertIn("CurriculumMain27/SecPart1/Maths_SecP1X_2026-27.pdf", html_curr)
        self.assertNotIn("CurriculumMain25", html_curr)

        # Non-existent subject should return 404
        res_404 = self.client.get("/cbse/syllabus/non-existent-subject")
        self.assertEqual(res_404.status_code, 404)
        self.assertIn("404", res_404.data.decode("utf-8"))

    def test_datesheets(self):
        """Test exam date sheets page, official links, and production vs demo labeling"""
        res = self.client.get("/cbse/datesheets")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("CBSE Board Exam Date Sheet Hub", html)
        # Verify verified URL is used, NOT the broken URL
        self.assertNotIn("cbsenew/examination.html", html)
        self.assertIn("cbse.gov.in/cbsenew/examination_Circular.html", html)

        # In production mode (SHOW_DEMO_DATA=False), demo badge must NOT appear
        self.assertIn("Official Timetable Pending", html)
        self.assertNotIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html)

        # When SHOW_DEMO_DATA is True (testing mode), demo badge must appear
        orig_demo = Config.SHOW_DEMO_DATA
        try:
            Config.SHOW_DEMO_DATA = True
            res_demo = self.client.get("/cbse/datesheets")
            html_demo = res_demo.data.decode("utf-8")
            self.assertIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html_demo)
        finally:
            Config.SHOW_DEMO_DATA = orig_demo

    def test_circulars(self):
        """Test circulars directory and category filters"""
        res = self.client.get("/cbse/circulars")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("CBSE Circulars & Academic Updates", html)

        # Filter by Academic category
        res_acad = self.client.get("/cbse/circulars?category=Academic")
        self.assertEqual(res_acad.status_code, 200)
        self.assertIn("Science Challenge", res_acad.data.decode("utf-8"))

        # Filter by Examination category
        res_exam = self.client.get("/cbse/circulars?category=Examination")
        self.assertEqual(res_exam.status_code, 200)

        # Verify empty Administrative category option is removed from circulars filter
        self.assertNotIn('value="Administrative"', html)
        self.assertIn('value="Academic"', html)
        self.assertIn('value="Examination"', html)

    def test_search_and_json_api(self):
        """Test search by keyword and multi-field filters with noindex directive"""
        res = self.client.get("/search?q=Chemistry")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Chemistry", html)
        # Search page must have noindex, follow to prevent indexing thin search query combinations
        self.assertIn('<meta name="robots" content="noindex, follow">', html)

        # AJAX JSON search response
        res_json = self.client.get("/search?q=Physics&format=json")
        self.assertEqual(res_json.status_code, 200)
        data = res_json.get_json()
        self.assertGreater(data["count"], 0)
        self.assertTrue(any("Physics" in r["title"] for r in data["results"]))

    def test_informational_pages(self):
        """Test About, Contact, Privacy, Terms, and Disclaimer pages"""
        for route in ["/about", "/contact", "/privacy-policy", "/terms", "/disclaimer"]:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Route {route} failed")
            html = res.data.decode("utf-8")
            self.assertIn("StudySignal", html)

    def test_contact_submission(self):
        """Test contact form behavior: limitation advisory on GET and truthful submission notice on POST"""
        # GET request must display clear pre-submission limitation advisory
        res_get = self.client.get("/contact")
        self.assertEqual(res_get.status_code, 200)
        html_get = res_get.data.decode("utf-8")
        self.assertIn("Message Delivery Advisory", html_get)
        self.assertIn("not active on this portal", html_get)
        self.assertNotIn("responds within 24 to 48 business hours", html_get)

        # POST request must not claim successful receipt or promise replies
        res_post = self.client.post("/contact", data={
            "name": "Amit Sharma",
            "email": "amit@example.com",
            "subject": "General Feedback",
            "message": "Testing portal functionality"
        })
        self.assertEqual(res_post.status_code, 200)
        html_post = res_post.data.decode("utf-8")
        self.assertNotIn("Message Received Successfully", html_post)
        self.assertNotIn("24 to 48 business hours", html_post)
        self.assertIn("Form Submission Notice", html_post)
        self.assertIn("Automated message delivery and storage are currently not configured", html_post)

    def test_robots_txt(self):
        """Test robots.txt accessibility, live sitemap, absence of 127.0.0.1 and no Disallow /search"""
        res = self.client.get("/robots.txt")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/plain", res.content_type)
        text = res.data.decode("utf-8")
        self.assertIn("User-agent: *", text)
        self.assertIn("Allow: /", text)
        self.assertIn("Sitemap:", text)
        self.assertNotIn("127.0.0.1", text, "robots.txt must never expose 127.0.0.1")
        # Ensure Disallow: /search is not used so Googlebot can crawl and see noindex
        self.assertNotIn("Disallow: /search", text)

        # Verify static/robots.txt also never exposes 127.0.0.1
        static_robots = os.path.join(app.root_path, "static", "robots.txt")
        if os.path.exists(static_robots):
            with open(static_robots, "r", encoding="utf-8") as f:
                s_text = f.read()
            self.assertNotIn("127.0.0.1", s_text)

    def test_sitemap_xml(self):
        """Test sitemap.xml validity as standard XML, exclusion of /search, exclusion of unverified AI, and URL origin"""
        res = self.client.get("/sitemap.xml")
        self.assertEqual(res.status_code, 200)
        self.assertIn("application/xml", res.content_type)
        xml_data = res.data.decode("utf-8")
        # Validate XML structure
        root = ET.fromstring(xml_data)
        self.assertTrue(root.tag.endswith("urlset"))
        # Check that URLs are present
        urls = [elem.text for elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")]
        self.assertGreater(len(urls), 10)
        self.assertTrue(any("/cbse/class-10" in u for u in urls))
        self.assertTrue(any("/cbse/class-12" in u for u in urls))

        # Ensure /search is not present in sitemap
        self.assertFalse(any(u.endswith("/search") for u in urls), "/search must be excluded from sitemap.xml")

        # Ensure unverified Class 10 AI subject is excluded from sitemap
        self.assertFalse(any("cbse-10-ai-2027" in u for u in urls), "Unverified AI subject must be excluded from sitemap")

        # Ensure production origin is used and 127.0.0.1/localhost never leak into sitemap locs
        for u in urls:
            self.assertNotIn("127.0.0.1", u, f"Sitemap URL must not contain 127.0.0.1: {u}")
            self.assertNotIn("localhost", u, f"Sitemap URL must not contain localhost: {u}")
            self.assertTrue(u.startswith("https://") or u.startswith("http://"), f"Sitemap URL must have valid scheme: {u}")

    def test_disclaimer_presence(self):
        """Test non-affiliation disclaimer presence on legal page and banner"""
        res = self.client.get("/disclaimer")
        html = res.data.decode("utf-8")
        self.assertIn("Strict Non-Affiliation Declaration", html)
        self.assertIn("independent, free-access educational information portal", html)
        self.assertIn("Central Board of Secondary Education (CBSE)", html)
        self.assertIn("cbse.gov.in", html)
        self.assertIn("cbseacademic.nic.in", html)

    def test_ad_toggle_config(self):
        """Test that turning off ads in config completely hides ad units"""
        orig_enabled = Config.ADS["enabled"]
        try:
            Config.ADS["enabled"] = False
            res = self.client.get("/")
            html = res.data.decode("utf-8")
            self.assertNotIn("ad-placement-wrapper", html)
        finally:
            Config.ADS["enabled"] = orig_enabled

    # =========================================================================
    # Regression & Audit Tests (Requirement 8)
    # =========================================================================

    def test_no_broken_cbse_examination_url(self):
        """Ensure broken URL cbsenew/examination.html is NOT present in any route or data file"""
        broken_pattern = "cbsenew/examination.html"

        # 1. Verify in config
        self.assertNotIn(broken_pattern, Config.OFFICIAL_URLS.values())

        # 2. Verify in all data files
        for filename in ["syllabus.json", "circulars.json", "datesheets.json"]:
            filepath = os.path.join(app.root_path, "data", filename)
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                self.assertNotIn(broken_pattern, content, f"Broken URL found in {filename}")

        # 3. Verify in rendered key templates
        for endpoint in ["/", "/cbse/class-10", "/cbse/class-12", "/cbse/datesheets", "/cbse/circulars", "/search", "/disclaimer"]:
            res = self.client.get(endpoint)
            self.assertEqual(res.status_code, 200)
            self.assertNotIn(broken_pattern, res.data.decode("utf-8"), f"Broken URL rendered in {endpoint}")

    def test_fixed_english_syllabus_link(self):
        """Verify Class 10 English Language & Literature syllabus link is verified and points to current 2026-27 PDF"""
        filepath = os.path.join(app.root_path, "data", "syllabus.json")
        with open(filepath, "r", encoding="utf-8") as f:
            syllabus = json.load(f)
        eng = next((s for s in syllabus if s.get("id") == "cbse-10-english-2027"), None)
        self.assertIsNotNone(eng)
        self.assertEqual(eng.get("official_url"), "https://cbseacademic.nic.in/web_material/CurriculumMain27/SecPart1/English_LL_SecP1_2026-27.pdf")
        self.assertNotIn("CurriculumMain25", eng.get("official_url"))

    def test_demo_records_badges_and_labels(self):
        """Verify demo records are hidden by default in production, and display unmistakable DEMO label when enabled"""
        # 1. Default production setting (SHOW_DEMO_DATA = False): demo records must be hidden
        res_circ = self.client.get("/cbse/circulars")
        html_circ = res_circ.data.decode("utf-8")
        self.assertNotIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html_circ)

        res_datesheet = self.client.get("/cbse/datesheets")
        html_ds = res_datesheet.data.decode("utf-8")
        self.assertNotIn("[PROTOTYPE / NON-OFFICIAL DEMO ROW]", html_ds)

        # 2. When demo data is explicitly enabled, verify badges and labels
        orig_show_demo = getattr(Config, "SHOW_DEMO_DATA", False)
        try:
            Config.SHOW_DEMO_DATA = True
            res_ds_demo = self.client.get("/cbse/datesheets")
            html_ds_demo = res_ds_demo.data.decode("utf-8")
            self.assertIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html_ds_demo)

            res_circ_demo = self.client.get("/cbse/circulars")
            html_circ_demo = res_circ_demo.data.decode("utf-8")
            self.assertIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html_circ_demo)

            # In search results, verify demo items do NOT receive verified badge
            res_search = self.client.get("/search?category=datesheet")
            html_search = res_search.data.decode("utf-8")
            if "DEMO — NOT AN OFFICIAL ANNOUNCEMENT" in html_search:
                self.assertIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html_search)
        finally:
            Config.SHOW_DEMO_DATA = orig_show_demo

    def test_demo_toggle_config(self):
        """Verify that setting SHOW_DEMO_DATA=False cleanly hides demo circulars and schedules"""
        orig_show_demo = getattr(Config, "SHOW_DEMO_DATA", True)
        try:
            Config.SHOW_DEMO_DATA = False
            res_circ = self.client.get("/cbse/circulars")
            html_circ = res_circ.data.decode("utf-8")
            self.assertNotIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html_circ)

            res_ds = self.client.get("/cbse/datesheets")
            html_ds = res_ds.data.decode("utf-8")
            self.assertNotIn("[PROTOTYPE / NON-OFFICIAL DEMO ROW]", html_ds)
        finally:
            Config.SHOW_DEMO_DATA = orig_show_demo

    def test_academic_year_preservation(self):
        """Ensure historical 2024-25 syllabus records are removed and only current 2026-27 verified records are preserved"""
        filepath = os.path.join(app.root_path, "data", "syllabus.json")
        with open(filepath, "r", encoding="utf-8") as f:
            syllabus = json.load(f)
        
        historical = [s for s in syllabus if s.get("session_type") == "historical" or s.get("academic_year") == "2024-25"]
        current = [s for s in syllabus if s.get("session_type") == "current" or s.get("academic_year") == "2026-27"]

        self.assertEqual(len(historical), 0)
        self.assertGreaterEqual(len(current), 18)

        for s in current:
            self.assertEqual(s.get("academic_year"), "2026-27")
            self.assertEqual(s.get("session_type"), "current")
            self.assertIn("Current", s.get("academic_year_label"))

        # Verify config specifies current academic year as 2026-27 (October 2026)
        self.assertEqual(Config.CURRENT_ACADEMIC_YEAR, "2026-27")

    def test_current_syllabus_not_pointing_to_old_pdfs(self):
        """Ensure current 2026-27 syllabus records do NOT point to old 2024-25 or 2025-26 archive folders"""
        filepath = os.path.join(app.root_path, "data", "syllabus.json")
        with open(filepath, "r", encoding="utf-8") as f:
            syllabus = json.load(f)

        current = [s for s in syllabus if s.get("session_type") == "current"]
        self.assertGreaterEqual(len(current), 17)

        for s in current:
            if s.get("verification_status") == "verified_official":
                url = s.get("official_url", "")
                self.assertTrue(url.startswith("https://cbseacademic.nic.in/"), f"Non-official URL: {url}")
                self.assertNotIn("CurriculumMain25", url, f"Current subject points to 2024-25 folder: {url}")
                self.assertNotIn("CurriculumMain26", url, f"Current subject points to 2025-26 folder: {url}")
                self.assertNotIn("2024-25.pdf", url, f"Current subject points to 2024-25 PDF: {url}")
                self.assertIn("CurriculumMain27", url, f"Current subject must point to CurriculumMain27: {url}")
                self.assertIn("2026-27.pdf", url, f"Current subject must be 2026-27: {url}")
                
                # Class 10 must point to SecPart1
                if s.get("class") == "10":
                    self.assertIn("SecPart1", url, f"Class 10 should point to SecPart1: {url}")
                # Class 12 must point to SecPart2
                elif s.get("class") == "12":
                    self.assertIn("SecPart2", url, f"Class 12 should point to SecPart2: {url}")

    def test_unverified_current_links_warning_and_directory(self):
        """Test that unverified current links display appropriate warning and link to official CBSE directory"""
        # Detail view for unverified subject (e.g. Class 10 AI)
        res = self.client.get("/cbse/syllabus/cbse-10-ai-2027")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Current syllabus link not verified yet", html)
        self.assertNotIn("Download Official PDF", html)
        self.assertIn("Visit Official CBSE Curriculum Directory", html)
        self.assertIn("cbseacademic.nic.in/curriculum_2027.html", html)

        # Catalog view for unverified subject
        res_cat = self.client.get("/cbse/syllabus?q=Artificial")
        self.assertEqual(res_cat.status_code, 200)
        html_cat = res_cat.data.decode("utf-8")
        self.assertIn("Current link unverified", html_cat)
        self.assertIn("Directory ↗", html_cat)

    def test_class_hubs_render_current_session_pdfs(self):
        """Ensure Class 10 and Class 12 hub pages render only current verified 2026-27 PDFs"""
        res10 = self.client.get("/cbse/class-10")
        self.assertEqual(res10.status_code, 200)
        html10 = res10.data.decode("utf-8")
        self.assertIn("CurriculumMain27/SecPart1/Maths_SecP1X_2026-27.pdf", html10)
        self.assertIn("CurriculumMain27/SecPart1/Science_SecP1_2026-27.pdf", html10)
        self.assertNotIn("CurriculumMain25/Sec/Maths_Sec_2024-25.pdf", html10)

        res12 = self.client.get("/cbse/class-12")
        self.assertEqual(res12.status_code, 200)
        html12 = res12.data.decode("utf-8")
        self.assertIn("CurriculumMain27/SecPart2/Physics_SecP2_2026-27.pdf", html12)
        self.assertIn("CurriculumMain27/SecPart2/Chemistry_SecP2_2026-27.pdf", html12)
        self.assertNotIn("CurriculumMain25/SrSec/Physics_SrSec_2024-25.pdf", html12)

    def test_ad_placeholder_copy_clean(self):
        """Verify ad placeholders are hidden when ads are disabled, and show clean labels when enabled"""
        # 1. Default production setting (ADS['enabled'] = False): ad wrappers are absent
        for route in ["/", "/cbse/class-10", "/cbse/class-12", "/cbse/syllabus"]:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200)
            html = res.data.decode("utf-8")
            self.assertNotIn("ad-placement-wrapper", html)
            self.assertNotIn("To integrate Google AdSense", html)
            self.assertNotIn("config.py", html)

        # 2. When ads are explicitly enabled, verify clean labels and NO internal developer instructions
        orig_enabled = Config.ADS["enabled"]
        try:
            Config.ADS["enabled"] = True
            for route in ["/", "/cbse/class-10", "/cbse/class-12", "/cbse/syllabus"]:
                res = self.client.get(route)
                self.assertEqual(res.status_code, 200)
                html = res.data.decode("utf-8")
                # Ensure developer instructions are never visible to users
                self.assertNotIn("To integrate Google AdSense", html)
                self.assertNotIn("config.py", html)
                # Ensure subtle, honest labels are present
                self.assertIn("Advertisement", html)
                self.assertIn("Sponsored placement", html)
                self.assertIn("Reserved space for future non-intrusive educational sponsorships", html)
        finally:
            Config.ADS["enabled"] = orig_enabled

    def test_circular_verification_badges_and_directories(self):
        """Verify individual notices vs official directories vs demo items have distinct badges"""
        res = self.client.get("/cbse/circulars")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # 1. Verified specific notices
        self.assertIn("✓ Verified Official Notice", html)
        self.assertIn("View Official PDF ↗", html)

        # 2. Portal directories (must NOT claim to be verified individual notices)
        self.assertIn("Official Portal Directory", html)
        self.assertIn("Open Directory Portal ↗", html)

        # 3. In default production mode (SHOW_DEMO_DATA = False), demo entries are hidden
        self.assertNotIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html)

        # 4. When demo data is explicitly enabled, verify demo items receive distinct demo badge
        orig_show_demo = getattr(Config, "SHOW_DEMO_DATA", False)
        try:
            Config.SHOW_DEMO_DATA = True
            res_demo = self.client.get("/cbse/circulars")
            html_demo = res_demo.data.decode("utf-8")
            self.assertIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html_demo)
        finally:
            Config.SHOW_DEMO_DATA = orig_show_demo

    def test_class_12_syllabus_descriptions_and_marks(self):
        """Verify Class 12 descriptions clarify Senior Secondary scope and AI remains unverified"""
        filepath = os.path.join(app.root_path, "data", "syllabus.json")
        with open(filepath, "r", encoding="utf-8") as f:
            syllabus = json.load(f)

        current_12 = [s for s in syllabus if s.get("class") == "12" and s.get("session_type") == "current"]
        self.assertEqual(len(current_12), 11)

        for s in current_12:
            desc = s.get("description", "")
            # Must clarify document covers Classes XI & XII while card presents Class XII
            self.assertIn("covering Classes XI & XII", desc)
            self.assertIn("presenting Class XII", desc)

            # Check that marks and duration exist
            exam = s.get("exam_structure", {})
            self.assertIn("theory_marks", exam)
            self.assertIn("internal_assessment_marks", exam)
            self.assertIn("duration_hours", exam)

        # Confirm Class 10 AI remains unverified until official syllabus is confirmed
        ai_item = next((s for s in syllabus if s.get("id") == "cbse-10-ai-2027"), None)
        self.assertIsNotNone(ai_item)
        self.assertEqual(ai_item.get("verification_status"), "unverified")

    # =========================================================================
    # Render & Production Deployment Tests
    # =========================================================================

    def test_gunicorn_wsgi_entrypoint_and_requirements(self):
        """Verify gunicorn is specified in requirements.txt and app:app WSGI callable is valid"""
        req_path = os.path.join(app.root_path, "requirements.txt")
        self.assertTrue(os.path.exists(req_path), "requirements.txt must exist")
        with open(req_path, "r", encoding="utf-8") as f:
            reqs = f.read()
        self.assertIn("gunicorn", reqs, "gunicorn must be listed in requirements.txt")
        self.assertIn("flask", reqs, "flask must be listed in requirements.txt")

        # Verify WSGI entrypoint app:app
        import app as app_module
        from flask import Flask
        self.assertTrue(hasattr(app_module, "app"), "app.py must expose 'app'")
        self.assertIsInstance(app_module.app, Flask, "app must be an instance of Flask")

        # Verify gunicorn.conf.py exists and configures dynamic PORT
        gun_conf_path = os.path.join(app.root_path, "gunicorn.conf.py")
        self.assertTrue(os.path.exists(gun_conf_path), "gunicorn.conf.py must exist")
        with open(gun_conf_path, "r", encoding="utf-8") as f:
            gun_conf = f.read()
        self.assertIn("PORT", gun_conf)
        self.assertIn("0.0.0.0", gun_conf)

    def test_deployment_assets_and_gitignore(self):
        """Verify .gitignore exists, protects secrets/caches, and preserves required data & static assets"""
        gitignore_path = os.path.join(app.root_path, ".gitignore")
        self.assertTrue(os.path.exists(gitignore_path), ".gitignore must exist")
        with open(gitignore_path, "r", encoding="utf-8") as f:
            gi_lines = [line.strip() for line in f.readlines() if line.strip() and not line.startswith("#")]

        # Must ignore bytecode, env secrets, and virtual environments
        self.assertIn("__pycache__/", gi_lines)
        self.assertIn(".env", gi_lines)
        self.assertTrue(any("venv" in l for l in gi_lines))

        # Must NOT ignore production data and assets
        required_paths = [
            os.path.join("data", "syllabus.json"),
            os.path.join("data", "circulars.json"),
            os.path.join("data", "datesheets.json"),
            os.path.join("static", "css", "style.css"),
            os.path.join("static", "js", "main.js"),
            os.path.join("static", "images", "favicon.svg"),
            os.path.join("static", "images", "studysignal-logo.svg"),
            os.path.join("static", "images", "studysignal-icon.svg"),
            os.path.join("static", "images", "og-preview.png"),
            os.path.join("static", "images", "og-preview-master.png"),
            os.path.join("static", "googlec86ebbde15f4cbc3.html"),
            os.path.join("templates", "base.html"),
            os.path.join("templates", "index.html"),
        ]
        for rel_path in required_paths:
            full_path = os.path.join(app.root_path, rel_path)
            self.assertTrue(os.path.exists(full_path), f"Required deployment asset missing: {rel_path}")
            # Ensure none of the gitignore rules accidentally match these essential files
            for rule in gi_lines:
                clean_rule = rule.rstrip("/")
                self.assertNotIn(clean_rule, rel_path.split(os.sep), f"Asset {rel_path} matched by gitignore rule {rule}")

    def test_google_search_console_verification(self):
        """Verify Google Search Console verification file is served at root with HTTP 200 and expected token"""
        res = self.client.get("/googlec86ebbde15f4cbc3.html")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/html", res.content_type)
        content = res.data.decode("utf-8").strip()
        res.close()
        self.assertEqual(content, "google-site-verification: googlec86ebbde15f4cbc3.html")

    def test_trailing_slash_redirects(self):
        """Verify trailing-slash URLs safely redirect with 301 to canonical non-slash URLs"""
        # 1. Root / must return 200 without redirect
        res_root = self.client.get("/")
        self.assertEqual(res_root.status_code, 200)

        # 2. Normal pages with trailing slash must 301 redirect to non-slash equivalent
        res_about = self.client.get("/about/")
        self.assertEqual(res_about.status_code, 301)
        self.assertTrue(res_about.headers.get("Location").endswith("/about"))

        res_c10 = self.client.get("/cbse/class-10/")
        self.assertEqual(res_c10.status_code, 301)
        self.assertTrue(res_c10.headers.get("Location").endswith("/cbse/class-10"))

        # 3. Query parameters must be preserved across redirect
        res_q = self.client.get("/cbse/syllabus/?class=10")
        self.assertEqual(res_q.status_code, 301)
        self.assertTrue(res_q.headers.get("Location").endswith("/cbse/syllabus?class=10"))

        # 4. Following redirect returns 200 OK
        res_follow = self.client.get("/about/", follow_redirects=True)
        self.assertEqual(res_follow.status_code, 200)
        self.assertIn("About Us", res_follow.data.decode("utf-8"))

        # 5. Static file and verification URL must not be affected
        res_ver = self.client.get("/googlec86ebbde15f4cbc3.html")
        self.assertEqual(res_ver.status_code, 200)

    def test_social_sharing_metadata_and_keywords(self):
        """Verify dynamic OG/Twitter metadata inheritance and updated 2026-27 meta keywords"""
        # Test homepage metadata
        res_home = self.client.get("/")
        html_home = res_home.data.decode("utf-8")
        self.assertIn('property="og:title" content="StudySignal – Multi-Board Educational Platform (CBSE, UP Board & CISCE)"', html_home)
        self.assertIn('name="twitter:title" content="StudySignal – Multi-Board Educational Platform (CBSE, UP Board & CISCE)"', html_home)
        self.assertIn('2026-27', html_home)
        # Check keywords tag specifically
        kw_part = html_home.split('name="keywords"')[1].split('>')[0]
        self.assertIn('2026-27', kw_part)
        self.assertNotIn('2024-25', kw_part, "Meta keywords must not reference 2024-25")

        # Test subpage metadata inheritance (Class 10 Hub)
        res_c10 = self.client.get("/cbse/class-10")
        html_c10 = res_c10.data.decode("utf-8")
        self.assertIn('property="og:title" content="CBSE Class 10 (Secondary) - StudySignal"', html_c10)
        self.assertIn('name="twitter:title" content="CBSE Class 10 (Secondary) - StudySignal"', html_c10)
        self.assertIn('Complete guide for CBSE Class 10 (Secondary)', html_c10)
        # Verify it does NOT fall back to generic site tagline
        self.assertNotIn('property="og:title" content="StudySignal - Independent CBSE Education Information Portal"', html_c10)

    def test_social_image_metadata_and_asset(self):
        """Verify Open Graph & Twitter social sharing image tags, accessibility, dimensions and master preservation"""
        from PIL import Image

        # 1. Verify meta tags in rendered homepage HTML
        res_home = self.client.get("/")
        self.assertEqual(res_home.status_code, 200)
        html = res_home.data.decode("utf-8")

        expected_og_image = "https://exampulse-india.onrender.com/static/images/og-preview.png"
        self.assertIn(f'property="og:image" content="{expected_og_image}"', html)
        self.assertIn('property="og:image:width" content="1200"', html)
        self.assertIn('property="og:image:height" content="630"', html)
        self.assertIn('property="og:image:alt"', html)
        self.assertIn("CBSE Class 10 (Secondary) and Class 12 (Senior Secondary)", html)
        self.assertIn('name="twitter:card" content="summary_large_image"', html)
        self.assertIn(f'name="twitter:image" content="{expected_og_image}"', html)
        self.assertIn('name="twitter:image:alt"', html)

        # 2. Verify subpage inherits the same default og:image
        res_c12 = self.client.get("/cbse/class-12")
        self.assertEqual(res_c12.status_code, 200)
        html_c12 = res_c12.data.decode("utf-8")
        self.assertIn(f'property="og:image" content="{expected_og_image}"', html_c12)
        self.assertIn(f'name="twitter:image" content="{expected_og_image}"', html_c12)

        # 3. Verify static file route serves the image with HTTP 200
        res_img = self.client.get("/static/images/og-preview.png")
        self.assertEqual(res_img.status_code, 200)
        self.assertIn("image/png", res_img.content_type)
        res_img.close()

        # 4. Verify physical image dimensions and file size on disk
        og_path = os.path.join(app.root_path, "static", "images", "og-preview.png")
        self.assertTrue(os.path.exists(og_path), "Optimized og-preview.png must exist")
        file_size = os.path.getsize(og_path)
        self.assertLess(file_size, 1024 * 1024, f"Image size ({file_size} bytes) should be < 1 MB")

        with Image.open(og_path) as img:
            self.assertEqual(img.size, (1200, 630), f"Dimensions must be exactly 1200x630, got {img.size}")
            self.assertEqual(img.format, "PNG")

        # 5. Verify master backup exists and preserves original resolution
        master_path = os.path.join(app.root_path, "static", "images", "og-preview-master.png")
        self.assertTrue(os.path.exists(master_path), "Master backup og-preview-master.png must exist")
        with Image.open(master_path) as master_img:
            self.assertEqual(master_img.size, (1733, 907), f"Master dimensions should be (1733, 907), got {master_img.size}")

    def test_syllabus_educational_content_and_unit_breakdown(self):
        """Verify syllabus detail pages render rich authentic unit marks, textbooks, and question paper design"""
        # Test Class 10 Mathematics
        res_m10 = self.client.get("/cbse/syllabus/cbse-10-maths-2027")
        self.assertEqual(res_m10.status_code, 200)
        html_m10 = res_m10.data.decode("utf-8")
        
        self.assertIn("Official Unit-Wise Marks Distribution", html_m10)
        self.assertIn("Number Systems", html_m10)
        self.assertIn("6 Marks", html_m10)
        self.assertIn("Algebra", html_m10)
        self.assertIn("20 Marks", html_m10)
        self.assertIn("Official Question Paper Design & Typology", html_m10)
        self.assertIn("Remembering &amp; Understanding", html_m10)
        self.assertIn("Prescribed Textbooks & Reading Materials", html_m10)
        self.assertIn("Mathematics - Textbook for Class X", html_m10)
        self.assertIn("Internal Assessment (20 Marks)", html_m10)
        self.assertIn("Lab Practical Activities", html_m10)

        # Test Class 12 Physics
        res_p12 = self.client.get("/cbse/syllabus/cbse-12-physics-2027")
        self.assertEqual(res_p12.status_code, 200)
        html_p12 = res_p12.data.decode("utf-8")

        self.assertIn("Electrostatics &amp; Current Electricity", html_p12)
        self.assertIn("16 Marks", html_p12)
        self.assertIn("Electromagnetic Waves &amp; Optics", html_p12)
        self.assertIn("18 Marks", html_p12)
        self.assertIn("Physics Part-I, Class XII", html_p12)
        self.assertIn("Two Experiments", html_p12)

    def test_distinction_between_official_data_and_editorial_advice(self):
        """Verify clear visual and textual separation between official CBSE syllabus and editorial study advice"""
        res = self.client.get("/cbse/syllabus/cbse-10-science-2027")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # Official markers
        self.assertIn("Official CBSE Curriculum Weightage", html)
        self.assertIn("Board Assessment Pattern", html)

        # Editorial advice markers
        self.assertIn("💡 StudySignal Independent Editorial Study Advice", html)
        self.assertIn("Non-Statutory Study Strategy", html)
        self.assertIn("do not constitute official CBSE mandates", html)

    def test_unverified_subject_educational_content_notice(self):
        """Verify unverified subject (Class 10 AI) explicitly shows verification advisory instead of guessed units"""
        res_ai = self.client.get("/cbse/syllabus/cbse-10-ai-2027")
        self.assertEqual(res_ai.status_code, 200)
        html_ai = res_ai.data.decode("utf-8")

        self.assertIn("Curriculum Unit Verification Notice", html_ai)
        self.assertIn("pending official verification against the CBSE Skill Education directory", html_ai)
        self.assertNotIn("Official Unit-Wise Marks Distribution", html_ai)

    def test_factual_accuracy_audit_corrections_class10(self):
        """Verify factual audit corrections for Class 10 Science (086) and Computer Applications (165)"""
        filepath = os.path.join(app.root_path, "data", "syllabus.json")
        with open(filepath, "r", encoding="utf-8") as f:
            syllabus = json.load(f)

        # 1. Class 10 Science (086) QPD: 50% (40M), 30% (24M), 20% (16M)
        sci10 = next(s for s in syllabus if s.get("id") == "cbse-10-science-2027")
        sci_typo = sci10["question_paper_design"]["typology"]
        self.assertEqual(len(sci_typo), 3)
        self.assertEqual(sci_typo[0]["percentage"], "50%")
        self.assertEqual(sci_typo[0]["marks"], 40)
        self.assertEqual(sci_typo[1]["percentage"], "30%")
        self.assertEqual(sci_typo[1]["marks"], 24)
        self.assertEqual(sci_typo[2]["percentage"], "20%")
        self.assertEqual(sci_typo[2]["marks"], 16)
        self.assertEqual(sum(t["marks"] for t in sci_typo), 80)

        res_sci = self.client.get("/cbse/syllabus/cbse-10-science-2027")
        self.assertEqual(res_sci.status_code, 200)
        html_sci = res_sci.data.decode("utf-8")
        self.assertIn("Demonstrate Knowledge and Understanding", html_sci)
        self.assertIn("50%", html_sci)
        self.assertIn("40 M", html_sci)
        self.assertIn("Application of Knowledge and Concepts", html_sci)
        self.assertIn("30%", html_sci)
        self.assertIn("24 M", html_sci)
        self.assertIn("Formulate, Analyse, Evaluate and Create", html_sci)
        self.assertIn("20%", html_sci)
        self.assertIn("16 M", html_sci)

        # 2. Class 10 Computer Applications (165) Unit Names: Networking (15M), HTML (25M), Cyber ethics (10M)
        ca10 = next(s for s in syllabus if s.get("id") == "cbse-10-computer-app-2027")
        unit_names = [(u.get("name"), u.get("marks")) for u in ca10.get("units", [])]
        self.assertEqual(unit_names, [("Networking", 15), ("HTML", 25), ("Cyber ethics", 10)])
        self.assertEqual(sum(u.get("marks") for u in ca10.get("units", [])), 50)

        res_ca = self.client.get("/cbse/syllabus/cbse-10-computer-app-2027")
        self.assertEqual(res_ca.status_code, 200)
        html_ca = res_ca.data.decode("utf-8")
        self.assertIn("Networking", html_ca)
        self.assertIn("HTML", html_ca)
        self.assertIn("Cyber ethics", html_ca)
        self.assertNotIn("Networking and Cyberethics", html_ca)
        self.assertNotIn("Cyber Safety", html_ca)

    def test_factual_accuracy_audit_corrections_class12(self):
        """Verify factual audit corrections for Class 12 Biology, BST, Economics, History, Accountancy, and CS"""
        filepath = os.path.join(app.root_path, "data", "syllabus.json")
        with open(filepath, "r", encoding="utf-8") as f:
            syllabus = json.load(f)

        # 3. Class 12 Biology (044) QPD: 50% (35M), 30% (21M), 20% (14M)
        bio12 = next(s for s in syllabus if s.get("id") == "cbse-12-biology-2027")
        bio_typo = bio12["question_paper_design"]["typology"]
        self.assertEqual(len(bio_typo), 3)
        self.assertEqual(bio_typo[0]["percentage"], "50%")
        self.assertEqual(bio_typo[0]["marks"], 35)
        self.assertEqual(bio_typo[1]["percentage"], "30%")
        self.assertEqual(bio_typo[1]["marks"], 21)
        self.assertEqual(bio_typo[2]["percentage"], "20%")
        self.assertEqual(bio_typo[2]["marks"], 14)
        self.assertEqual(sum(t["marks"] for t in bio_typo), 70)

        res_bio = self.client.get("/cbse/syllabus/cbse-12-biology-2027")
        html_bio = res_bio.data.decode("utf-8")
        self.assertIn("35 M", html_bio)
        self.assertIn("21 M", html_bio)
        self.assertIn("14 M", html_bio)

        # 4. Class 12 Business Studies (054) QPD: 40% (32M), 35% (28M), 25% (20M)
        bst12 = next(s for s in syllabus if s.get("id") == "cbse-12-business-studies-2027")
        bst_typo = bst12["question_paper_design"]["typology"]
        self.assertEqual(bst_typo[0]["percentage"], "40%")
        self.assertEqual(bst_typo[0]["marks"], 32)
        self.assertEqual(bst_typo[1]["percentage"], "35%")
        self.assertEqual(bst_typo[1]["marks"], 28)
        self.assertEqual(bst_typo[2]["percentage"], "25%")
        self.assertEqual(bst_typo[2]["marks"], 20)
        self.assertEqual(sum(t["marks"] for t in bst_typo), 80)

        res_bst = self.client.get("/cbse/syllabus/cbse-12-business-studies-2027")
        html_bst = res_bst.data.decode("utf-8")
        self.assertIn("32 M", html_bst)
        self.assertIn("28 M", html_bst)
        self.assertIn("20 M", html_bst)

        # 5. Class 12 Economics (030) QPD: 40% (32M), 35% (28M), 25% (20M)
        eco12 = next(s for s in syllabus if s.get("id") == "cbse-12-economics-2027")
        eco_typo = eco12["question_paper_design"]["typology"]
        self.assertEqual(eco_typo[0]["percentage"], "40%")
        self.assertEqual(eco_typo[0]["marks"], 32)
        self.assertEqual(eco_typo[1]["percentage"], "35%")
        self.assertEqual(eco_typo[1]["marks"], 28)
        self.assertEqual(eco_typo[2]["percentage"], "25%")
        self.assertEqual(eco_typo[2]["marks"], 20)
        self.assertEqual(sum(t["marks"] for t in eco_typo), 80)

        res_eco = self.client.get("/cbse/syllabus/cbse-12-economics-2027")
        html_eco = res_eco.data.decode("utf-8")
        self.assertIn("32 M", html_eco)
        self.assertIn("28 M", html_eco)
        self.assertIn("20 M", html_eco)

        # 6. Class 12 History (027) Question-Format Breakdown (Sections A-E totaling 80M)
        hist12 = next(s for s in syllabus if s.get("id") == "cbse-12-history-2027")
        hist_typo = hist12["question_paper_design"]["typology"]
        self.assertEqual(len(hist_typo), 5)
        self.assertEqual(sum(t["marks"] for t in hist_typo), 80)
        self.assertEqual(hist_typo[0]["marks"], 21) # Section A MCQ
        self.assertEqual(hist_typo[1]["marks"], 18) # Section B SA
        self.assertEqual(hist_typo[2]["marks"], 24) # Section C LA
        self.assertEqual(hist_typo[3]["marks"], 12) # Section D Source
        self.assertEqual(hist_typo[4]["marks"], 5)  # Section E Map

        res_hist = self.client.get("/cbse/syllabus/cbse-12-history-2027")
        html_hist = res_hist.data.decode("utf-8")
        self.assertIn("Section A: Multiple Choice Questions (MCQ)", html_hist)
        self.assertIn("Section B: Short Answer Type (SA)", html_hist)
        self.assertIn("Section C: Long Answer Type (LA)", html_hist)
        self.assertIn("Section D: Source-Based Questions", html_hist)
        self.assertIn("Section E: Map-Based Work", html_hist)

        # 7. Class 12 Accountancy (055) Practical: Project File 12M, Viva Voce 8M (Total 20M)
        acc12 = next(s for s in syllabus if s.get("id") == "cbse-12-accountancy-2027")
        acc_breakdown = acc12["practical_guidance"]["breakdown"]
        self.assertEqual(len(acc_breakdown), 2)
        self.assertEqual(acc_breakdown[0]["item"], "Project File")
        self.assertEqual(acc_breakdown[0]["marks"], 12)
        self.assertEqual(acc_breakdown[1]["item"], "Viva Voce")
        self.assertEqual(acc_breakdown[1]["marks"], 8)
        self.assertEqual(sum(b["marks"] for b in acc_breakdown), 20)

        res_acc = self.client.get("/cbse/syllabus/cbse-12-accountancy-2027")
        html_acc = res_acc.data.decode("utf-8")
        self.assertIn("Project File", html_acc)
        self.assertIn("12 Marks", html_acc)
        self.assertIn("Viva Voce", html_acc)
        self.assertIn("8 Marks", html_acc)
        self.assertNotIn("Written Test (One Hour)", html_acc)

        # 8. Class 12 Computer Science (083): Explicitly labeled as StudySignal editorial estimate
        cs12 = next(s for s in syllabus if s.get("id") == "cbse-12-computer-science-2027")
        self.assertTrue(cs12["question_paper_design"].get("is_editorial_estimate"))
        self.assertIn("CBSE does not publish an official cognitive percentage table", cs12["question_paper_design"].get("editorial_notice", ""))

        res_cs = self.client.get("/cbse/syllabus/cbse-12-computer-science-2027")
        html_cs = res_cs.data.decode("utf-8")
        self.assertIn("Estimated Question Paper Typology", html_cs)
        self.assertIn("StudySignal Editorial Estimate (Non-Official)", html_cs)
        self.assertIn("CBSE does not publish an official cognitive percentage table for Computer Science", html_cs)

    def test_privacy_policy_transparency_and_disclosures(self):
        """Test privacy policy disclosures, cookie-free status, ad disablement, and updated portal transparency"""
        # 1. Privacy Policy verification
        res_privacy = self.client.get("/privacy-policy")
        self.assertEqual(res_privacy.status_code, 200)
        html_privacy = res_privacy.data.decode("utf-8")

        # Must accurately disclose cookie-free status, analytics, and advertising
        self.assertIn("cookie-free", html_privacy)
        self.assertIn("No Tracking or Session Cookies", html_privacy)
        self.assertIn("No Analytics Scripts", html_privacy)
        self.assertIn("completely disabled", html_privacy)
        self.assertIn("Third-Party Advertising Status", html_privacy)

        # Minor student protections & DPDPA statutory notice
        self.assertIn("Children's and Minor Students' Privacy", html_privacy)
        self.assertIn("Digital Personal Data Protection Act, 2023", html_privacy)
        self.assertIn("Secondary (Class 10) and Senior Secondary (Class 12) students", html_privacy)

        # Must not contain obsolete or misleading claims
        self.assertNotIn("under the age of 13", html_privacy, "US COPPA age limit must not be used")
        self.assertNotIn("COPPA", html_privacy)
        self.assertNotIn("uses standard browser cookies", html_privacy)

        # 2. About page terminology
        res_about = self.client.get("/about")
        self.assertEqual(res_about.status_code, 200)
        html_about = res_about.data.decode("utf-8")
        self.assertIn("independent, free-access educational information portal", html_about)
        self.assertIn("Independent, Free-Access Approach", html_about)
        self.assertNotIn("Non-Commercial &amp; Accessible Approach", html_about)
        self.assertNotIn("Non-Commercial & Accessible Approach", html_about)

        # 3. Disclaimer page terminology and non-affiliation preservation
        res_disclaimer = self.client.get("/disclaimer")
        self.assertEqual(res_disclaimer.status_code, 200)
        html_disclaimer = res_disclaimer.data.decode("utf-8")
        self.assertIn("Strict Non-Affiliation Declaration", html_disclaimer)
        self.assertIn("independent, free-access educational information portal", html_disclaimer)
        self.assertIn("nominative, descriptive, and educational capacity", html_disclaimer)
        self.assertNotIn("non-commercial educational information website", html_disclaimer)
        self.assertNotIn("non-commercial educational capacity", html_disclaimer)

        # 4. Global disclaimer and footer terminology (non-commercial replaced with independent, free-access)
        self.assertNotIn("non-commercial", Config.OFFICIAL_DISCLAIMER.lower())
        self.assertIn("independent, free-access", Config.OFFICIAL_DISCLAIMER.lower())

        res_home = self.client.get("/")
        html_home = res_home.data.decode("utf-8")
        self.assertNotIn("non-commercial", html_home.lower())
        self.assertIn("independent, free-access educational information platform", html_home.lower())
        self.assertIn("Independent Portal Notice", html_home)

    # =========================================================================
    # Stage 2 Phase 2: Date-Sheet Usability & Circular Schema Tests
    # =========================================================================

    def test_datesheet_improved_empty_state_and_last_checked(self):
        """Verify date-sheet page provides rich guidance, explicit last-checked date, and authentic checklist when timetables are pending"""
        orig_demo = getattr(Config, "SHOW_DEMO_DATA", False)
        try:
            Config.SHOW_DEMO_DATA = False
            res = self.client.get("/cbse/datesheets")
            self.assertEqual(res.status_code, 200)
            html = res.data.decode("utf-8")

            # 1. Explicit last-checked status from data file (never dynamically generated today)
            self.assertIn("Official cbse.gov.in portal verified: 26 October 2026", html)
            self.assertIn("Timetable Pending Announcement", html)

            # 2. Both Class 10 & 12 sections display status awaiting press release
            self.assertIn("Class 10 Schedule Status:", html)
            self.assertIn("Class 12 Schedule Status:", html)
            self.assertIn("Awaiting official press release from the Controller of Examinations", html)

            # 3. Authentic verification instructions (3-column guide)
            self.assertIn("1. Checking Official Releases", html)
            self.assertIn("2. Spotting Fake Timetables", html)
            self.assertIn("3. Official Sample Papers", html)
            self.assertIn("cbse.gov.in/cbsenew/examination_Circular.html", html)
            self.assertIn("CBSE Academic Portal", html)

            # 4. Distinctly labeled independent preparation guidance
            self.assertIn("💡 Independent Preparation Guidance (Non-Official / Non-Statutory)", html)
            self.assertIn("Class 10 Core Focus:", html)
            self.assertIn("Science Stream:", html)
            self.assertIn("Commerce Stream:", html)
            self.assertIn("Arts / Humanities:", html)

            # 5. Clean separation: no unannounced speculative exam dates
            self.assertNotIn("[PROTOTYPE / NON-OFFICIAL DEMO ROW]", html)
        finally:
            Config.SHOW_DEMO_DATA = orig_demo

    def test_circular_schema_validation(self):
        """Validate circulars.json schema: required fields, valid status, ISO date formats, and explicit uncertainty"""
        from datetime import datetime
        filepath = os.path.join(app.root_path, "data", "circulars.json")
        with open(filepath, "r", encoding="utf-8") as f:
            circulars = json.load(f)

        self.assertGreaterEqual(len(circulars), 6)

        required_keys = [
            "id", "title", "category", "class_target", "circular_no",
            "summary", "verification_status", "official_url", "source_portal", "status"
        ]

        for c in circulars:
            for k in required_keys:
                self.assertIn(k, c, f"Missing required key '{k}' in circular {c.get('id')}")

            # Status must be valid
            self.assertIn(c.get("status"), ["active", "archived", "demo"], f"Invalid status in {c.get('id')}")

            # Official URLs must start with HTTPS and point to CBSE domains
            self.assertTrue(c["official_url"].startswith("https://"), f"URL must be HTTPS: {c['official_url']}")
            self.assertTrue(
                "cbse.gov.in" in c["official_url"] or "cbseacademic.nic.in" in c["official_url"],
                f"Official URL must point to CBSE domain: {c['official_url']}"
            )

            # ISO date validation
            iso = c.get("iso_date")
            if iso is not None:
                # Must be YYYY-MM-DD
                parsed = datetime.strptime(iso, "%Y-%m-%d")
                self.assertEqual(iso, parsed.strftime("%Y-%m-%d"))
                # If dated, academic_year should be explicitly set
                self.assertIsNotNone(c.get("academic_year"))
            else:
                # If iso_date is null, verify uncertainty is handled explicitly (continuous directory or demo)
                self.assertTrue(
                    c.get("verification_status") in ["official_directory", "demo"],
                    f"Null iso_date only allowed for official_directory or demo, got {c.get('id')}"
                )

    def test_circular_chronological_sorting_and_null_handling(self):
        """Verify get_circulars sorts dated notices in descending order and places undated directories afterwards"""
        from app import get_circulars

        orig_demo = getattr(Config, "SHOW_DEMO_DATA", False)
        try:
            Config.SHOW_DEMO_DATA = False
            items = get_circulars()
            self.assertEqual(len(items), 6)

            # First 4 must be dated notices sorted newest to oldest
            dated_items = [c for c in items if c.get("iso_date") is not None]
            self.assertEqual(len(dated_items), 4)

            expected_dates = ["2026-10-26", "2026-10-21", "2026-10-13", "2026-10-07"]
            actual_dates = [c.get("iso_date") for c in dated_items]
            self.assertEqual(actual_dates, expected_dates)

            # 26 Oct Acad-68 notice must be first
            self.assertEqual(items[0].get("id"), "circ-acad-68-2026")
            self.assertIn("Acad-68/2026", items[0].get("circular_no"))

            # 21 Oct LOC notice must be second
            self.assertEqual(items[1].get("id"), "circ-exam-loc-reminder-2026")
            self.assertIn("Reminder 6 / LOC-2026", items[1].get("circular_no"))

            # Undated directories must follow after dated notices, not before them
            undated_items = [c for c in items if c.get("iso_date") is None]
            self.assertEqual(len(undated_items), 2)
            for d in undated_items:
                self.assertEqual(d.get("verification_status"), "official_directory")

            # Check homepage rendering: latest 4 circulars are the 4 dated notices
            res = self.client.get("/")
            html = res.data.decode("utf-8")
            self.assertIn("Reminder: Submission of List of Candidates", html)
            self.assertIn("Observance of Vigilance Awareness Week", html)
            self.assertIn("CBSE Science Challenge", html)
            self.assertIn("Online Examination Forms Submission for Private Candidates", html)
        finally:
            Config.SHOW_DEMO_DATA = orig_demo

    def test_circular_acad_68_date_and_inconclusive_verification_labels(self):
        """Verify Acad-68 corrected date and ensure inconclusive/unverified records are never falsely labeled as verified"""
        import json
        from unittest.mock import patch

        # 1. Verify Acad-68 in data/circulars.json has the audited date
        with open("data/circulars.json", "r", encoding="utf-8") as f:
            circulars = json.load(f)
        acad68 = next((c for c in circulars if c.get("id") == "circ-acad-68-2026"), None)
        self.assertIsNotNone(acad68)
        self.assertEqual(acad68.get("published_date"), "26 October 2026")
        self.assertEqual(acad68.get("iso_date"), "2026-10-26")
        self.assertEqual(acad68.get("verification_status"), "verified_official")

        # 2. Check circulars page renders the corrected date
        res = self.client.get("/cbse/circulars")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Published: 26 October 2026", html)
        self.assertNotIn("Published: 14 October 2026", html)

        # 3. Test verification labels for inconclusive or unverified notices
        # Construct a synthetic circular with inconclusive status
        inconclusive_sample = [
            {
                "id": "circ-test-inconclusive",
                "title": "Pending Verification Notice for Board Coordinators",
                "category": "Examination",
                "class_target": "Classes 10 & 12",
                "academic_year": "2026-27",
                "published_date": "25 October 2026",
                "iso_date": "2026-10-25",
                "last_verified": "2026-10-27",
                "circular_no": "Coord/Test/2026",
                "summary": "This notice is awaiting conclusive content verification.",
                "verification_status": "inconclusive",
                "is_official": True,
                "is_demo": False,
                "status": "active",
                "official_url": "https://www.cbse.gov.in/cbsenew/documents/test.pdf",
                "source_portal": "https://www.cbse.gov.in"
            }
        ]

        with patch("app.get_circulars", return_value=inconclusive_sample), \
             patch("app.get_up_circulars", return_value=[]), \
             patch("app.get_icse_circulars", return_value=[]):
            res_circ = self.client.get("/cbse/circulars")
            html_circ = res_circ.data.decode("utf-8")
            self.assertIn("Verification Inconclusive", html_circ)
            self.assertIn("Document Content Pending Verification", html_circ)
            # Crucially: it must NOT have verified labels
            self.assertNotIn("✓ Verified Official Notice", html_circ)
            self.assertNotIn("✓ Verified against Official CBSE Source", html_circ)

            res_home = self.client.get("/")
            html_home = res_home.data.decode("utf-8")
            self.assertIn("Verification Inconclusive", html_home)
            self.assertIn("Document Content Pending Verification", html_home)
            self.assertNotIn("✓ Verified Official Notice", html_home)
            self.assertNotIn("✓ Verified on cbseacademic.nic.in", html_home)

    def test_phase_3c_adsense_readiness_remediations(self):
        """Verify Phase 3C remediations: date-sheet production badges, canonical URLs, sitemap pruning, privacy disclosures"""
        import xml.etree.ElementTree as ET

        # 1. Date-sheet production status: no DEMO badge, rendered pending status
        orig_demo = Config.SHOW_DEMO_DATA
        try:
            Config.SHOW_DEMO_DATA = False
            res_ds = self.client.get("/cbse/datesheets")
            self.assertEqual(res_ds.status_code, 200)
            html_ds = res_ds.data.decode("utf-8")
            self.assertNotIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html_ds)
            self.assertIn("Official Timetable Pending", html_ds)

            # Fact-checked exam day instructions
            self.assertIn("CBSE Standard Examination Day Guidelines (Reference Protocols)", html_ds)
            self.assertIn("Centre Entry Protocol:", html_ds)
            self.assertIn("Mandatory Documents:", html_ds)
            self.assertIn("Question Paper Reading Window:", html_ds)
            self.assertIn("Prohibited Materials:", html_ds)
        finally:
            Config.SHOW_DEMO_DATA = orig_demo

        # 2. Canonical URLs in templates must never leak 127.0.0.1 or localhost
        for path in ["/", "/cbse/class-10", "/cbse/class-12", "/cbse/datesheets", "/cbse/circulars", "/about", "/contact", "/privacy-policy"]:
            res = self.client.get(path)
            self.assertEqual(res.status_code, 200)
            html = res.data.decode("utf-8")
            self.assertIn('<link rel="canonical" href="https://exampulse-india.onrender.com', html)
            self.assertNotIn('<link rel="canonical" href="http://127.0.0.1', html)
            self.assertNotIn('<link rel="canonical" href="http://localhost', html)
            self.assertNotIn('property="og:url" content="http://127.0.0.1', html)

        # 3. Contact page transparency (no unverified GitHub link, honest warning preserved)
        res_contact = self.client.get("/contact")
        self.assertEqual(res_contact.status_code, 200)
        html_contact = res_contact.data.decode("utf-8")
        self.assertNotIn("github.com/lakshya-aaa/EXAMPULSE", html_contact, "Unverified candidate repo must not be published")
        self.assertIn("Message Delivery Advisory:", html_contact)
        self.assertNotIn("24 to 48 business hours", html_contact)

        # 4. Privacy Policy advertising transparency & future disclosures
        res_privacy = self.client.get("/privacy-policy")
        self.assertEqual(res_privacy.status_code, 200)
        html_privacy = res_privacy.data.decode("utf-8")
        self.assertIn("Third-Party Advertising Status & Future Disclosures", html_privacy)
        self.assertIn("completely disabled", html_privacy)
        self.assertIn("adssettings.google.com", html_privacy)
        self.assertIn("aboutads.info/choices", html_privacy)
        self.assertIn("policies.google.com/technologies/ads", html_privacy)

        # 5. Robots meta tag scoped conditioning: unverified records have noindex; verified records preserve base index, follow
        # Unverified subject (Class 10 AI)
        res_ai = self.client.get("/cbse/syllabus/cbse-10-ai-2027")
        self.assertEqual(res_ai.status_code, 200)
        html_ai = res_ai.data.decode("utf-8")
        self.assertIn('<meta name="robots" content="noindex, follow">', html_ai)

        # Verified Class 10 subject (Mathematics)
        res_maths = self.client.get("/cbse/syllabus/cbse-10-maths-2027")
        self.assertEqual(res_maths.status_code, 200)
        html_maths = res_maths.data.decode("utf-8")
        self.assertIn('<meta name="robots" content="index, follow">', html_maths)
        self.assertNotIn("noindex", html_maths)

        # Verified Class 12 subject (Physics)
        res_phys = self.client.get("/cbse/syllabus/cbse-12-physics-2027")
        self.assertEqual(res_phys.status_code, 200)
        html_phys = res_phys.data.decode("utf-8")
        self.assertIn('<meta name="robots" content="index, follow">', html_phys)
        self.assertNotIn("noindex", html_phys)

        # Base template normal robots behavior preserved on core pages
        res_home = self.client.get("/")
        self.assertIn('<meta name="robots" content="index, follow">', res_home.data.decode("utf-8"))

        # 6. Sitemap XML verification
        res_sm = self.client.get("/sitemap.xml")
        self.assertEqual(res_sm.status_code, 200)
        root = ET.fromstring(res_sm.data.decode("utf-8"))
        ns = {"ns": "http://www.sitemaps.org/schemas/sitemap/0.9"}
        url_nodes = root.findall(".//ns:url", ns)

        # Build map of loc -> (priority, changefreq, lastmod)
        sitemap_map = {}
        for node in url_nodes:
            loc = node.find("ns:loc", ns).text
            prio = node.find("ns:priority", ns).text if node.find("ns:priority", ns) is not None else None
            freq = node.find("ns:changefreq", ns).text if node.find("ns:changefreq", ns) is not None else None
            lastmod = node.find("ns:lastmod", ns).text if node.find("ns:lastmod", ns) is not None else None
            sitemap_map[loc] = (prio, freq, lastmod)

        # cbse-10-ai-2027 must NOT be in sitemap
        self.assertFalse(any("cbse-10-ai-2027" in loc for loc in sitemap_map))

        # Check removed historical archive records are NOT in sitemap
        hist_maths_url = "https://exampulse-india.onrender.com/cbse/syllabus/cbse-10-maths-2025"
        self.assertNotIn(hist_maths_url, sitemap_map)

        # Check current verified record has priority 0.7 and monthly changefreq
        curr_maths_url = "https://exampulse-india.onrender.com/cbse/syllabus/cbse-10-maths-2027"
        self.assertIn(curr_maths_url, sitemap_map)
        self.assertEqual(sitemap_map[curr_maths_url][0], "0.7")
        self.assertEqual(sitemap_map[curr_maths_url][1], "monthly")

        # Check static legal page has NO invented current-date lastmod
        terms_url = "https://exampulse-india.onrender.com/terms"
        self.assertIn(terms_url, sitemap_map)
        self.assertIsNone(sitemap_map[terms_url][2], "Terms page should omit lastmod if not explicitly tracked")

    def test_studysignal_brand_assets_and_clean_references(self):
        """Verify StudySignal SVG assets are served correctly and templates reference them"""
        # 1. Test logo SVG asset
        res_logo = self.client.get("/static/images/studysignal-logo.svg")
        self.assertEqual(res_logo.status_code, 200)
        self.assertIn("image/svg+xml", res_logo.content_type)
        self.assertIn("StudySignal", res_logo.data.decode("utf-8"))
        res_logo.close()

        # 2. Test icon SVG asset
        res_icon = self.client.get("/static/images/studysignal-icon.svg")
        self.assertEqual(res_icon.status_code, 200)
        self.assertIn("image/svg+xml", res_icon.content_type)
        self.assertIn("StudySignal icon", res_icon.data.decode("utf-8"))
        res_icon.close()

        # 3. Test base.html rendered output links to the assets
        res_home = self.client.get("/")
        html = res_home.data.decode("utf-8")
        self.assertIn("/static/images/studysignal-logo.svg", html)
        self.assertIn("/static/images/studysignal-icon.svg", html)
        self.assertIn('alt="StudySignal"', html)

        # 4. Ensure old brand text is not rendered on core pages
        for path in ["/", "/about", "/contact", "/disclaimer", "/privacy-policy", "/terms"]:
            page = self.client.get(path)
            self.assertNotIn("ExamPulse India", page.data.decode("utf-8"), f"Old brand 'ExamPulse India' leaked in {path}")

    def test_studysignal_css_brand_palette_and_footer_logo(self):
        """Verify StudySignal CSS variables, color contrast, and footer logo styling"""
        res_css = self.client.get("/static/css/style.css")
        self.assertEqual(res_css.status_code, 200)
        css_text = res_css.data.decode("utf-8")
        res_css.close()

        # Primary brand colors from logo
        self.assertIn("--brand-blue: #2424F5", css_text)
        self.assertIn("--brand-blue-light: #3A4BFF", css_text)
        self.assertIn("--brand-yellow: #FFD166", css_text)
        self.assertIn("--brand-yellow-gold: #F5A300", css_text)
        self.assertIn("--bg-dark-midnight: #0A0F24", css_text)
        self.assertIn("--bg-dark-deep: #050814", css_text)

        # Ensure old brand saffron/orange does not linger
        self.assertNotIn("#ff9933", css_text)
        self.assertNotIn("#e65100", css_text)

        # Official CBSE warning/disclaimer preserved
        self.assertIn(".official-disclaimer-banner", css_text)
        self.assertIn(".demo-table-alert", css_text)

        # Footer logo outline and glow protection
        self.assertIn(".footer-logo", css_text)
        self.assertIn("outline: none;", css_text)
        self.assertIn("box-shadow: none;", css_text)
        self.assertIn("filter: none;", css_text)

    def test_pyq_page_route_navigation_and_filters(self):
        """Phase 2: Verify /cbse/pyq route accessibility, navigation links, and filter form rendering"""
        # 1. Main PYQ page returns 200 OK
        res = self.client.get("/cbse/pyq")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("CBSE Previous Year Question Papers (PYQ Library)", html)
        self.assertIn("StudySignal", html)
        self.assertNotIn("ExamPulse India", html)

        # 2. Main navigation contains PYQ link and marks it active
        self.assertIn('href="/cbse/pyq" class="nav-link active"', html)
        self.assertIn('href="/cbse/pyq" class="active"', html)  # mobile drawer active

        # 3. /pyq redirects to /cbse/pyq
        res_redir = self.client.get("/pyq")
        self.assertEqual(res_redir.status_code, 301)
        self.assertTrue(res_redir.location.endswith("/cbse/pyq"))

        # 4. Filter form is present with class, subject, and year inputs
        self.assertIn('<form action="/cbse/pyq"', html)
        self.assertIn('name="class"', html)
        self.assertIn('name="subject"', html)
        self.assertIn('name="year"', html)
        self.assertIn('name="availability"', html)

    def test_pyq_filtering_by_class_subject_year_and_empty_state(self):
        """Phase 2: Verify class, subject, year filtering and empty state handling"""
        # 1. Filter by Class 10
        res_c10 = self.client.get("/cbse/pyq?class=10")
        self.assertEqual(res_c10.status_code, 200)
        html_c10 = res_c10.data.decode("utf-8")
        self.assertIn("Class 10", html_c10)
        self.assertNotIn("Senior School Certificate Examination", html_c10)

        # 2. Filter by Class 12
        res_c12 = self.client.get("/cbse/pyq?class=12")
        self.assertEqual(res_c12.status_code, 200)
        html_c12 = res_c12.data.decode("utf-8")
        self.assertIn("Class 12", html_c12)
        self.assertIn("Senior School Certificate Examination", html_c12)

        # 3. Filter by Year 2024
        res_2024 = self.client.get("/cbse/pyq?year=2024")
        self.assertEqual(res_2024.status_code, 200)
        html_2024 = res_2024.data.decode("utf-8")
        self.assertIn("2024 Exam", html_2024)

        # 4. Filter by specific subject (Physics)
        res_phys = self.client.get("/cbse/pyq?subject=Physics")
        self.assertEqual(res_phys.status_code, 200)
        html_phys = res_phys.data.decode("utf-8")
        self.assertIn('<h3 class="pyq-card-title">Physics</h3>', html_phys)
        self.assertNotIn('<h3 class="pyq-card-title">Biology</h3>', html_phys)
        self.assertNotIn('<h3 class="pyq-card-title">Accountancy</h3>', html_phys)

        # 5. Empty state when no papers match
        res_empty = self.client.get("/cbse/pyq?q=NonExistentSubject999")
        self.assertEqual(res_empty.status_code, 200)
        html_empty = res_empty.data.decode("utf-8")
        self.assertIn("No Question Papers Match Your Filters", html_empty)
        self.assertIn("Reset All Filters", html_empty)
        self.assertIn('href="/cbse/pyq"', html_empty)

    def test_pyq_availability_integrity_and_no_fake_links(self):
        """Phase 2: Verify authentic links for available papers and proper unavailable handling without fake links"""
        res = self.client.get("/cbse/pyq")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # Available papers must point to authentic cbse.gov.in zip archives
        self.assertIn("https://www.cbse.gov.in/cbsenew/question-paper/2024/X/MATHEMATICS_STANDARD.zip", html)
        self.assertIn("https://www.cbse.gov.in/cbsenew/question-paper/2024/XII/PHYSICS.zip", html)
        self.assertIn("Download Official Paper", html)

        # Unavailable papers must show disabled button and clear status
        self.assertIn("Paper Unavailable", html)
        self.assertIn("Pending Release", html)
        self.assertIn("disabled", html)

        # Test filter for unavailable only
        res_unavail = self.client.get("/cbse/pyq?availability=unavailable")
        self.assertEqual(res_unavail.status_code, 200)
        html_unavail = res_unavail.data.decode("utf-8")
        self.assertIn("Paper Unavailable", html_unavail)
        self.assertNotIn("Download Official Paper", html_unavail)
        self.assertNotIn("Download All Sets", html_unavail)

    def test_pyq_2025_entries_and_official_links(self):
        """Phase 2: Verify 2025 examination question papers are present, available, and have authentic official URLs"""
        res_2025 = self.client.get("/cbse/pyq?year=2025")
        self.assertEqual(res_2025.status_code, 200)
        html_2025 = res_2025.data.decode("utf-8")

        # 2025 Exam badge present
        self.assertIn("2025 Exam", html_2025)

        # Class 10 & 12 2025 official CBSE links
        self.assertIn("https://www.cbse.gov.in/cbsenew/question-paper/2025/X/041_Mathematics_Standard.zip", html_2025)
        self.assertIn("https://www.cbse.gov.in/cbsenew/question-paper/2025/X/086_Science.zip", html_2025)
        self.assertIn("https://www.cbse.gov.in/cbsenew/question-paper/2025/XII/PHYSICS.zip", html_2025)
        self.assertIn("https://www.cbse.gov.in/cbsenew/question-paper/2025/XII/CHEMISTRY.zip", html_2025)
        self.assertIn("https://www.cbse.gov.in/cbsenew/question-paper/2025/XII/ACCOUNTANCY.zip", html_2025)

    def test_pyq_multiple_sets_representation_and_individual_sets(self):
        """Phase 2: Verify clear representation of multi-set ZIP archives vs individual set PDF files"""
        # 1. Multi-set ZIP packages show multi-set badge and download all sets button
        res_2025 = self.client.get("/cbse/pyq?year=2025&subject=Mathematics+Standard")
        self.assertEqual(res_2025.status_code, 200)
        html_mset = res_2025.data.decode("utf-8")
        self.assertIn("Multi-Set ZIP", html_mset)
        self.assertIn("Download All Sets", html_mset)
        self.assertIn("ZIP Archive", html_mset)

        # 2. 2015 individual sets are listed with specific set identifiers
        res_2015 = self.client.get("/cbse/pyq?year=2015&subject=English+Language+%26+Literature")
        self.assertEqual(res_2015.status_code, 200)
        html_2015 = res_2015.data.decode("utf-8")
        self.assertIn("Delhi Region - Set 1", html_2015)
        self.assertIn("Delhi Region - Set 2", html_2015)
        self.assertIn("Outside Delhi Region - Set 1", html_2015)
        self.assertIn("PDF Document", html_2015)

    def test_pyq_missing_and_cancelled_years_handling(self):
        """Phase 2: Verify transparent handling of 2021 (COVID-19 cancelled) and 2019/2014 (not hosted in online archive)"""
        # 1. 2021 COVID cancellation
        res_2021 = self.client.get("/cbse/pyq?year=2021")
        self.assertEqual(res_2021.status_code, 200)
        html_2021 = res_2021.data.decode("utf-8")
        self.assertIn("cancelled nationwide due to the COVID-19 pandemic", html_2021)
        self.assertIn("Paper Unavailable", html_2021)

        # 2. 2019 CBSE online archive status
        res_2019 = self.client.get("/cbse/pyq?year=2019")
        self.assertEqual(res_2019.status_code, 200)
        html_2019 = res_2019.data.decode("utf-8")
        self.assertIn("not hosted in the CBSE online download repository", html_2019)
        self.assertIn("Paper Unavailable", html_2019)

        # 3. 2014 CBSE online archive status
        res_2014 = self.client.get("/cbse/pyq?year=2014")
        self.assertEqual(res_2014.status_code, 200)
        html_2014 = res_2014.data.decode("utf-8")
        self.assertIn("not hosted in the CBSE online download repository", html_2014)
        self.assertIn("Paper Unavailable", html_2014)

    def test_pyq_source_links_and_verified_dates(self):
        """Phase 2: Verify source portal links and checked/verified dates across records"""
        res = self.client.get("/cbse/pyq?year=2025")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Verified:", html)
        self.assertIn("2026-11-01", html)
        self.assertIn("Source Archive", html)

    # -------------------------------------------------------------
    # Multi-Board & Competitive Exam Expansion Tests
    # -------------------------------------------------------------

    def test_boards_hub_route_and_contents(self):
        """Verify /boards directory displays active CBSE, in-development ICSE, and coming soon items without IBPS"""
        res = self.client.get("/boards")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # 1. Page Header & Structure
        self.assertIn("Educational Boards &amp; Competitive Examinations", html)
        self.assertIn("School Education Boards", html)
        self.assertIn("National Competitive Examinations", html)

        # 2. CBSE is Active and fully clickable
        self.assertIn("CBSE", html)
        self.assertIn("Central Board of Secondary Education", html)
        self.assertIn("Active", html)
        self.assertIn('href="/cbse/class-10"', html)
        self.assertIn('href="/cbse/class-12"', html)
        self.assertIn('href="/cbse/pyq"', html)

        # 3. ICSE is In Development with link to /icse
        self.assertIn("ICSE", html)
        self.assertIn("Council for the Indian School Certificate Examinations", html)
        self.assertIn("In Development", html)
        self.assertIn('href="/icse"', html)

        # 4. State Boards are Coming Soon as non-clickable status cards
        self.assertIn("UP Board", html)
        self.assertIn("Uttar Pradesh Madhyamik Shiksha Parishad", html)
        self.assertIn("Bihar Board (BSEB)", html)
        self.assertIn("Bihar School Examination Board", html)
        self.assertIn("Maharashtra Board (MSBSHSE)", html)
        self.assertIn("Maharashtra State Board", html)
        self.assertIn("Coming Soon", html)
        self.assertIn("btn-disabled-soon", html)

        # 5. Competitive Exams are Coming Soon
        self.assertIn("JEE", html)
        self.assertIn("Joint Entrance Examination", html)
        self.assertIn("NEET", html)
        self.assertIn("National Eligibility cum Entrance Test", html)
        self.assertIn("CUET", html)
        self.assertIn("Common University Entrance Test", html)

        # 6. Must NOT include IBPS
        self.assertNotIn("IBPS", html)
        self.assertNotIn("Banking Personnel", html)

    def test_boards_cisce_card_links(self):
        """Verify CISCE card on /boards shows only Class 10 Hub and Class 12 Hub for class portals,
        with redundant ICSE & ISC Hub link removed, and all utility links intact."""
        res = self.client.get("/boards")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # 1. Class portal links
        self.assertIn('<span>Class 10 Hub</span>', html)
        self.assertIn('href="/icse/class-10"', html)
        self.assertIn('<span>Class 12 Hub</span>', html)
        self.assertIn('href="/icse/class-12"', html)

        # 2. Redundant / replaced links removed
        self.assertNotIn('<span>ICSE &amp; ISC Hub</span>', html)
        self.assertNotIn('<span>ICSE & ISC Hub</span>', html)
        self.assertNotIn('<span>ICSE Class 10 Portal</span>', html)
        self.assertNotIn('<span>ISC Class 12 Portal</span>', html)

        # 3. Existing resource links preserved
        self.assertIn('href="/icse/pyq"', html)
        self.assertIn('href="/icse/syllabus"', html)
        self.assertIn('href="/icse/datesheets"', html)
        self.assertIn('href="/icse/circulars"', html)

        # 4. Footer CTA button preserved
        self.assertIn('href="/icse"', html)

    def test_cbse_hub_route_and_contents(self):
        """Verify dedicated /cbse Board Examination Hub loads with verified content,
        quick navigation, course level cards pointing to class-10 & class-12 hubs,
        and legal disclaimer without fake data."""
        res = self.client.get("/cbse")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # 1. Page Header & Academic Branding
        self.assertIn("CBSE Board Examination Hub", html)
        self.assertIn("Active Board Portal", html)
        self.assertIn("Session 2026-27", html)

        # 2. Class portal links point to existing CBSE hubs
        self.assertIn('href="/cbse/class-10"', html)
        self.assertIn('href="/cbse/class-12"', html)

        # 3. Existing CBSE sections navigation
        self.assertIn('href="/cbse/syllabus"', html)
        self.assertIn('href="/cbse/datesheets"', html)
        self.assertIn('href="/cbse/circulars"', html)
        self.assertIn('href="/cbse/pyq"', html)

        # 4. Official CBSE source links
        self.assertIn("cbse.gov.in", html)
        self.assertIn("cbseacademic.nic.in", html)

        # 5. Non-affiliation disclaimer
        self.assertIn("CBSE Non-Affiliation Legal Notice", html)

        # 6. Cross-bridge to CISCE
        self.assertIn('href="/icse"', html)

    def test_boards_cbse_card_cta_points_to_cbse(self):
        """Verify on /boards that 'Explore CBSE Portal' points to /cbse,
        and class portal links still point to /cbse/class-10 and /cbse/class-12."""
        res = self.client.get("/boards")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # Explore CBSE Portal CTA button
        self.assertIn('href="/cbse"', html)
        # Class Hub links within CBSE card
        self.assertIn('href="/cbse/class-10"', html)
        self.assertIn('href="/cbse/class-12"', html)

    def test_icse_hub_route_and_integrity(self):
        """Verify /icse dedicated board hub has Active status, verified CISCE links, and complete portal navigation"""
        res = self.client.get("/icse")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # 1. Active board status
        self.assertIn("Active Board Portal", html)
        self.assertIn("ICSE &amp; ISC Board Examination Hub", html)

        # 2. Integrity policy: No unverified content
        self.assertIn("StudySignal Academic Verification Policy for CISCE", html)
        self.assertIn("does not publish unverified curriculum files", html)

        # 3. Dedicated sub-route links
        self.assertIn('href="/icse/class-10"', html)
        self.assertIn('href="/icse/class-12"', html)
        self.assertIn('href="/icse/syllabus"', html)
        self.assertIn('href="/icse/datesheets"', html)
        self.assertIn('href="/icse/circulars"', html)
        self.assertIn('href="/icse/pyq"', html)

        # 4. Verified official CISCE portal links
        self.assertIn("https://cisce.org", html)
        self.assertIn("https://cisce.org/regulations-and-syllabuses/", html)

        # 5. Active CBSE bridge callout & Non-affiliation legal notice
        self.assertIn("Looking for CBSE Resources?", html)
        self.assertIn("CISCE Non-Affiliation Legal Notice", html)

    def test_icse_class_hubs(self):
        """Verify ICSE Class 10 and ISC Class 12 portals"""
        # Class 10
        res_10 = self.client.get("/icse/class-10")
        self.assertEqual(res_10.status_code, 200)
        html_10 = res_10.data.decode("utf-8")
        self.assertIn("ICSE Class 10 (Secondary)", html_10)
        self.assertIn("Mathematics", html_10)
        self.assertIn("Physics", html_10)
        self.assertIn("Examination Schedule &amp; Timetable Status", html_10)
        self.assertIn('href="/icse/pyq?class=10"', html_10)

        # Class 12
        res_12 = self.client.get("/icse/class-12")
        self.assertEqual(res_12.status_code, 200)
        html_12 = res_12.data.decode("utf-8")
        self.assertIn("ISC Class 12 (Higher Secondary)", html_12)
        self.assertIn("Science Stream Subjects", html_12)
        self.assertIn("Commerce Stream Subjects", html_12)
        self.assertIn("Humanities &amp; Arts Electives", html_12)
        self.assertIn('href="/icse/pyq?class=12"', html_12)

    def test_icse_syllabus_directory_and_filters(self):
        """Verify ICSE syllabus directory with class, stream, and query filters"""
        # Main directory
        res = self.client.get("/icse/syllabus")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("ICSE &amp; ISC Subject-wise Syllabus Directory", html)
        self.assertIn("Mathematics", html)

        # Class 10 filter
        res_10 = self.client.get("/icse/syllabus?class=10")
        self.assertEqual(res_10.status_code, 200)
        html_10 = res_10.data.decode("utf-8")
        self.assertIn("icse-10-mathematics-2027", html_10)
        self.assertNotIn("isc-12-physics-2027", html_10)

        # Class 12 filter
        res_12 = self.client.get("/icse/syllabus?class=12")
        self.assertEqual(res_12.status_code, 200)
        html_12 = res_12.data.decode("utf-8")
        self.assertIn("isc-12-physics-2027", html_12)
        self.assertNotIn("icse-10-mathematics-2027", html_12)

        # Stream filter
        res_stream = self.client.get("/icse/syllabus?stream=Science")
        self.assertEqual(res_stream.status_code, 200)
        html_stream = res_stream.data.decode("utf-8")
        self.assertIn("Physics", html_stream)

        # Search query
        res_q = self.client.get("/icse/syllabus?q=physics")
        self.assertEqual(res_q.status_code, 200)
        html_q = res_q.data.decode("utf-8")
        self.assertIn("Physics", html_q)

    def test_icse_syllabus_detail_page(self):
        """Verify ICSE & ISC individual subject syllabus content-first view and 404 behavior"""
        # Valid ICSE subject
        res = self.client.get("/icse/syllabus/icse-10-mathematics-2027")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("ICSE Class 10 Mathematics Syllabus", html)
        self.assertIn("Written Theory Paper", html)
        self.assertIn("Commercial Mathematics", html)
        self.assertIn("Selina Publishers", html)
        self.assertIn("Download Official PDF", html)

        # Valid ISC subject
        res_isc = self.client.get("/icse/syllabus/isc-12-physics-2027")
        self.assertEqual(res_isc.status_code, 200)
        html_isc = res_isc.data.decode("utf-8")
        self.assertIn("ISC Class 12 Physics Syllabus", html_isc)
        self.assertIn("Electrostatics &amp; Current Electricity", html_isc)

        # Non-existent subject returns 404
        res_404 = self.client.get("/icse/syllabus/non-existent-subject-xyz")
        self.assertEqual(res_404.status_code, 404)

    def test_icse_datesheets_view(self):
        """Verify ICSE datesheet tracking view, honest status, and session timings"""
        res = self.client.get("/icse/datesheets")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("ICSE &amp; ISC Examination Timetable Hub", html)
        self.assertIn("Schedule Pending Official Release", html)
        self.assertIn("11:00 AM IST", html)
        self.assertIn("02:00 PM IST", html)
        self.assertIn("https://cisce.org/examination/", html)

        # Filter by class
        res_10 = self.client.get("/icse/datesheets?class=10")
        self.assertEqual(res_10.status_code, 200)
        self.assertIn("ICSE Class 10 (Secondary)", res_10.data.decode("utf-8"))

    def test_icse_circulars_view(self):
        """Verify CISCE circulars & notices directory with filters"""
        res = self.client.get("/icse/circulars")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("CISCE Official Circulars &amp; Academic Notices", html)
        self.assertIn("Official CISCE", html)

        # Filter by category
        res_cat = self.client.get("/icse/circulars?category=Curriculum")
        self.assertEqual(res_cat.status_code, 200)
        self.assertIn("Modern English", res_cat.data.decode("utf-8"))

        # Filter by class
        res_cls = self.client.get("/icse/circulars?class=10")
        self.assertEqual(res_cls.status_code, 200)

    def test_icse_pyq_library_and_filtering(self):
        """Verify ICSE & ISC PYQ library with multi-year coverage, filters, and honest states"""
        res = self.client.get("/icse/pyq")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("ICSE &amp; ISC Previous Year Question Paper Library", html)

        # Available paper check (e.g. 2025 or 2024)
        self.assertIn("Official Paper", html)
        self.assertIn("Download Official PDF", html)

        # Filter available only
        res_avail = self.client.get("/icse/pyq?availability=available")
        self.assertEqual(res_avail.status_code, 200)
        self.assertIn("Official Paper", res_avail.data.decode("utf-8"))

        # Filter unavailable only (historical unhosted years)
        res_unavail = self.client.get("/icse/pyq?availability=unavailable")
        self.assertEqual(res_unavail.status_code, 200)
        html_unavail = res_unavail.data.decode("utf-8")
        self.assertIn("Not Hosted Online", html_unavail)
        self.assertIn("Paper Unavailable", html_unavail)

        # Filter by year and class
        res_filter = self.client.get("/icse/pyq?class=10&year=2025")
        self.assertEqual(res_filter.status_code, 200)
        self.assertIn("2025 Exam", res_filter.data.decode("utf-8"))

        # Empty state when filter doesn't match
        res_empty = self.client.get("/icse/pyq?q=nonexistentsearchterm12345xyz")
        self.assertEqual(res_empty.status_code, 200)
        self.assertIn("No Question Papers Match Your Filters", res_empty.data.decode("utf-8"))

    def test_icse_sitemap_entries(self):
        """Verify /sitemap.xml includes all ICSE & ISC section URLs"""
        res = self.client.get("/sitemap.xml")
        self.assertEqual(res.status_code, 200)
        xml = res.data.decode("utf-8")

        self.assertIn("<loc>https://exampulse-india.onrender.com/icse</loc>", xml)
        self.assertIn("<loc>https://exampulse-india.onrender.com/icse/class-10</loc>", xml)
        self.assertIn("<loc>https://exampulse-india.onrender.com/icse/class-12</loc>", xml)
        self.assertIn("<loc>https://exampulse-india.onrender.com/icse/syllabus</loc>", xml)
        self.assertIn("<loc>https://exampulse-india.onrender.com/icse/datesheets</loc>", xml)
        self.assertIn("<loc>https://exampulse-india.onrender.com/icse/circulars</loc>", xml)
        self.assertIn("<loc>https://exampulse-india.onrender.com/icse/pyq</loc>", xml)
        self.assertIn("/icse/syllabus/icse-10-mathematics-2027", xml)

    def test_navigation_boards_and_exams_selector(self):
        """Verify navigation bar dropdown, mobile drawer, and homepage selector section"""
        # 1. Header Desktop Nav has Boards & Exams dropdown
        res_home = self.client.get("/")
        self.assertEqual(res_home.status_code, 200)
        html_home = res_home.data.decode("utf-8")

        self.assertIn('href="/boards"', html_home)
        self.assertIn("Boards &amp; Exams", html_home)
        self.assertIn('href="/icse"', html_home)

        # 2. Homepage selector section exists with boards & competitive exams
        self.assertIn('id="boards-exams"', html_home)
        self.assertIn("Explore Boards &amp; Competitive Examinations", html_home)
        self.assertIn("School Education Boards", html_home)
        self.assertIn("Competitive Examinations", html_home)
        self.assertIn("JEE (Main &amp; Advanced)", html_home)
        self.assertIn("NEET (UG)", html_home)
        self.assertIn("CUET (UG)", html_home)
        self.assertNotIn("IBPS", html_home)

        # 3. Mobile drawer contains Boards & Exams Hub and ICSE
        self.assertIn('href="/boards"', html_home)
        self.assertIn('href="/icse"', html_home)

    def test_sitemap_includes_boards_and_icse(self):
        """Verify /sitemap.xml lists /boards and /icse canonical URLs"""
        res = self.client.get("/sitemap.xml")
        self.assertEqual(res.status_code, 200)
        xml = res.data.decode("utf-8")

        self.assertIn("<loc>https://exampulse-india.onrender.com/boards</loc>", xml)
        self.assertIn("<loc>https://exampulse-india.onrender.com/icse</loc>", xml)

    def test_search_includes_both_cbse_and_icse(self):
        """Verify /search searches across both CBSE and ICSE resources"""
        res = self.client.get("/search?q=mathematics")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        # Should include both CBSE and ICSE Mathematics
        self.assertIn("CBSE Class 10", html)
        self.assertIn("ICSE Class 10", html)
        self.assertNotIn("IBPS", html)

    def test_icse_pyq_details_and_multi_year_integrity(self):
        """Verify ICSE PYQ contains verified years and honest unavailable notes"""
        res = self.client.get("/icse/pyq?year=2025")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("2025 Exam", html)
        self.assertIn("Official Paper", html)

        # Historical year 2014 unavailable note check
        res_2014 = self.client.get("/icse/pyq?year=2014")
        self.assertEqual(res_2014.status_code, 200)
        html_2014 = res_2014.data.decode("utf-8")
        self.assertIn("Not Hosted Online", html_2014)
        self.assertIn("The official CISCE online repository does not host public question paper files", html_2014)

    def test_canonical_and_meta_tags_on_icse_routes(self):
        """Verify canonical URLs and OG preview images on all ICSE routes"""
        routes = [
            "/icse",
            "/icse/class-10",
            "/icse/class-12",
            "/icse/syllabus",
            "/icse/datesheets",
            "/icse/circulars",
            "/icse/pyq",
            "/icse/syllabus/icse-10-mathematics-2027"
        ]
        for route in routes:
            res = self.client.get(route)
            self.assertEqual(res.status_code, 200, f"Route {route} failed")
            html = res.data.decode("utf-8")
            self.assertIn(f'<link rel="canonical" href="https://exampulse-india.onrender.com{route}">', html)
            self.assertIn('<meta property="og:image" content="https://exampulse-india.onrender.com/static/images/og-preview.png">', html)

    def test_syllabus_responsive_layout_and_table_wrappers(self):
        """Verify mobile responsive layout classes, keyboard accessible table wrappers, and scroll hints"""
        res_detail = self.client.get("/cbse/syllabus/cbse-10-maths-2027")
        self.assertEqual(res_detail.status_code, 200)
        html_detail = res_detail.data.decode("utf-8")

        # Responsive grid layout and card wrappers
        self.assertIn('class="syllabus-detail-layout"', html_detail)
        self.assertIn('class="syllabus-detail-main"', html_detail)
        self.assertIn('class="syllabus-detail-sidebar"', html_detail)
        self.assertIn('class="syllabus-detail-card"', html_detail)
        self.assertIn('class="syllabus-detail-title"', html_detail)

        # Content-first syllabus reading containers and secondary PDF download utility
        self.assertIn('class="syllabus-units-container"', html_detail)
        self.assertIn('class="syllabus-unit-block"', html_detail)
        self.assertIn('class="syllabus-chapter-list"', html_detail)
        self.assertIn('class="syllabus-secondary-pdf-bar"', html_detail)

        # Accessible table wrappers with keyboard focus (tabindex=0), role=region, and aria-labels
        self.assertIn('class="table-scroll-hint"', html_detail)
        self.assertIn('role="region"', html_detail)
        self.assertIn('tabindex="0"', html_detail)
        self.assertIn('aria-label="Official Examination Marks Structure Table"', html_detail)
        self.assertIn('aria-label="Official Unit-Wise Marks Distribution Table"', html_detail)
        self.assertIn('aria-label="Question Paper Design & Assessment Typology Table"', html_detail)
        self.assertIn('aria-label="Practical Assessment Framework Table"', html_detail)

        # Prescribed books responsive grid
        self.assertIn('class="prescribed-books-grid"', html_detail)

        # Catalog filter form and counter bar
        res_cat = self.client.get("/cbse/syllabus")
        self.assertEqual(res_cat.status_code, 200)
        html_cat = res_cat.data.decode("utf-8")
        self.assertIn('class="syllabus-filter-form"', html_cat)
        self.assertIn('class="syllabus-count-bar"', html_cat)

    def test_syllabus_current_vs_archive_labeling_and_demarcation(self):
        """Verify historical 2024-25 archive section and cards are removed, showing only current verified content"""
        # Catalog view: only current session content, zero historical archive cards or sections
        res_all = self.client.get("/cbse/syllabus")
        self.assertEqual(res_all.status_code, 200)
        html_all = res_all.data.decode("utf-8")

        self.assertIn("Academic Session 2026-27 (Current)", html_all)
        self.assertNotIn("Historical Curriculum Archives", html_all)
        self.assertNotIn("subject-card-archive", html_all)
        self.assertNotIn("📁 Historical Archive", html_all)
        self.assertNotIn("Archive PDF ↗", html_all)
        self.assertNotIn("2024-25 (Historical Archive)", html_all)

        # Historical detail page must return 404 (archive-only pages removed)
        res_hist_detail = self.client.get("/cbse/syllabus/cbse-10-maths-2025")
        self.assertEqual(res_hist_detail.status_code, 404)

        # Current detail page: must display verified official status
        res_curr_detail = self.client.get("/cbse/syllabus/cbse-10-maths-2027")
        self.assertEqual(res_curr_detail.status_code, 200)
        html_curr_detail = res_curr_detail.data.decode("utf-8")
        self.assertIn("✓ Verified Official CBSE Document", html_curr_detail)
        self.assertNotIn("Historical Archive Document", html_curr_detail)

    def test_css_responsive_table_and_code_wrapping_rules(self):
        """Verify CSS contains necessary overflow prevention rules, wrapping, and table minimum widths"""
        css_path = os.path.join(app.root_path, "static", "css", "style.css")
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()

        # Monospace code and URL wrapping
        self.assertIn("word-break: break-all;", css)
        self.assertIn("overflow-wrap: anywhere;", css)

        # Responsive table container rules
        self.assertIn(".table-responsive {", css)
        self.assertIn("max-width: 100%;", css)
        self.assertIn("-webkit-overflow-scrolling: touch;", css)
        self.assertIn(".table-scroll-hint {", css)

        # Legible table min-width
        self.assertIn("min-width: 560px;", css)

        # Layout and grid responsiveness
        self.assertIn(".syllabus-detail-layout {", css)
        self.assertIn(".syllabus-detail-main {", css)
        self.assertIn("min-width: 0;", css)
        self.assertIn(".syllabus-filter-form {", css)
        self.assertIn(".subject-card-archive {", css)


    def test_complete_blueprint_removal_and_content_first_reading_experience(self):
        """Verify blueprint buttons and links are completely removed across CBSE and ICSE,
        and content-first syllabus reading with secondary PDF links is enforced.
        """
        # 1. CBSE Syllabus Catalog: cards must have "Complete Syllabus ->" and "Official PDF ↗", no "Blueprint"
        res_cbse_cat = self.client.get("/cbse/syllabus")
        self.assertEqual(res_cbse_cat.status_code, 200)
        html_cbse_cat = res_cbse_cat.data.decode("utf-8")
        self.assertIn("Complete Syllabus &rarr;", html_cbse_cat)
        self.assertIn("Official PDF ↗", html_cbse_cat)
        self.assertNotIn(">Blueprint<", html_cbse_cat)
        self.assertNotIn("Blueprint &rarr;", html_cbse_cat)
        self.assertNotIn("Blueprint ↗", html_cbse_cat)

        # 2. CBSE Class Hubs: cards must have "Complete Syllabus ->"
        res_hub10 = self.client.get("/cbse/class-10")
        self.assertEqual(res_hub10.status_code, 200)
        html_hub10 = res_hub10.data.decode("utf-8")
        self.assertIn("Complete Syllabus &rarr;", html_hub10)
        self.assertNotIn(">Blueprint<", html_hub10)
        self.assertNotIn("Blueprint &rarr;", html_hub10)

        # 3. ICSE Syllabus Catalog: cards must have "Complete Syllabus ->" and "Official PDF ↗"
        res_icse_cat = self.client.get("/icse/syllabus")
        self.assertEqual(res_icse_cat.status_code, 200)
        html_icse_cat = res_icse_cat.data.decode("utf-8")
        self.assertIn("Complete Syllabus &rarr;", html_icse_cat)
        self.assertIn("Official PDF ↗", html_icse_cat)
        self.assertNotIn(">Blueprint<", html_icse_cat)
        self.assertNotIn("Blueprint &rarr;", html_icse_cat)

        # 4. CBSE Subject Detail: Content-first unit reading, no blueprint buttons, secondary PDF utility
        res_cbse_detail = self.client.get("/cbse/syllabus/cbse-10-maths-2027")
        self.assertEqual(res_cbse_detail.status_code, 200)
        html_cbse_detail = res_cbse_detail.data.decode("utf-8")
        self.assertNotIn(">Blueprint<", html_cbse_detail)
        self.assertNotIn("Blueprint &rarr;", html_cbse_detail)
        self.assertIn("syllabus-units-container", html_cbse_detail)
        self.assertIn("syllabus-unit-block", html_cbse_detail)
        self.assertIn("syllabus-chapter-list", html_cbse_detail)
        self.assertIn("Number Systems", html_cbse_detail)
        self.assertIn("Algebra", html_cbse_detail)
        self.assertIn("Coordinate Geometry", html_cbse_detail)
        self.assertIn("syllabus-secondary-pdf-bar", html_cbse_detail)
        self.assertIn("Download official PDF", html_cbse_detail)

        # 5. ICSE Subject Detail: Content-first unit reading, no blueprint buttons, secondary PDF utility
        res_icse_detail = self.client.get("/icse/syllabus/icse-10-mathematics-2027")
        self.assertEqual(res_icse_detail.status_code, 200)
        html_icse_detail = res_icse_detail.data.decode("utf-8")
        self.assertNotIn(">Blueprint<", html_icse_detail)
        self.assertNotIn("Blueprint &rarr;", html_icse_detail)
        self.assertIn("syllabus-units-container", html_icse_detail)
        self.assertIn("syllabus-unit-block", html_icse_detail)
        self.assertIn("syllabus-secondary-pdf-bar", html_icse_detail)
        self.assertIn("Download official PDF", html_icse_detail)

        # 6. ISC Subject Detail (Physics)
        res_isc_detail = self.client.get("/icse/syllabus/isc-12-physics-2027")
        self.assertEqual(res_isc_detail.status_code, 200)
        html_isc_detail = res_isc_detail.data.decode("utf-8")
        self.assertIn("syllabus-units-container", html_isc_detail)
        self.assertIn("syllabus-unit-block", html_isc_detail)
        self.assertIn("Electrostatics &amp; Current Electricity", html_isc_detail)
        self.assertIn("syllabus-secondary-pdf-bar", html_isc_detail)

        # 7. Missing detailed unit content notice for subjects pending full digitization
        res_unverified = self.client.get("/cbse/syllabus/cbse-10-ai-2027")
        self.assertEqual(res_unverified.status_code, 200)
        html_unverified = res_unverified.data.decode("utf-8")
        self.assertIn("Curriculum Unit Verification Notice:", html_unverified)
        self.assertIn("pending official verification", html_unverified)


    def test_isc_syllabus_directory_route(self):
        """Verify dedicated ISC Class 12 syllabus directory route (/isc/syllabus)"""
        res = self.client.get("/isc/syllabus")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("ISC Class 12 Subject-wise Syllabus Directory", html)
        self.assertIn("Physics", html)
        self.assertIn("Chemistry", html)
        self.assertIn("Mathematics", html)
        self.assertIn("Complete Syllabus &rarr;", html)
        self.assertIn("Official PDF ↗", html)
        self.assertNotIn("Historical Curriculum Archives", html)


    # -------------------------------------------------------------
    # UP Board (UPMSP) Foundational Onboarding Tests
    # -------------------------------------------------------------

    def test_up_board_hub_active(self):
        """Verify /up-board overview hub has Active status, verified UPMSP links,
        dual-language terminology, confirmed 2027 timetable, and distinct sample papers and question bank links."""
        res = self.client.get("/up-board")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # 1. Active status & branding
        self.assertIn("Active", html)
        self.assertIn("UP Board Examination Hub", html)
        self.assertIn("उत्तर प्रदेश माध्यमिक शिक्षा परिषद्, प्रयागराज (UPMSP)", html)

        # 2. Dual-language class portals
        self.assertIn("हाई स्कूल (High School)", html)
        self.assertIn("इण्टरमीडिएट (Intermediate)", html)
        self.assertIn('href="/up-board/class-10"', html)
        self.assertIn('href="/up-board/class-12"', html)

        # 3. Confirmed 2027 examination timetable
        self.assertIn("Official 2027 Schedule Confirmed", html)
        self.assertIn("05 Feb 2027 to 24 Feb 2027", html)
        self.assertIn("मा०शि०प०/समन्वय/183-7", html)
        self.assertIn("12 October 2026", html)
        self.assertIn("TimeTable_2027_Vigyapti.pdf", html)

        # 4. Verified official sources & links
        self.assertIn("https://upmsp.edu.in", html)
        self.assertIn("Board_Syllabus.aspx", html)
        self.assertIn("Board_ModelPaper.aspx", html)

        # 5. Distinct Sample Papers and Question Bank links
        self.assertIn('href="/up-board/sample-papers"', html)
        self.assertIn('href="/up-board/question-bank"', html)
        self.assertIn("Official Sample Papers", html)
        self.assertIn("Question Bank", html)
        self.assertIn("Verified Subject Syllabi", html)
        self.assertIn("Official Notifications", html)
        self.assertIn("विज्ञप्ति एवं महत्वपूर्ण सूचना", html)

        # 6. Absence of UP Board PYQ references
        self.assertNotIn('/up-board/pyq', html)
        self.assertNotIn("Previous Year Question Papers (PYQs)", html)
        self.assertNotIn("विगत वर्षों के प्रश्न-पत्र", html)

        # 7. Non-affiliation legal disclaimer
        self.assertIn("UPMSP Non-Affiliation Legal Notice", html)
        self.assertIn("NOT affiliated with, endorsed by, or connected to the Uttar Pradesh Madhyamik Shiksha Parishad", html)

    def test_up_board_class_hubs(self):
        """Verify UP Board High School (Class 10) and Intermediate (Class 12) portals with separate sample paper and question bank navigation."""
        # 1. High School (Class 10) Hub
        res10 = self.client.get("/up-board/class-10")
        self.assertEqual(res10.status_code, 200)
        html10 = res10.data.decode("utf-8")
        self.assertIn("UP Board High School (Class 10)", html10)
        self.assertIn("हाईस्कूल (कक्षा 10)", html10)
        self.assertIn("Active", html10)
        self.assertIn("Official 2027 Schedule Confirmed", html10)
        self.assertIn("05 Feb 2027 to 24 Feb 2027", html10)
        self.assertIn("High School Official Syllabi", html10)
        self.assertIn("कोड: 901", html10)
        self.assertIn("कोड: 928", html10)
        self.assertIn("Official Sample Papers / Model Papers", html10)
        self.assertIn('href="/up-board/sample-papers?class=10"', html10)
        self.assertIn('href="/up-board/question-bank"', html10)
        self.assertNotIn('/up-board/pyq', html10)
        self.assertIn("TimeTable_2027_Vigyapti.pdf", html10)

        # 2. Intermediate (Class 12) Hub
        res12 = self.client.get("/up-board/class-12")
        self.assertEqual(res12.status_code, 200)
        html12 = res12.data.decode("utf-8")
        self.assertIn("UP Board Intermediate (Class 12)", html12)
        self.assertIn("इण्टरमीडिएट (कक्षा 12)", html12)
        self.assertIn("Active", html12)
        self.assertIn("Official 2027 Schedule Confirmed", html12)
        self.assertIn("05 Feb 2027 to 24 Feb 2027", html12)
        self.assertIn("Intermediate Official Syllabi", html12)
        self.assertIn("कोड: 101", html12)
        self.assertIn("कोड: 151", html12)
        self.assertIn("विज्ञान वर्ग", html12)
        self.assertIn("मानविकी व कला वर्ग", html12)
        self.assertIn("वाणिज्य वर्ग", html12)
        self.assertIn("कृषि वर्ग", html12)
        self.assertIn("Official Sample Papers / Model Papers", html12)
        self.assertIn('href="/up-board/sample-papers?class=12"', html12)
        self.assertIn('href="/up-board/question-bank"', html12)
        self.assertNotIn('/up-board/pyq', html12)

    def test_up_board_subroutes_status_views(self):
        """Verify dedicated views for datesheets, syllabus, circulars, sample papers, question bank, and 404 for removed pyq."""
        # 1. Datesheets
        res_ds = self.client.get("/up-board/datesheets")
        self.assertEqual(res_ds.status_code, 200)
        html_ds = res_ds.data.decode("utf-8")
        self.assertIn("Official 2027 Timetable Declared", html_ds)
        self.assertIn("05 February 2027 to 24 February 2027", html_ds)
        self.assertIn("मा०शि०प०/समन्वय/183-7", html_ds)
        self.assertIn("TimeTable_2027_Vigyapti.pdf", html_ds)
        self.assertIn("901 / 902", html_ds)
        self.assertIn("101 / 102", html_ds)

        # 2. Syllabus
        res_syl = self.client.get("/up-board/syllabus")
        self.assertEqual(res_syl.status_code, 200)
        html_syl = res_syl.data.decode("utf-8")
        self.assertIn("UP Board Subject-wise Syllabus Directory", html_syl)
        self.assertIn("सत्र 2026–27 अधिकृत पाठ्यक्रम निर्देशिका", html_syl)
        self.assertIn("कोड: 901", html_syl)
        self.assertIn("कोड: 151", html_syl)
        self.assertIn("https://upmsp.edu.in/Downloads/Syllabus/Class10/901-Hindi-Class-10.pdf", html_syl)

        # 3. Syllabus Search filtering
        res_syl_search = self.client.get("/up-board/syllabus?q=901")
        self.assertEqual(res_syl_search.status_code, 200)
        html_syl_search = res_syl_search.data.decode("utf-8")
        self.assertIn("कोड: 901", html_syl_search)
        self.assertNotIn("कोड: 928", html_syl_search)

        # 4. Circulars
        res_circ = self.client.get("/up-board/circulars")
        self.assertEqual(res_circ.status_code, 200)
        html_circ = res_circ.data.decode("utf-8")
        self.assertIn("UP Board Official Circulars &amp; Notices", html_circ)
        self.assertIn("मा०शि०प०/समन्वय/183-7", html_circ)
        self.assertIn("12 October 2026", html_circ)

        # 5. Dedicated Sample Papers page (/up-board/sample-papers)
        res_sp = self.client.get("/up-board/sample-papers")
        self.assertEqual(res_sp.status_code, 200)
        html_sp = res_sp.data.decode("utf-8")
        self.assertIn("UP Board Official Sample Papers / Model Papers", html_sp)
        self.assertIn("Official Sample Paper", html_sp)
        self.assertIn("High School (Class 10) Sample Papers", html_sp)
        self.assertIn("Intermediate (Class 12) Sample Papers", html_sp)
        self.assertIn("कोड: 901", html_sp)
        self.assertIn("कोड: 151", html_sp)
        self.assertIn("https://upmsp.edu.in/Downloads/ModelPaper/class10/901-Hindi.pdf", html_sp)
        self.assertIn("https://upmsp.edu.in/Downloads/ModelPaper/class12/151-Physics.pdf", html_sp)
        self.assertIn("View PDF ↗", html_sp)
        self.assertIn("Download", html_sp)
        # Must NOT be labeled as PYQ
        self.assertNotIn("Previous Year Question Papers (PYQs)", html_sp)
        self.assertNotIn("विगत वर्षों के प्रश्न-पत्र", html_sp)

        # 6. Sample Papers Search filtering
        res_sp_search = self.client.get("/up-board/sample-papers?q=901")
        self.assertEqual(res_sp_search.status_code, 200)
        html_sp_search = res_sp_search.data.decode("utf-8")
        self.assertIn("कोड: 901", html_sp_search)
        self.assertNotIn("कोड: 928", html_sp_search)

        # 7. Model-papers alias route
        res_mp = self.client.get("/up-board/model-papers")
        self.assertEqual(res_mp.status_code, 200)
        self.assertIn("UP Board Official Sample Papers / Model Papers", res_mp.data.decode("utf-8"))

        # 8. Dedicated Question Bank page (/up-board/question-bank)
        res_qb = self.client.get("/up-board/question-bank")
        self.assertEqual(res_qb.status_code, 200)
        html_qb = res_qb.data.decode("utf-8")
        self.assertIn("UP Board Official Question Bank", html_qb)
        self.assertIn("अधिकृत प्रश्न बैंक", html_qb)
        self.assertIn("Awaiting Official Release", html_qb)
        self.assertIn("कक्षा 9 आधारभूत अधिकृत प्रश्न बैंक", html_qb)
        self.assertIn("https://upmsp.edu.in/Downloads/QuestionBank/901_Hindi.pdf", html_qb)
        # Must NOT be labeled as PYQs
        self.assertNotIn("Previous Year Question Papers (PYQs)", html_qb)

        # 9. Removed PYQ route returns 404
        res_pyq = self.client.get("/up-board/pyq")
        self.assertEqual(res_pyq.status_code, 404)

    def test_boards_up_card_active(self):
        """Verify on /boards that UP Board is marked Active with correct links and updated description."""
        res = self.client.get("/boards")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        self.assertIn("UP Board", html)
        self.assertIn("Uttar Pradesh Madhyamik Shiksha Parishad (UPMSP)", html)
        self.assertIn("Active", html)
        self.assertIn("Explore UP Board Portal &rarr;", html)
        self.assertIn("Comprehensive UP Board resources for High School (Class 10) and Intermediate (Class 12)", html)
        self.assertIn('href="/up-board"', html)
        self.assertIn('href="/up-board/class-10"', html)
        self.assertIn('href="/up-board/class-12"', html)

    def test_sitemap_includes_up_board(self):
        """Verify /sitemap.xml contains UP Board foundational routes including sample-papers and question-bank, and excludes pyq."""
        res = self.client.get("/sitemap.xml")
        self.assertEqual(res.status_code, 200)
        xml = res.data.decode("utf-8")
        self.assertIn("/up-board", xml)
        self.assertIn("/up-board/class-10", xml)
        self.assertIn("/up-board/class-12", xml)
        self.assertIn("/up-board/datesheets", xml)
        self.assertIn("/up-board/sample-papers", xml)
        self.assertIn("/up-board/question-bank", xml)
        self.assertNotIn("/up-board/pyq", xml)

    def test_up_board_data_files_integrity(self):
        """Verify that all populated UP Board records have official URLs, 
        last_verified dates, official UPMSP domains, and correct sample paper and question bank labeling."""
        import json
        # 1. Datesheets
        with open(os.path.join(app.root_path, "data", "up_datesheets.json"), "r", encoding="utf-8") as f:
            ds = json.load(f)
        self.assertEqual(ds["notification_number"], "मा०शि०प०/समन्वय/183-7")
        self.assertEqual(ds["exam_window"], "05 February 2027 to 24 February 2027")
        self.assertTrue(ds["official_timetable_pdf"].startswith("https://upmsp.edu.in"))
        self.assertEqual(len(ds["classes"]["10"]["schedule_items"]), 10)
        self.assertEqual(len(ds["classes"]["12"]["schedule_items"]), 13)

        # 2. Syllabi
        with open(os.path.join(app.root_path, "data", "up_syllabus.json"), "r", encoding="utf-8") as f:
            syl = json.load(f)
        self.assertEqual(len(syl), 21)
        for s in syl:
            self.assertEqual(s["last_verified"], "2026-11-07")
            self.assertTrue(s["official_url"].startswith("https://upmsp.edu.in"))
            self.assertTrue(s["is_official"])

        # 3. Sample Papers (23 verified official papers: 12 Class 10, 11 Class 12)
        with open(os.path.join(app.root_path, "data", "up_sample_papers.json"), "r", encoding="utf-8") as f:
            sp = json.load(f)
        self.assertEqual(len(sp), 23)
        c10_sp = [p for p in sp if p["class"] == "10"]
        c12_sp = [p for p in sp if p["class"] == "12"]
        self.assertEqual(len(c10_sp), 12)
        self.assertEqual(len(c12_sp), 11)
        for p in sp:
            self.assertEqual(p["last_verified"], "2026-11-07")
            self.assertTrue(p["view_url"].startswith("https://upmsp.edu.in/Downloads/ModelPaper/"))
            self.assertTrue(p["download_url"].startswith("https://upmsp.edu.in/Downloads/ModelPaper/"))
            self.assertEqual(p["verification_status"], "verified_official")
            self.assertEqual(p["academic_session"], "2026-27")
            self.assertIn("3 Hours 15 Minutes", p["duration"])
            self.assertIn(p["max_marks"], [70, 100])

        # 4. Question Bank
        with open(os.path.join(app.root_path, "data", "up_question_bank.json"), "r", encoding="utf-8") as f:
            qb = json.load(f)
        self.assertEqual(qb["metadata"]["official_source"], "https://upmsp.edu.in/Board_QuestionBank.aspx")
        self.assertEqual(qb["classes"]["10"]["status"], "awaiting_official_release")
        self.assertEqual(qb["classes"]["12"]["status"], "awaiting_official_release")
        self.assertEqual(len(qb["classes"]["9"]["items"]), 16)
        for item in qb["classes"]["9"]["items"]:
            self.assertTrue(item["download_url"].startswith("https://upmsp.edu.in/Downloads/QuestionBank/"))

        # 5. Circulars
        with open(os.path.join(app.root_path, "data", "up_circulars.json"), "r", encoding="utf-8") as f:
            circ = json.load(f)
        self.assertEqual(len(circ), 5)
        for c in circ:
            self.assertEqual(c["last_verified"], "2026-11-05")
            self.assertTrue(c["official_url"].startswith("https://upmsp.edu.in"))


    # =========================================================================
    # Multi-Board Homepage Upgrade & Branding Modernisation Tests
    # =========================================================================

    def test_multi_board_homepage_branding_and_hero(self):
        """Verify homepage hero badge, heading, description, search placeholder, and no CBSE-only platform claims"""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # Hero badge & heading
        self.assertIn("Independent Boards &amp; Exam Resources", html)
        self.assertIn("Verified Board &amp; Competitive Exam Information", html)
        self.assertIn("StudySignal is an independent educational platform providing verified syllabus PDFs, official date sheets, sample papers, circulars, and notices across CBSE, UP Board (UPMSP), and CISCE (ICSE &amp; ISC).", html)
        self.assertIn('placeholder="Search subjects, codes, circulars, or boards across India..."', html)

        # Popular search chips
        self.assertIn("CBSE Class 10 Math", html)
        self.assertIn("UP Board Hindi 901", html)
        self.assertIn("ICSE Class 10 English", html)
        self.assertIn("UP Board High School", html)
        self.assertIn("ISC Class 12 Physics", html)

        # No CBSE-only platform claims
        self.assertNotIn("Dedicated CBSE Education Information Portal", html)
        self.assertNotIn("CBSE Class 10 & 12 Examination Hub", html)

    def test_multi_board_navigation_and_announcement_bar(self):
        """Verify top bar uses 'Official Sources' with cbse, upmsp, cisce and dropdown links to /cbse"""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # Top announcement bar
        self.assertIn("Official Sources:", html)
        self.assertNotIn("Official CBSE Links:", html)
        self.assertIn("https://www.cbse.gov.in", html)
        self.assertIn("https://upmsp.edu.in", html)
        self.assertIn("https://cisce.org", html)

        # Navigation dropdown
        self.assertIn('href="/cbse"', html)
        self.assertIn('href="/up-board"', html)
        self.assertIn('href="/icse"', html)

    def test_multi_board_independent_portal_notice(self):
        """Verify site-wide advisory notice includes CBSE, UPMSP, CISCE, ICSE, ISC"""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        self.assertIn("INDEPENDENT PORTAL NOTICE", html)
        self.assertIn("Central Board of Secondary Education (CBSE)", html)
        self.assertIn("Uttar Pradesh Madhyamik Shiksha Parishad (UPMSP)", html)
        self.assertIn("Council for the Indian School Certificate Examinations (CISCE / ICSE / ISC)", html)

    def test_multi_board_dedicated_portals_section(self):
        """Verify Dedicated Boards & Exam Portals section contains CBSE, UP Board, and CISCE cards with working links"""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        self.assertIn("Dedicated Boards &amp; Exam Portals", html)
        # CBSE card
        self.assertIn('href="/cbse/class-10"', html)
        self.assertIn('href="/cbse/class-12"', html)
        self.assertIn('href="/cbse/datesheets"', html)
        self.assertIn('href="/cbse/syllabus"', html)
        self.assertIn('href="/cbse/pyq"', html)
        self.assertIn('href="/cbse/circulars"', html)

        # UP Board card
        self.assertIn('href="/up-board/class-10"', html)
        self.assertIn('href="/up-board/class-12"', html)
        self.assertIn('href="/up-board/sample-papers"', html)
        self.assertIn('href="/up-board/question-bank"', html)
        self.assertIn('href="/up-board/datesheets"', html)
        self.assertIn('href="/up-board/circulars"', html)

        # CISCE card
        self.assertIn('href="/icse/class-10"', html)
        self.assertIn('href="/icse/class-12"', html)
        self.assertIn('href="/icse/syllabus"', html)
        self.assertIn('href="/icse/pyq"', html)
        self.assertIn('href="/icse/datesheets"', html)
        self.assertIn('href="/icse/circulars"', html)

    def test_multi_board_syllabus_and_circulars_sections(self):
        """Verify syllabus and circulars sections contain board badges, filters, and source hosts"""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # Syllabus
        self.assertIn("Verified Official Syllabus Resources", html)
        self.assertIn("syllabus-filter-bar", html)
        self.assertIn("cbseacademic.nic.in", html)
        self.assertIn("upmsp.edu.in", html)
        self.assertIn("cisce.org", html)

        # Circulars
        self.assertIn("Boards &amp; Examination Updates", html)
        self.assertIn("circulars-filter-bar", html)
        self.assertIn("Reminder: Submission of List of Candidates", html)

    def test_multi_board_datesheet_advisory_and_footer(self):
        """Verify multi-board datesheet advisory and footer columns"""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # Datesheet advisory
        self.assertIn("Board-wise Examination Date Sheet Advisory", html)
        self.assertIn('href="/cbse/datesheets"', html)
        self.assertIn('href="/up-board/datesheets"', html)
        self.assertIn('href="/icse/datesheets"', html)

        # Footer
        self.assertIn("Multi-Board Educational Platform", html)
        self.assertIn("Boards &amp; Exam Resources", html)
        self.assertIn("Official Sources", html)
        self.assertIn("cbse.gov.in", html)
        self.assertIn("upmsp.edu.in", html)
        self.assertIn("cisce.org", html)


    def test_upmsp_official_urls_integrity(self):
        """Verify that UPMSP official URLs point to active .aspx endpoints, not dead .html files."""
        self.assertEqual(Config.OFFICIAL_URLS["upmsp_syllabus"], "https://upmsp.edu.in/Board_Syllabus.aspx")
        self.assertEqual(Config.OFFICIAL_URLS["upmsp_model_papers"], "https://upmsp.edu.in/Board_ModelPaper.aspx")
        self.assertEqual(Config.OFFICIAL_URLS["upmsp_question_bank"], "https://upmsp.edu.in/Board_QuestionBank.aspx")
        for k, v in Config.OFFICIAL_URLS.items():
            if "upmsp" in k:
                self.assertNotIn("Syllabus.html", v, f"Dead URL Syllabus.html found in {k}")
                self.assertNotIn("ModelPaper.html", v, f"Dead URL ModelPaper.html found in {k}")
                self.assertNotIn("QuestionBank.html", v, f"Dead URL QuestionBank.html found in {k}")


    def test_logo_assets_exist_and_served(self):
        """Verify that all authentic board and exam logo PNG assets exist and are served via static endpoint."""
        import os
        from PIL import Image

        logos = [
            ("static/images/boards/cbse-logo.png", "/static/images/boards/cbse-logo.png"),
            ("static/images/boards/upmsp-logo.png", "/static/images/boards/upmsp-logo.png"),
            ("static/images/boards/cisce-logo.png", "/static/images/boards/cisce-logo.png"),
            ("static/images/exams/nta-logo.png", "/static/images/exams/nta-logo.png"),
            ("static/images/exams/jee-adv-logo.png", "/static/images/exams/jee-adv-logo.png"),
        ]

        for filepath, url_path in logos:
            self.assertTrue(os.path.exists(filepath), f"Missing logo file on disk: {filepath}")
            # Verify image format and integrity
            with Image.open(filepath) as img:
                self.assertEqual(img.format, "PNG")
                self.assertGreater(img.width, 0)
                self.assertGreater(img.height, 0)
            # Verify HTTP serving
            res = self.client.get(url_path)
            self.assertEqual(res.status_code, 200, f"Failed to serve {url_path}")
            self.assertIn("image/png", res.content_type)
            res.close()

    def test_homepage_board_and_exam_logos_rendered(self):
        """Verify homepage renders official board and examination logos across all required sections."""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")

        # 1. Dedicated Portal Cards with logos
        self.assertIn("portal-card-logo", html)
        self.assertIn("/static/images/boards/cbse-logo.png", html)
        self.assertIn("/static/images/boards/upmsp-logo.png", html)
        self.assertIn("/static/images/boards/cisce-logo.png", html)

        # 2. Roadmap mini-cards with logos
        self.assertIn("mini-logo", html)
        self.assertIn("/static/images/exams/nta-logo.png", html)

        # 3. Syllabus and circular badges with inline logos
        self.assertIn("badge-board-logo", html)

        # 4. Datesheet advisory with board logos
        self.assertIn("datesheet-board-logo", html)

        # 5. Header dropdown and mobile drawer
        self.assertIn("nav-board-logo", html)

        # 6. Footer official source links with logos
        self.assertIn("footer-source-logo", html)

    def test_hub_pages_logo_branding(self):
        """Verify individual board hubs and directory cards display authentic branding logos."""
        # 1. CBSE Hub & Class 10
        res = self.client.get("/cbse")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("hub-hero-logo", html)
        self.assertIn("/static/images/boards/cbse-logo.png", html)

        res = self.client.get("/cbse/class-10")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("hub-hero-logo", html)
        self.assertIn("/static/images/boards/cbse-logo.png", html)

        # 2. UP Board Hub & High School
        res = self.client.get("/up-board")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("hub-hero-logo", html)
        self.assertIn("/static/images/boards/upmsp-logo.png", html)

        res = self.client.get("/up-board/class-10")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("hub-hero-logo", html)
        self.assertIn("/static/images/boards/upmsp-logo.png", html)

        # 3. CISCE Hub & ICSE Class 10
        res = self.client.get("/icse")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("hub-hero-logo", html)
        self.assertIn("/static/images/boards/cisce-logo.png", html)

        res = self.client.get("/icse/class-10")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("hub-hero-logo", html)
        self.assertIn("/static/images/boards/cisce-logo.png", html)

        # 4. Boards Directory
        res = self.client.get("/boards")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("board-card-logo", html)
        self.assertIn("/static/images/boards/cbse-logo.png", html)
        self.assertIn("/static/images/boards/upmsp-logo.png", html)
        self.assertIn("/static/images/boards/cisce-logo.png", html)
        self.assertIn("/static/images/exams/nta-logo.png", html)

if __name__ == "__main__":
    unittest.main()


