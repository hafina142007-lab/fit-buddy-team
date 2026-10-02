document.querySelectorAll('.choice').forEach((choice) => {
  const input = choice.querySelector('input');
  input.addEventListener('change', () => {
    document.querySelectorAll('.choice').forEach((item) => item.classList.remove('selected'));
    if (input.checked) choice.classList.add('selected');
  });
});
const form = document.getElementById('fitness-form');
if (form) {
  form.addEventListener('submit', (event) => {
    if (!form.reportValidity()) {
      event.preventDefault();
      return;
    }
    const button = form.querySelector('button[type="submit"]');
    button.disabled = true;
    button.innerHTML = 'Building your plan <span class="spinner"></span>';
  });
}
const observer = ('IntersectionObserver' in window) ? new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (entry.isIntersecting) {
      entry.target.classList.add('visible');
      observer.unobserve(entry.target);
    }
  });
}, { threshold: 0.12 }) : null;
if (observer) {
  document.querySelectorAll('.feature, .section-heading, .form-card, .planner-aside').forEach((el) => {
    el.classList.add('reveal');
    observer.observe(el);
  });
}
