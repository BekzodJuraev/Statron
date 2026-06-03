function toggleIcon(button) {
    const icon = button.querySelector('.icon');
    if (icon.src.includes('material-symbols_stop.svg')) {
        icon.src = 'img/tracking-posts/solar_play-bold.svg';
    } else {
        icon.src = 'img/tracking-posts/material-symbols_stop.svg';
    }
}

// bookmarks.html button click event

function setActiveTab(button) {
    // Remove '_tab-active' class from all buttons
    const buttons = document.querySelectorAll('.tabs-navigation__title');
    buttons.forEach(btn => btn.classList.remove('_tab-active'));

    // Add '_tab-active' to the clicked button
    button.classList.add('_tab-active');

    // Hide all tab contents
    const tabContents = document.querySelectorAll('.tab-content');
    tabContents.forEach(content => content.style.display = 'none');

    // Get the tab identifier from the clicked button's data-tab attribute
    const tabId = button.getAttribute('data-tab');

    // Show the corresponding tab content
    const activeContent = document.getElementById(tabId);
    if (activeContent) {
        activeContent.style.display = 'block';
    }
}
document.addEventListener("click", function (e) {
    const s = e.target;

    // --- ЛОГИКА DROPDOWN (Balance) ---
    const dropBtn = s.closest("[data-dropdown-btn]");
    const currentDropdown = s.closest("[data-dropdown]");

    if (dropBtn) {
        // 1. Клик по кнопке: закрываем все другие, переключаем текущий
        document.querySelectorAll("[data-dropdown]._active").forEach(openDrp => {
            if (openDrp !== currentDropdown) openDrp.classList.remove("_active");
        });
        currentDropdown.classList.toggle("_active");
        return; // Важно: выходим, чтобы не сработал код закрытия ниже
    }

    if (currentDropdown) {
        // 2. Клик внутри контента дропдауна: ничего не делаем, не закрываем
        // Здесь можно добавить проверку на клик по ссылкам внутри, если нужно закрывать при переходе
    } else {
        // 3. Клик мимо (на пустое место): закрываем все активные дропдауны
        document.querySelectorAll("[data-dropdown]._active").forEach(openDrp => {
            openDrp.classList.remove("_active");
        });
    }

    // --- ВАША ОСТАЛЬНАЯ ЛОГИКА ---
    // Обработка [data-click]
    if (s.closest("[data-click]")) {
        const clickElement = s.closest("[data-click]");
        document.querySelectorAll("[data-click]._active").forEach(el => {
            if (el !== clickElement) el.classList.remove("_active");
        });
        clickElement.classList.add("_active");
    }

    // Обработка #like
    if (s.closest("#like")) {
        // Используем стандартный toggle вместо функции t
        s.closest("#like").classList.toggle("_active");
    }
});