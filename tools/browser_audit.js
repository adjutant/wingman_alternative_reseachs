(async () => {
  const manifest = await (await fetch('/coverage.json')).json();
  const paths = ['index.html', 'generic/index.html', 'generic/purpose.html', 'generic/method.html', 'generic/task-coordination.html',
    ...manifest.repositories.map(r => r.directory.split('/')[0] + '/index.html')];
  const frame = document.createElement('iframe');
  frame.style.cssText = 'position:fixed;left:-5000px;top:0;border:0;height:900px';
  document.body.append(frame);
  const results = [];
  for (const width of [1440, 390]) {
    frame.style.width = width + 'px';
    for (const path of paths) {
      await new Promise((resolve, reject) => {
        const timer = setTimeout(() => reject(new Error('Load timeout: ' + path)), 10000);
        frame.onload = () => { clearTimeout(timer); resolve(); };
        frame.src = '/' + path;
      });
      const doc = frame.contentDocument;
      await doc.fonts.ready;
      const view = frame.contentWindow;
      const issues = [];
      if (doc.documentElement.scrollWidth > doc.documentElement.clientWidth + 1) issues.push('page overflow');
      if (!view.getComputedStyle(doc.body).fontFamily.startsWith('Manrope')) issues.push('wrong font');
      if (!doc.fonts.check('13px Manrope')) issues.push('font unavailable');
      if (view.getComputedStyle(doc.querySelector('h1')).fontSize !== (width === 390 ? '28px' : '32px')) issues.push('wrong heading size');
      if (view.getComputedStyle(doc.querySelector('.sidebar')).display !== (width === 390 ? 'none' : 'flex')) issues.push('wrong navigation layout');
      if (Array.from(doc.images).some(img => !img.complete || img.naturalWidth === 0)) issues.push('image unavailable');
      if (Array.from(doc.querySelectorAll('pre')).some(block => block.tabIndex < 0)) issues.push('code block lacks keyboard access');
      if (/adjutant/i.test(doc.body.innerText)) issues.push('foreign brand in visible text');
      results.push({path, width, issues});
    }
  }
  frame.remove();
  return {pages: paths.length, viewports: [1440, 390], renderChecks: results.length,
    failures: results.filter(r => r.issues.length), checked: results};
})()
