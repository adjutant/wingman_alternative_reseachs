(() => {
  'use strict';
  const menu = document.querySelector('.menu-toggle');
  const sidebar = document.querySelector('#sidebar');
  const closeMenu = () => { sidebar?.classList.remove('open'); menu?.setAttribute('aria-expanded', 'false'); };
  menu?.addEventListener('click', () => {
    const open = sidebar.classList.toggle('open');
    menu.setAttribute('aria-expanded', String(open));
  });
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && sidebar?.classList.contains('open')) { closeMenu(); menu.focus(); }
  });
  sidebar?.querySelectorAll('a').forEach(a => a.addEventListener('click', closeMenu));
  const table = document.querySelector('#comparison-table');
  if (!table) return;
  const search = document.querySelector('#project-search');
  const group = document.querySelector('#group-filter');
  const lens = document.querySelector('#lens-filter');
  const ranges = table.dataset.study === 'tasks' ? {
    priority: [4,5,7,8,14,15,21,22], organization: [1,2,3,9,10,20],
    work: [4,6,7,8,9,11,12,13], runtime: [5,14,15,16,17],
    visibility: [10,18,19,20,21,22,23,24],
    all: Array.from({length:24}, (_,i) => i+1)
  } : {
    priority: [4,5,7,14,17,22], organization: [1,2,3,4,5,6,7,8],
    work: [9,10,11,12,13], runtime: [14,15,16,17], visibility: [18,19,20,21,22,23,24],
    all: Array.from({length:24}, (_,i) => i+1)
  };
  const total = table.querySelectorAll('tbody tr').length;
  const unit = table.dataset.study === 'tasks' ? 'codebases' : 'projects';
  const apply = () => {
    const query = search.value.trim().toLocaleLowerCase();
    let count = 0;
    table.querySelectorAll('tbody tr').forEach(row => {
      const visible = row.dataset.search.includes(query) && (!group.value || row.dataset.group === group.value);
      row.hidden = !visible;
      if (visible) count++;
    });
    table.querySelectorAll('[data-feature]').forEach(cell => {
      cell.hidden = !ranges[lens.value].includes(Number(cell.dataset.feature.slice(1)));
    });
    document.querySelector('#result-count').textContent = `${count} of ${total} ${unit}`;
    document.querySelector('#empty-result').hidden = count !== 0;
  };
  search.addEventListener('input', apply);
  group.addEventListener('change', apply);
  lens.addEventListener('change', apply);
  document.querySelector('.filters').addEventListener('submit', e => e.preventDefault());
  apply();
})();
