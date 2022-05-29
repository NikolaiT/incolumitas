function adblockDetected() {
    return new Promise(function (resolve, reject) {
        var script = document.createElement('script');

        script.onload = function() {
            if (document.getElementById('ybVg4vsBhs')) {
                resolve(false);
            } else {
                resolve(true);
            }
        }

        script.onerror = function() {
            resolve(true);
        }

        script.src = 'https://incolumitas.com/data/sailthru.js';
        document.body.appendChild(script);
    });
}

adblockDetected().then(function(result) {
    console.log('Adblock detected: ', result);
});