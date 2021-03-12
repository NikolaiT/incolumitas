window.addEventListener('load', function() {
    var imgs = document.querySelectorAll('.post-content img');
    imgs.forEach(function (node) {
        node.addEventListener('click', function(event) {
            window.location = event.target.src;
        });
    });
});