// Adding a simple fade-in effect on scroll
window.addEventListener('scroll', () => {
  const cards = document.querySelectorAll('.equipment-card');
  cards.forEach(card => {
    const cardTop = card.getBoundingClientRect().top;
    if (cardTop < window.innerHeight - 50) {
      card.style.opacity = '1';
      card.style.transform = 'translateY(0)';
    }
  });
});
