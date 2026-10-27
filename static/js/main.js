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

// Заявки: отправка без перезагрузки страницы. Без JS форма уходит обычным POST
// и сервер отвечает отдельной страницей
const NETWORK_ERROR = "Не удалось отправить заявку. Проверьте интернет и попробуйте ещё раз.";

function showLeadErrors(form, errors) {
  const common = [];
  for (const [name, messages] of Object.entries(errors)) {
    const field = form.elements[name];
    if (!field || field.type === "hidden") {
      common.push(...messages);
      continue;
    }
    field.setAttribute("aria-invalid", "true");
    const note = document.createElement("p");
    note.className = "mt-1.5 text-sm text-danger";
    note.dataset.fieldError = "";
    note.textContent = messages.join(" ");
    (field.type === "checkbox" ? field.closest("label") : field).after(note);
  }
  if (common.length) showLeadError(form, common.join(" "));
}

function showLeadError(form, message) {
  const box = form.querySelector("[data-lead-error]");
  box.textContent = message;
  box.hidden = false;
}

document.addEventListener("submit", async (event) => {
  const form = event.target.closest("form[data-lead-form]");
  if (!form) return;
  event.preventDefault();

  form.querySelectorAll("[data-field-error]").forEach((note) => note.remove());
  form.querySelectorAll("[aria-invalid]").forEach((field) => field.removeAttribute("aria-invalid"));
  form.querySelector("[data-lead-error]").hidden = true;
  if (!form.checkValidity()) {
    form.reportValidity();
    return;
  }

  const button = form.querySelector('[type="submit"]');
  button.disabled = true;
  try {
    const response = await fetch(form.action, {
      method: "POST",
      body: new FormData(form),
      headers: { Accept: "application/json" },
    });
    const data = await response.json();
    if (data.ok) {
      const success = form.closest("[data-lead-form-wrap]").querySelector("[data-lead-success]");
      form.hidden = true;
      success.hidden = false;
      form.reset();
    } else {
      showLeadErrors(form, data.errors || {});
    }
  } catch {
    showLeadError(form, NETWORK_ERROR);
  } finally {
    button.disabled = false;
  }
});
