// Apply after each page load, including instant navigation.
document$.subscribe(function () {
  document.querySelectorAll('a[href]').forEach(function (link) {
    if (/^https?:$/.test(link.protocol) && link.origin !== window.location.origin) {
      link.target = '_blank';
      link.relList.add('noopener', 'noreferrer');
    }
  });
});
