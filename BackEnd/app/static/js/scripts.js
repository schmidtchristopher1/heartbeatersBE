// JavaScript for handling a mobile navigation toggle
document.addEventListener("DOMContentLoaded", function () {
  const navToggle = document.querySelector(".nav-toggle");
  const navLinks = document.querySelectorAll("header nav a");

  // Toggle navigation menu on small screens
  navToggle &&
    navToggle.addEventListener("click", () => {
      document.querySelector("header nav").classList.toggle("open");
    });

  // Close navigation when a link is clicked (useful for mobile view)
  navLinks.forEach((link) => {
    link.addEventListener("click", () => {
      document.querySelector("header nav").classList.remove("open");
    });
  });
});
