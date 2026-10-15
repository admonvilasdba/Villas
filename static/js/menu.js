(function () {
  'use strict';

  var modal = document.getElementById('dish-modal');
  if (!modal) return;

  var modalName = document.getElementById('modal-name');
  var modalDesc = document.getElementById('modal-desc');
  var modalPrice = document.getElementById('modal-price');
  var modalImage = document.getElementById('modal-image');
  var modalMedia = document.getElementById('modal-media');
  var modalPrep = document.getElementById('modal-prep');
  var modalTime = document.getElementById('modal-time');
  var closeBtn = modal.querySelector('.modal__close');
  var backBtn = document.getElementById('modal-back');

  var lastTrigger = null;

  function openModal(card) {
    lastTrigger = card;
    modalName.textContent = card.dataset.title || '';
    modalDesc.textContent = card.dataset.desc || '';
    modalPrice.textContent = card.dataset.price || '';

    if (card.dataset.image) {
      modalImage.src = card.dataset.image;
      modalImage.hidden = false;
      modalImage.alt = card.dataset.title || '';
    } else {
      modalImage.src = '';
      modalImage.hidden = true;
      modalImage.alt = '';
      modalMedia.classList.add('is-placeholder');
    }

    if (card.dataset.time) {
      modalTime.textContent = card.dataset.time;
      modalPrep.hidden = false;
    } else {
      modalPrep.hidden = true;
    }

    modal.classList.add('is-open');
    document.body.classList.add('modal-open');
    closeBtn.focus();
  }

  function closeModal() {
    modal.classList.remove('is-open');
    document.body.classList.remove('modal-open');
    if (lastTrigger) lastTrigger.focus();
  }

  document.querySelectorAll('.dish').forEach(function (card) {
    card.addEventListener('click', function () {
      openModal(card);
    });
    card.addEventListener('keydown', function (event) {
      if (event.key === 'Enter' || event.key === ' ') {
        event.preventDefault();
        openModal(card);
      }
    });
  });

  closeBtn.addEventListener('click', closeModal);
  if (backBtn) {
    backBtn.addEventListener('click', closeModal);
  }

  modal.addEventListener('click', function (event) {
    if (event.target === modal) closeModal();
  });

  document.addEventListener('keydown', function (event) {
    if (event.key === 'Escape' && modal.classList.contains('is-open')) {
      closeModal();
    }
  });

  /* Puntos del carrusel: resaltan el platillo visible. */
  document.querySelectorAll('.carousel-dots').forEach(function (dots) {
    var carousel = dots.previousElementSibling;
    if (!carousel || !carousel.classList.contains('dish-carousel')) return;

    var dotEls = Array.prototype.slice.call(dots.querySelectorAll('.carousel-dots__dot'));

    function update() {
      var threshold = carousel.scrollLeft + carousel.clientWidth / 2;
      var index = 0;
      Array.prototype.slice.call(carousel.children).forEach(function (child, i) {
        if (child.offsetLeft + child.offsetWidth / 2 <= threshold) index = i;
      });
      dotEls.forEach(function (dot, i) {
        dot.classList.toggle('is-active', i === index);
      });
    }

    carousel.addEventListener('scroll', update, { passive: true });
    window.addEventListener('resize', update, { passive: true });
    update();
  });

  /* Scrollspy: marca la categoría visible en la navegación de anclas. */
  var navLinks = Array.prototype.slice.call(document.querySelectorAll('.menu-nav__link'));
  var sections = Array.prototype.slice.call(document.querySelectorAll('.menu-category'));

  if (navLinks.length && sections.length) {
    var byId = new Map();
    navLinks.forEach(function (link) {
      var id = link.getAttribute('href').slice(1);
      byId.set(id, link);
    });

    var observer = new IntersectionObserver(
      function (entries) {
        entries.forEach(function (entry) {
          if (!entry.isIntersecting) return;
          var link = byId.get(entry.target.id);
          navLinks.forEach(function (l) {
            l.classList.toggle('is-active', l === link);
          });
        });
      },
      { rootMargin: '-90px 0px -65% 0px', threshold: 0 }
    );

    sections.forEach(function (section) {
      observer.observe(section);
    });
  }
})();