/**
 * StudySignal - Core Client-Side Utilities
 * Vanilla JS for responsive drawer, client-side filtering, and copy utilities
 */

document.addEventListener("DOMContentLoaded", function () {
  // 1. Mobile Menu Toggle
  const mobileBtn = document.getElementById("mobileMenuBtn");
  const mobileDrawer = document.getElementById("mobileDrawer");

  if (mobileBtn && mobileDrawer) {
    mobileBtn.addEventListener("click", function () {
      const isOpen = mobileDrawer.classList.toggle("open");
      mobileBtn.setAttribute("aria-expanded", isOpen ? "true" : "false");
    });
  }

  // 2. Client-side instant filter for Subject Grid (on /cbse/syllabus page)
  const clientFilterInput = document.getElementById("syllabusLiveSearch");
  const subjectCards = document.querySelectorAll(".subject-card");

  if (clientFilterInput && subjectCards.length > 0) {
    clientFilterInput.addEventListener("input", function (e) {
      const query = e.target.value.toLowerCase().trim();
      let matchCount = 0;

      subjectCards.forEach(function (card) {
        const title = card.querySelector(".subject-card-title")?.textContent.toLowerCase() || "";
        const code = card.querySelector(".code-pill")?.textContent.toLowerCase() || "";
        const desc = card.querySelector(".subject-card-desc")?.textContent.toLowerCase() || "";

        if (!query || title.includes(query) || code.includes(query) || desc.includes(query)) {
          card.style.display = "";
          matchCount++;
        } else {
          card.style.display = "none";
        }
      });

      const liveCounter = document.getElementById("syllabusLiveCount");
      if (liveCounter) {
        liveCounter.textContent = `Showing ${matchCount} of ${subjectCards.length} subjects`;
      }
    });
  }

  // 3. Class 12 Stream Tabs Switcher
  const streamTabs = document.querySelectorAll(".stream-tab-btn");
  const streamSections = document.querySelectorAll(".stream-content-group");

  if (streamTabs.length > 0 && streamSections.length > 0) {
    streamTabs.forEach(function (btn) {
      btn.addEventListener("click", function () {
        const targetStream = this.getAttribute("data-stream");

        streamTabs.forEach((t) => t.classList.remove("active"));
        this.classList.add("active");

        streamSections.forEach(function (sec) {
          if (targetStream === "all" || sec.getAttribute("data-stream") === targetStream) {
            sec.style.display = "";
          } else {
            sec.style.display = "none";
          }
        });
      });
    });
  }

  // 4. Copy Link Helper
  window.copyToClipboard = function (text, btnElement) {
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text).then(function () {
        const originalText = btnElement.innerText;
        btnElement.innerText = "Copied! ✓";
        btnElement.style.background = "#15803d";
        btnElement.style.color = "#ffffff";
        setTimeout(function () {
          btnElement.innerText = originalText;
          btnElement.style.background = "";
          btnElement.style.color = "";
        }, 2000);
      });
    }
  };
});
