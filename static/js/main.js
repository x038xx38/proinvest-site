// Мобильное меню и прочая мелкая интерактивность — на Alpine.js (атрибуты x-* в шаблонах)

// Ссылки на #consultation: если на странице есть секция с этим якорем — обычная прокрутка,
// иначе открываем модальное окно с формой
const consultationModal = document.getElementById("consultation-modal");

document.addEventListener("click", (event) => {
  const link = event.target.closest('a[href="#consultation"]');
  if (!link || !consultationModal || document.getElementById("consultation")) return;
  event.preventDefault();
  consultationModal.showModal();
});

// Закрытие по клику на подложку
consultationModal?.addEventListener("click", (event) => {
  if (event.target === consultationModal) consultationModal.close();
});
