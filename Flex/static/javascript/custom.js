
var imgs = document.querySelectorAll('.post-content img');

function fullwidth(event) {
    window.location = event.target.src;
}

imgs.forEach((node) => {
    node.onclick = fullwidth;
    // this is too annoying for mobile phones
    //node.ontouchstart = fullwidth;
});
