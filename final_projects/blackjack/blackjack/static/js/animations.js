// Анимации для BlackJack приложения
document.addEventListener('DOMContentLoaded', function() {
    // Анимация для карточек профиля
    const cards = document.querySelectorAll('.card');
    cards.forEach(card => {
        card.classList.add('animate__animated', 'animate__fadeIn');
    });

    // Анимация для аватара
    const avatar = document.querySelector('.avatar-image');
    if (avatar) {
        avatar.classList.add('animate__animated', 'animate__pulse');
        avatar.addEventListener('mouseenter', function() {
            this.classList.remove('animate__pulse');
            this.classList.add('animate__tada');
        });
        avatar.addEventListener('mouseleave', function() {
            this.classList.remove('animate__tada');
            this.classList.add('animate__pulse');
        });
    }

    // Анимация для кнопок
    const buttons = document.querySelectorAll('.casino-btn');
    buttons.forEach(button => {
        button.classList.add('animate__animated');
        button.addEventListener('mouseenter', function() {
            this.classList.add('animate__pulse');
        });
        button.addEventListener('mouseleave', function() {
            this.classList.remove('animate__pulse');
        });
    });

    // Анимация для баланса
    const balance = document.querySelector('.balance-amount');
    if (balance) {
        balance.classList.add('animate__animated', 'animate__flipInX');
    }

    // Анимация для имени пользователя
    const username = document.querySelector('.username');
    if (username) {
        username.classList.add('animate__animated', 'animate__bounceIn');
    }

    // Анимация для формы выбора аватара
    const avatarForm = document.querySelector('.avatar-selection form');
    if (avatarForm) {
        avatarForm.classList.add('animate__animated', 'animate__fadeInUp');
    }

    // Анимация для статистики игр
    const statsItems = document.querySelectorAll('.list-group-item');
    statsItems.forEach((item, index) => {
        item.classList.add('animate__animated', 'animate__fadeInRight');
        item.style.animationDelay = `${index * 0.1}s`;
    });

    // Анимация для таблицы последних игр
    const tableRows = document.querySelectorAll('tbody tr');
    tableRows.forEach((row, index) => {
        row.classList.add('animate__animated', 'animate__fadeInUp');
        row.style.animationDelay = `${index * 0.1}s`;
    });
});