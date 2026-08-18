function highlightCode(el) {
  if (!el || !window.hljs) {
    return;
  }
  if (el.getAttribute('data-highlighted')) {
    el.removeAttribute('data-highlighted');
  }
  window.hljs.highlightElement(el);
}

window.addEventListener('load', function() {
    var imgs = document.querySelectorAll('.post-content img');
    imgs.forEach(function (node) {
        node.addEventListener('click', function(event) {
            window.location = event.target.src;
        });
    });
});
