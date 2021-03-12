
document.addEventListener('load', function() {
    var imgs = document.querySelectorAll('.post-content img');

    function fullwidth(event) {
        window.location = event.target.src;
    }

    imgs.forEach((node) => {
        node.addEventListener('click', fullwidth);
    });
});