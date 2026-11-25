(() => {
  "use strict";

  document.addEventListener("DOMContentLoaded", () => {
    // Mobile sidebar
    const shell = document.getElementById("appShell");
    const toggle = document.getElementById("menuToggle");
    const backdrop = document.getElementById("backdrop");

    const closeSidebar = () => {
      if (!shell) return;
      shell.classList.remove("sidebar-open");
      if (backdrop) backdrop.hidden = true;
      if (toggle) toggle.setAttribute("aria-expanded", "false");
    };

    if (toggle && shell) {
      toggle.addEventListener("click", () => {
        const open = shell.classList.toggle("sidebar-open");
        if (backdrop) backdrop.hidden = !open;
        toggle.setAttribute("aria-expanded", String(open));
      });
    }

    if (backdrop) backdrop.addEventListener("click", closeSidebar);

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeSidebar();
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 1024) closeSidebar();
    });

    // Auto-dismiss flash messages
    document.querySelectorAll(".flash").forEach((flash) => {
      window.setTimeout(() => {
        flash.classList.add("is-hiding");
        window.setTimeout(() => flash.remove(), 320);
      }, 5000);
    });

    // Live unit counter on the enrollment form
    const enrollForm = document.getElementById("enrollForm");
    if (enrollForm) {
      const boxes = Array.from(
        enrollForm.querySelectorAll('input[name="sections"]')
      );
      const unitTotal = document.getElementById("unitTotal");
      const subjectTotal = document.getElementById("subjectTotal");

      const updateSummary = () => {
        let units = 0;
        let subjects = 0;
        boxes.forEach((box) => {
          if (box.checked) {
            units += Number(box.dataset.units || 0);
            subjects += 1;
          }
        });
        if (unitTotal) unitTotal.textContent = String(units);
        if (subjectTotal) subjectTotal.textContent = String(subjects);
      };

      boxes.forEach((box) => box.addEventListener("change", updateSummary));
      updateSummary();
    }

    // Optional confirmations
    document.querySelectorAll("[data-confirm]").forEach((element) => {
      element.addEventListener("click", (event) => {
        const message =
          element.getAttribute("data-confirm") || "Are you sure?";
        if (!window.confirm(message)) event.preventDefault();
      });
    });
  });
})();
