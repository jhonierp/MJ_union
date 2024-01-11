document.addEventListener('DOMContentLoaded', function () {
    const passwordInput = document.getElementById('id_password');
    const showPasswordButton = document.getElementById('show-password');

    showPasswordButton.addEventListener('click', function () {
      if (passwordInput.type === 'password') {
        passwordInput.type = 'text';
        showPasswordButton.textContent = 'Ocultar Contraseña';
      } else {
        passwordInput.type = 'password';
        showPasswordButton.textContent = 'Mostrar Contraseña';
      }
    });
  });