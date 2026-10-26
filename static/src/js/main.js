// Мобильное меню
document.querySelectorAll("[data-menu-toggle]").forEach((btn) => {
  const menu = document.getElementById(btn.getAttribute("aria-controls"));
  btn.addEventListener("click", () => {
    const open = menu.classList.toggle("hidden") === false;
    btn.setAttribute("aria-expanded", String(open));
  });
});
