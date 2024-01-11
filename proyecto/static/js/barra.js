document.addEventListener("DOMContentLoaded", function () {
        const sidebar = document.querySelector('.sidebar');
        const navLinks = document.querySelectorAll('.nav-link');
        const toggle = document.querySelector('.toggle');
    
        // Agregar un evento de clic para mostrar u ocultar el submenú
        navLinks.forEach(link => {
            link.addEventListener('click', () => {
                link.classList.toggle('active');
            });
        });
        // Agregar un evento de clic para abrir y cerrar la barra lateral
        toggle.addEventListener('click', () => {
            sidebar.classList.toggle('close');
        });
});