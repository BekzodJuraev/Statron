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