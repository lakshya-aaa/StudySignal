"""
ExamPulse India - Configuration File
Centralized settings for site metadata, advertising slots, and official links.
"""

import os

class Config:
    # Site Identity
    SITE_NAME = "ExamPulse India"
    SITE_TAGLINE = "Independent CBSE Education Information Portal"
    SITE_DESCRIPTION = (
        "ExamPulse India provides accurate, verified CBSE Class 10 and 12 syllabus, "
        "official date sheet alerts, circulars, and academic notifications."
    )
    SECRET_KEY = os.environ.get("SECRET_KEY", "exampulse-india-default-dev-key")
    PRODUCTION_BASE_URL = os.environ.get("PRODUCTION_BASE_URL", "https://exampulse-india.onrender.com")
    BASE_URL = os.environ.get("BASE_URL", os.environ.get("RENDER_EXTERNAL_URL", "http://127.0.0.1:5000"))
    
    # Social Sharing Metadata (Representing full educational platform scope)
    DEFAULT_OG_IMAGE = f"{PRODUCTION_BASE_URL}/static/images/og-preview.png"
    DEFAULT_OG_IMAGE_ALT = (
        "ExamPulse India - Educational Information Portal for School Boards, "
        "Engineering & Medical Entrances, Government Examinations, and Higher Education Admissions"
    )
    
    # Academic Year Settings (Current: October 2026 -> Session 2026-27)
    CURRENT_ACADEMIC_YEAR = "2026-27"
    SHOW_DEMO_DATA = False  # Toggle to completely disable/hide demo and prototype records before launch
    
    # Non-Affiliation Disclaimer
    OFFICIAL_DISCLAIMER = (
        "ExamPulse India is an independent, non-commercial educational resource and is NOT "
        "affiliated with, endorsed by, or connected to the Central Board of Secondary Education "
        "(CBSE), Ministry of Education, or Government of India. Always cross-verify information "
        "on the official CBSE websites: cbse.gov.in and cbseacademic.nic.in."
    )
    
    # Verified Official CBSE URLs
    OFFICIAL_URLS = {
        "cbse_main": "https://www.cbse.gov.in",
        "cbse_academic": "https://cbseacademic.nic.in",
        "cbse_curriculum_current": "https://cbseacademic.nic.in/curriculum_2027.html",  # Current: 2026-27
        "cbse_curriculum_2026": "https://cbseacademic.nic.in/curriculum_2026.html",     # Previous: 2025-26
        "cbse_curriculum_2025": "https://cbseacademic.nic.in/curriculum_2025.html",     # Historical: 2024-25
        "cbse_curriculum_archive": "https://cbseacademic.nic.in/curriculum_archive.html",
        "cbse_circulars": "https://cbseacademic.nic.in/circulars.html",
        "cbse_examinations": "https://www.cbse.gov.in/cbsenew/examination_Circular.html"  # Verified active page
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
