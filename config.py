"""
StudySignal - Configuration File
Centralized settings for site metadata, advertising slots, and official links.
"""

import os

class Config:
    # Site Identity
    SITE_NAME = "StudySignal"
    SITE_TAGLINE = "Independent Multi-Board & Competitive Exam Information Portal"
    SITE_DESCRIPTION = (
        "StudySignal provides accurate, verified Class 10 and 12 curriculum, syllabus documents, "
        "official date sheets, sample papers, PYQs, circulars, and notifications across CBSE, "
        "UP Board (UPMSP), CISCE (ICSE/ISC), Bihar Board (BSEB), and Maharashtra Board (MSBSHSE), "
        "plus dedicated official portals for JEE Main, JEE Advanced, NEET UG, and CUET UG."
    )
    SECRET_KEY = os.environ.get("SECRET_KEY", "studysignal-default-dev-key")
    PRODUCTION_BASE_URL = os.environ.get("PRODUCTION_BASE_URL", "https://exampulse-india.onrender.com")
    BASE_URL = os.environ.get("BASE_URL", os.environ.get("RENDER_EXTERNAL_URL", "http://127.0.0.1:5000"))
    
    # Social Sharing Metadata (Representing full educational platform scope)
    DEFAULT_OG_IMAGE = f"{PRODUCTION_BASE_URL}/static/images/og-preview.png"
    DEFAULT_OG_IMAGE_ALT = (
        "StudySignal - Independent Educational Information Portal for CBSE Class 10 (Secondary) and "
        "Class 12 (Senior Secondary), UP Board, CISCE, Bihar Board (BSEB), Maharashtra Board (MSBSHSE) "
        "and National Competitive Exams (JEE Main, JEE Advanced, NEET UG, CUET UG)"
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
        "SCERT Maharashtra, NTA (National Testing Agency), JEE Main, JEE Advanced / JAB / IITs, "
        "NEET UG, CUET UG, JoSAA, CSAB, NMC, DCI, MCC, AACCC, any education board, examination authority, "
        "Ministry of Education, or Government of India. Always verify important information through the "
        "respective official websites."
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
        "ebalbharati": "https://books.ebalbharati.in/ebook.aspx",
        # National Testing Agency (NTA) & Shared Official Prep Portals
        "nta_main": "https://nta.ac.in/",
        "nta_abhyas": "https://nta.ac.in/Abhyas",
        "nta_quiz": "https://nta.ac.in/Quiz",
        "nta_lectures": "https://nta.ac.in/LecturesContent",
        "nta_downloads": "https://nta.ac.in/Downloads",
        "nta_calendar_revised": "https://nta.ac.in/Download/Notice/ExamcalendarRevised.pdf",
        # JEE Main (NTA)
        "jeemain_main": "https://jeemain.nta.nic.in/",
        "jeemain_syllabus": "https://cdnbbsr.s3waas.gov.in/s3f8e59f4b2fe7c5705bf878bbd494ccdf/uploads/2026/10/20261024683680768.pdf",
        "jeemain_bulletin": "https://cdnbbsr.s3waas.gov.in/s3f8e59f4b2fe7c5705bf878bbd494ccdf/uploads/2026/10/202610241890224107.pdf",
        "jeemain_notices": "https://jeemain.nta.nic.in/public-notices/",
        "jeemain_archive_2026": "https://jeemain.nta.nic.in/2026-archive/",
        "jeemain_candidate_2026": "https://jeemain.nta.nic.in/candidate-activity-2026/",
        "jeemain_apply_2027": "https://jeemain.nta.nic.in/online-application-form-for-jee-main-2027-session-1/",
        # JEE Advanced (JAB / Organizing Institute: IIT Roorkee 2026) & JoSAA / CSAB
        "jeeadv_main": "https://jeeadv.ac.in/",
        "jeeadv_bulletin": "https://jeeadv.ac.in/documents/IBEnglish_2026.pdf",
        "jeeadv_archive": "https://jeeadv.ac.in/archive.html",
        "jeeadv_resources": "https://jeeadv.ac.in/resources.html",
        "jeeadv_eligibility": "https://jeeadv.ac.in/eligibility.html",
        "jeeadv_admission": "https://jeeadv.ac.in/admission_criteria.html",
        "jeeadv_foreign": "https://jeeadv.ac.in/foreign.html",
        "jeeadv_faq": "https://jeeadv.ac.in/faq.html",
        "jeeadv_cportal": "https://cportal.jeeadv.ac.in/",
        "josaa_main": "https://josaa.nic.in/",
        "josaa_login": "https://josaa.admissions.nic.in/applicant/root/candidatelogin.aspx",
        "csab_main": "https://csab.nic.in/",
        # NEET UG (NTA / NMC / DCI / MCC / AACCC)
        "neet_main": "https://neet.nta.nic.in/",
        "neet_syllabus_2026": "https://cdnbbsr.s3waas.gov.in/s37bc1ec1d9c3426357e69acd5bf320061/uploads/2026/01/202601081066816297.pdf",
        "neet_bulletin_2026": "https://cdnbbsr.s3waas.gov.in/s37bc1ec1d9c3426357e69acd5bf320061/uploads/2026/02/202602231394640855.pdf",
        "neet_notices": "https://neet.nta.nic.in/public-notices/",
        "neet_archive": "https://neet.nta.nic.in/archive/",
        "nmc_main": "https://www.nmc.org.in/",
        "dci_main": "https://dciindia.gov.in/",
        "mcc_ug": "https://mcc.nic.in/ug-medical-counselling/",
        "aaccc_main": "https://aaccc.gov.in/",
        # CUET UG (NTA)
        "cuet_main": "https://cuet.nta.nic.in/",
        "cuet_syllabus_2026": "https://cuet.nta.nic.in/cuetug-2026-syllabus/",
        "cuet_bulletin_2026": "https://cdnbbsr.s3waas.gov.in/s3d1a21da7bca4abff8b0b61b87597de73/uploads/2026/01/202601031633478370.pdf",
        "cuet_faq_2026": "https://cdnbbsr.s3waas.gov.in/s3d1a21da7bca4abff8b0b61b87597de73/uploads/2026/01/2026011697237004.pdf",
        "cuet_universities": "https://cuet.nta.nic.in/participating-universities/",
        "cuet_notices": "https://cuet.nta.nic.in/document-category/public-notice/"
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
