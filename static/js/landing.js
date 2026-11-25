(() => {
  "use strict";

  document.addEventListener("DOMContentLoaded", () => {
    const header = document.getElementById("siteHeader");
    const nav = document.getElementById("siteNav");
    const toggle = document.getElementById("navToggle");

    const closeDropdowns = () => {
      document.querySelectorAll(".nav-item.has-drop").forEach((item) => {
        item.classList.remove("is-open");
        const button = item.querySelector(".nav-link");
        if (button) button.setAttribute("aria-expanded", "false");
      });
    };

    const closeNav = () => {
      if (!nav) return;
      nav.classList.remove("is-open");
      if (toggle) toggle.setAttribute("aria-expanded", "false");
      closeDropdowns();
    };

    if (toggle && nav) {
      toggle.addEventListener("click", () => {
        const open = nav.classList.toggle("is-open");
        toggle.setAttribute("aria-expanded", String(open));
        if (!open) closeDropdowns();
      });
    }

    document.querySelectorAll(".nav-item.has-drop").forEach((item) => {
      const button = item.querySelector(".nav-link");
      if (!button) return;

      button.addEventListener("click", (event) => {
        event.preventDefault();
        const open = item.classList.toggle("is-open");
        button.setAttribute("aria-expanded", String(open));
        document.querySelectorAll(".nav-item.has-drop").forEach((other) => {
          if (other === item) return;
          other.classList.remove("is-open");
          const otherButton = other.querySelector(".nav-link");
          if (otherButton) otherButton.setAttribute("aria-expanded", "false");
        });
      });
    });

    document.addEventListener("click", (event) => {
      if (header && !header.contains(event.target)) {
        closeNav();
      }
    });

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape") closeNav();
    });

    nav?.querySelectorAll("a").forEach((link) => {
      link.addEventListener("click", closeNav);
    });

    window.addEventListener("resize", () => {
      if (window.innerWidth > 1024) closeNav();
    });

    if (header) {
      const updateHeader = () => {
        header.classList.toggle("is-scrolled", window.scrollY > 8);
      };
      updateHeader();
      window.addEventListener("scroll", updateHeader, { passive: true });
    }
  });
})();
