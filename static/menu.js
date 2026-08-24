const menuToggle = document.querySelector('.menu-toggle');
const mainMenu = document.querySelector('#main-menu');

if (menuToggle && mainMenu) {
  const setMenuState = isOpen => {
    menuToggle.setAttribute('aria-expanded', String(isOpen));
    mainMenu.classList.toggle('is-open', isOpen);
  };

  menuToggle.addEventListener('click', () => {
    const isOpen = menuToggle.getAttribute('aria-expanded') === 'true';
    setMenuState(!isOpen);
  });

  mainMenu.querySelectorAll('a').forEach(link => {
    link.addEventListener('click', () => setMenuState(false));
  });

  document.addEventListener('click', event => {
    if (!mainMenu.contains(event.target) && !menuToggle.contains(event.target)) {
      setMenuState(false);
    }
  });

  document.addEventListener('keydown', event => {
    if (event.key === 'Escape') {
      setMenuState(false);
      menuToggle.focus();
    }
  });
}
