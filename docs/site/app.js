'use strict';
const dialog = document.querySelector('#lightbox');
const image = dialog.querySelector('img');
const caption = dialog.querySelector('p');
document.querySelectorAll('.photo-open').forEach(link => {
  link.addEventListener('click', event => {
    if (event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
    event.preventDefault();
    image.src = link.href;
    image.alt = link.querySelector('img').alt;
    caption.textContent = image.alt;
    dialog.showModal();
    document.body.classList.add('modal-open');
  });
});
dialog.addEventListener('close', () => document.body.classList.remove('modal-open'));
dialog.addEventListener('click', event => {if(event.target === dialog) dialog.close();});
const links = [...document.querySelectorAll('.nav-item')];
const sections = [...document.querySelectorAll('main > .section')];
let pending = false;
function markCurrent() {
  pending = false;
  const current = [...sections].reverse().find(section => section.getBoundingClientRect().top <= 150) || sections[0];
  links.forEach(link => {
    if (link.hash === '#' + current.id) link.setAttribute('aria-current', 'location');
    else link.removeAttribute('aria-current');
  });
}
window.addEventListener('scroll', () => {if(!pending){pending=true;requestAnimationFrame(markCurrent);}}, {passive:true});
markCurrent();
