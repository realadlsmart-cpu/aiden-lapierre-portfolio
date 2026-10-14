const menu = document.querySelector('.menu-toggle');
const nav = document.querySelector('.nav');
menu?.addEventListener('click', () => {
  const open = menu.getAttribute('aria-expanded') !== 'true';
  menu.setAttribute('aria-expanded', String(open));
  nav.classList.toggle('is-open', open);
  menu.textContent = open ? 'Close' : 'Menu';
});
document.addEventListener('keydown', e => {
  if (e.key === 'Escape' && menu?.getAttribute('aria-expanded') === 'true') {
    menu.click(); menu.focus();
  }
});
const dialog = document.querySelector('#viewer');
if (dialog) {
  const buttons = [...document.querySelectorAll('.photo-button')];
  const image = dialog.querySelector('.viewer-image');
  const caption = dialog.querySelector('.viewer-caption');
  const counter = dialog.querySelector('.viewer-counter');
  const previous = dialog.querySelector('[data-previous]');
  const next = dialog.querySelector('[data-next]');
  let current = 0;
  let trigger;
  const show = index => {
    current = (index + buttons.length) % buttons.length;
    const b = buttons[current];
    image.src = b.dataset.full || b.querySelector('img').src;
    image.alt = b.querySelector('img').alt;
    caption.textContent = b.dataset.caption;
    counter.textContent = (current + 1) + ' / ' + buttons.length;
    previous.disabled = next.disabled = buttons.length < 2;
  };
  buttons.forEach((button, index) => button.addEventListener('click', () => {
    trigger = button; show(index); dialog.showModal();
  }));
  dialog.querySelector('[data-close]').addEventListener('click', () => dialog.close());
  previous.addEventListener('click', () => show(current - 1));
  next.addEventListener('click', () => show(current + 1));
  dialog.addEventListener('keydown', e => {
    if (e.key === 'ArrowLeft') {e.preventDefault(); show(current - 1);}
    if (e.key === 'ArrowRight') {e.preventDefault(); show(current + 1);}
  });
  dialog.addEventListener('click', e => {if(e.target === dialog) dialog.close();});
  dialog.addEventListener('close', () => {image.removeAttribute('src'); trigger?.focus();});
}
