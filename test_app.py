"""
ExamPulse India - Automated Test Suite
Phase 1 Content Integrity Audit, Broken Link Regression & Verification Tests.
"""

import json
import os
import unittest
import xml.etree.ElementTree as ET
from app import app
from config import Config

class ExamPulseIndiaTestCase(unittest.TestCase):
    def setUp(self):
        app.config["TESTING"] = True
        self.client = app.test_client()

    def test_homepage(self):
        """Test homepage loads with 200 OK, brand name, and key sections"""
        res = self.client.get("/")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("ExamPulse", html)
        self.assertIn("CBSE Class 10", html)
        self.assertIn("CBSE Class 12", html)
        self.assertIn("Official Advisory", html)
        self.assertIn("cbseacademic.nic.in", html)
        self.assertIn("Advertisement", html)  # Header leaderboard ad

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
        self.assertIn("CBSE Subject-wise Syllabus Explorer", html)

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
        """Test single subject syllabus blueprint view"""
        # Historical 2024-25 blueprint
        res_hist = self.client.get("/cbse/syllabus/cbse-10-maths-2025")
        self.assertEqual(res_hist.status_code, 200)
        html_hist = res_hist.data.decode("utf-8")
        self.assertIn("Mathematics", html_hist)
        self.assertIn("041", html_hist)
        self.assertIn("80 Marks", html_hist)
        self.assertIn("Historical Archive Record", html_hist)
        self.assertIn("cbseacademic.nic.in/web_material/CurriculumMain25/Sec/Maths_Sec_2024-25.pdf", html_hist)

        # Current 2026-27 blueprint
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
        """Test exam date sheets page and clear demo labeling"""
        res = self.client.get("/cbse/datesheets")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("CBSE Board Exam Date Sheet Hub", html)
        # Verify verified URL is used, NOT the broken URL
        self.assertNotIn("cbsenew/examination.html", html)
        self.assertIn("cbse.gov.in/cbsenew/examination_Circular.html", html)
        # Verify demo data has unmistakable label
        self.assertIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html)

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

    def test_search_and_json_api(self):
        """Test search by keyword and multi-field filters"""
        res = self.client.get("/search?q=Chemistry")
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Chemistry", html)

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
            self.assertIn("ExamPulse India", html)

    def test_contact_submission(self):
        """Test contact form POST request"""
        res = self.client.post("/contact", data={
            "name": "Amit Sharma",
            "email": "amit@example.com",
            "subject": "General Feedback",
            "message": "Testing portal functionality"
        })
        self.assertEqual(res.status_code, 200)
        html = res.data.decode("utf-8")
        self.assertIn("Message Received Successfully", html)
        self.assertIn("Amit Sharma", html)

    def test_robots_txt(self):
        """Test robots.txt accessibility and content"""
        res = self.client.get("/robots.txt")
        self.assertEqual(res.status_code, 200)
        self.assertIn("text/plain", res.content_type)
        text = res.data.decode("utf-8")
        self.assertIn("User-agent: *", text)
        self.assertIn("Sitemap:", text)

    def test_sitemap_xml(self):
        """Test sitemap.xml validity as standard XML"""
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

    def test_disclaimer_presence(self):
        """Test non-affiliation disclaimer presence on legal page and banner"""
        res = self.client.get("/disclaimer")
        html = res.data.decode("utf-8")
        self.assertIn("Strict Non-Affiliation Declaration", html)
        self.assertIn("independent, non-commercial educational information website", html)
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
        """Verify Class 10 English Language & Literature syllabus link is corrected and valid"""
        filepath = os.path.join(app.root_path, "data", "syllabus.json")
        with open(filepath, "r", encoding="utf-8") as f:
            syllabus = json.load(f)
        eng = next((s for s in syllabus if s.get("id") == "cbse-10-english-2025"), None)
        self.assertIsNotNone(eng)
        self.assertEqual(eng.get("official_url"), "https://cbseacademic.nic.in/web_material/CurriculumMain25/Sec/English_LL_2024-25.pdf")
        self.assertNotIn("English_LL_Sec_2024-25.pdf", eng.get("official_url"))

    def test_demo_records_badges_and_labels(self):
        """Verify demo records display unmistakable DEMO label and NEVER 'Verified Official'"""
        res_datesheet = self.client.get("/cbse/datesheets")
        html_ds = res_datesheet.data.decode("utf-8")
        self.assertIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html_ds)

        res_circ = self.client.get("/cbse/circulars")
        html_circ = res_circ.data.decode("utf-8")
        self.assertIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html_circ)

        # In search results, verify demo items do NOT receive verified badge
        res_search = self.client.get("/search?category=datesheet")
        html_search = res_search.data.decode("utf-8")
        if "DEMO — NOT AN OFFICIAL ANNOUNCEMENT" in html_search:
            # Check that DEMO items don't have the text '✓ Verified Official CBSE Source' on the same card
            self.assertIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html_search)

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
        """Ensure historical 2024-25 syllabus records are preserved with historical labels and not claimed as current"""
        filepath = os.path.join(app.root_path, "data", "syllabus.json")
        with open(filepath, "r", encoding="utf-8") as f:
            syllabus = json.load(f)
        
        historical = [s for s in syllabus if s.get("session_type") == "historical"]
        current = [s for s in syllabus if s.get("session_type") == "current"]

        self.assertGreaterEqual(len(historical), 17)
        self.assertGreaterEqual(len(current), 17)

        for s in historical:
            self.assertEqual(s.get("academic_year"), "2024-25")
            self.assertEqual(s.get("session_type"), "historical")
            self.assertIn("Historical Archive", s.get("academic_year_label"))

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
        """Verify ad placeholders show clean labels and NO internal developer instructions"""
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

        # 3. Demo entries
        self.assertIn("DEMO — NOT AN OFFICIAL ANNOUNCEMENT", html)

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

if __name__ == "__main__":
    unittest.main()
