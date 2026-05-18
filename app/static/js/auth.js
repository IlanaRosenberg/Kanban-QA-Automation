const TOKEN_KEY = 'kanban_token';
const USER_KEY = 'kanban_user';

(function initNav() {
  const token = localStorage.getItem(TOKEN_KEY);
  const user = JSON.parse(localStorage.getItem(USER_KEY) || 'null');
  const loginLink = document.getElementById('nav-login-link');
  const logoutLink = document.getElementById('nav-logout-link');
  const usernameEl = document.getElementById('nav-username');

  if (token && user) {
    if (loginLink) loginLink.classList.add('d-none');
    if (logoutLink) logoutLink.classList.remove('d-none');
    if (usernameEl) { usernameEl.textContent = user.username; usernameEl.classList.remove('d-none'); }
  }

  if (logoutLink) {
    logoutLink.addEventListener('click', (e) => {
      e.preventDefault();
      localStorage.removeItem(TOKEN_KEY);
      localStorage.removeItem(USER_KEY);
      window.location.href = '/login';
    });
  }
})();
