(() => {
  const toggle = document.getElementById('menuToggle');
  const sidebar = document.getElementById('sidebar');
  if (toggle && sidebar) toggle.addEventListener('click', () => sidebar.classList.toggle('is-open'));
  const description = document.getElementById('id_descricao');
  const counter = document.getElementById('descriptionCount');
  if (description && counter) {
    const update = () => { counter.textContent = String(description.value.length); };
    description.addEventListener('input', update); update();
  }
})();
