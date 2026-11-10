"""
StudySignal - Configuration File
Centralized settings for site metadata, advertising slots, and official links.
"""

import os

class Config:
    # Site Identity
    SITE_NAME = "StudySignal"
    SITE_TAGLINE = "Independent Multi-Board Education Information Portal"
    SITE_DESCRIPTION = (
        "StudySignal provides accurate, verified Class 10 and 12 curriculum, "
        "syllabus documents, official date sheets, sample papers, PYQs, circulars, and "
        "academic notifications across CBSE, UP Board (UPMSP), CISCE (ICSE/ISC), "
        "Bihar Board (BSEB), and Maharashtra Board (MSBSHSE)."
    )
    SECRET_KEY = os.environ.get("SECRET_KEY", "studysignal-default-dev-key")
    PRODUCTION_BASE_URL = os.environ.get("PRODUCTION_BASE_URL", "https://exampulse-india.onrender.com")
    BASE_URL = os.environ.get("BASE_URL", os.environ.get("RENDER_EXTERNAL_URL", "http://127.0.0.1:5000"))
    
    # Social Sharing Metadata (Representing full educational platform scope)
    DEFAULT_OG_IMAGE = f"{PRODUCTION_BASE_URL}/static/images/og-preview.png"
    DEFAULT_OG_IMAGE_ALT = (
        "StudySignal - Independent Educational Information Portal for CBSE, UP Board, "
        "CISCE, Bihar Board (BSEB), and Maharashtra Board (MSBSHSE) Class 10 & 12 Curriculum, Date Sheets, and Official Notices"
    )
    
    # Academic Year Settings (Current: Session 2026-27)
    CURRENT_ACADEMIC_YEAR = "2026-27"
    SHOW_DEMO_DATA = False  # Toggle to completely disable/hide demo and prototype records before launch
    
    # Non-Affiliation Disclaimer
    OFFICIAL_DISCLAIMER = (
        "StudySignal is an independent, free-access educational information platform created to help "
        "students, parents and educators access academic resources, examination updates and educational "
        "information. StudySignal is not affiliated with, endorsed by, or officially connected to CBSE, "
        "UPMSP, CISCE, ICSE, ISC, BSEB (Bihar School Examination Board), MSBSHSE (Maharashtra State Board), "
        "SCERT Maharashtra, any other education board, examination authority, Ministry of Education, "
        "or Government of India. Always verify important information through the respective official websites."
    )
    
    # Verified Official Board URLs
    OFFICIAL_URLS = {
        "cbse_main": "https://www.cbse.gov.in",
        "cbse_academic": "https://cbseacademic.nic.in",
        "cbse_curriculum_current": "https://cbseacademic.nic.in/curriculum_2027.html",  # Current: 2026-27
        "cbse_curriculum_2026": "https://cbseacademic.nic.in/curriculum_2026.html",     # Previous: 2025-26
        "cbse_curriculum_2025": "https://cbseacademic.nic.in/curriculum_2025.html",     # Historical: 2024-25
        "cbse_curriculum_archive": "https://cbseacademic.nic.in/curriculum_archive.html",
        "cbse_circulars": "https://cbseacademic.nic.in/circulars.html",
        "cbse_examinations": "https://www.cbse.gov.in/cbsenew/examination_Circular.html",  # Verified active page
        "cbse_pyq_main": "https://www.cbse.gov.in/cbsenew/question-paper.html",
        "cisce_main": "https://cisce.org",
        "cisce_regulations": "https://cisce.org/regulations-and-syllabuses/",
        "cisce_notices": "https://cisce.org/notice-board/",
        "upmsp_main": "https://upmsp.edu.in",
        "upmsp_syllabus": "https://upmsp.edu.in/Board_Syllabus.aspx",
        "upmsp_model_papers": "https://upmsp.edu.in/Board_ModelPaper.aspx",
        "upmsp_question_bank": "https://upmsp.edu.in/Board_QuestionBank.aspx",
        "upmsp_results": "https://upresults.nic.in",
        "bseb_main": "https://biharboardonline.com",
        "bseb_org": "https://www.biharboardonline.org/",
        "bseb_ofss": "https://www.ofssbihar.net/Higher-Education/index.html",
        "maha_main": "https://www.mahahsscboard.in/en",
        "maha_syllabus_ssc": "https://www.mahahsscboard.in/en/studentAndSyllabus/sscGeneral",
        "maha_syllabus_hsc": "https://www.mahahsscboard.in/en/studentAndSyllabus/hscGeneral",
        "maha_syllabus_voc": "https://www.mahahsscboard.in/en/studentAndSyllabus/hscVocational",
        "maha_timetables": "https://www.mahahsscboard.in/en/studentCorner/timetables",
        "maha_question_papers": "https://www.mahahsscboard.in/en/questionPaper",
        "maha_publications": "https://www.mahahsscboard.in/en/publications",
        "maha_result": "https://www.mahahsscboard.in/en/result",
        "maha_verification": "https://www.mahahsscboard.in/en/verification",
        "maha_emarksheet": "https://boardmarksheet.maharashtra.gov.in/emarksheet/",
        "maha_form17": "https://www.mahahsscboard.in/en/form17",
        "maha_downloads": "https://www.mahahsscboard.in/en/download",
        "scert_maha_main": "https://www.maa.ac.in",
        "scert_maha_qbank": "https://www.maa.ac.in/index.php?tcf=questionbank",
        "scert_maha_curriculum": "https://www.maa.ac.in/index.php?tcf=curriculum",
        "ebalbharati": "https://books.ebalbharati.in/ebook.aspx"
    }

    # Reusable & Configurable Ad Placements
    # To disable ads completely across the portal, set ENABLED to False.
    # To replace placeholders with real Google AdSense / Sponsor scripts,
    # edit templates/components/ad_slot.html or set custom ad snippets below.
    ADS = {
        "enabled": False,  # Master toggle for advertising
        "slots": {
            "header_leaderboard": {
                "name": "Header Leaderboard",
                "width": 728,
                "height": 90,
                "enabled": True,
                "placeholder_label": "Advertisement (728x90 Leaderboard)"
            },
            "sidebar_box": {
                "name": "Sidebar Rectangle",
                "width": 300,
                "height": 250,
                "enabled": True,
                "placeholder_label": "Advertisement (300x250 Medium Rectangle)"
            },
            "in_content_banner": {
                "name": "In-Content Native Banner",
                "width": 728,
                "height": 90,
                "enabled": True,
                "placeholder_label": "Sponsored Content / Advertisement"
            },
            "footer_banner": {
                "name": "Footer Banner",
                "width": 728,
                "height": 90,
                "enabled": True,
                "placeholder_label": "Advertisement (728x90 Footer Banner)"
            }
        }
    }
