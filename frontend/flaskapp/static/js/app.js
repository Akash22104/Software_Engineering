(function () {
  const html = document.documentElement;
  const toggleButton = document.getElementById("theme-toggle");
  const saved = window.localStorage.getItem("tracker-theme") || "dark";

  html.setAttribute("data-theme", saved);
  if (toggleButton) {
    toggleButton.textContent = saved === "dark" ? "Light Mode" : "Dark Mode";
    toggleButton.addEventListener("click", function () {
      const current = html.getAttribute("data-theme") || "dark";
      const next = current === "dark" ? "light" : "dark";
      html.setAttribute("data-theme", next);
      window.localStorage.setItem("tracker-theme", next);
      toggleButton.textContent = next === "dark" ? "Light Mode" : "Dark Mode";
    });
  }
})();
