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
    const buttons = document.querySelectorAll('.tabs-navigation__title');
    buttons.forEach(btn => btn.classList.remove('_tab-active'));
    button.classList.add('_tab-active');
}