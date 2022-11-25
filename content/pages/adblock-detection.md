Title: Adblock Detection
Date: 2022-10-16 22:00
Author: Nikolai Tschacher
Slug: Adblock-Detection
Status: draft
Sortorder: 10

Two years ago, I wrote a blog article about [Adblock Detection using JavaScript only](https://incolumitas.com/2020/12/27/detecting-uBlock-Origin-and-Adblock-Plus-with-JavaScript-only/). Since then, I maintain a NodeJS library to **detect Adblock Plus and uBlock Origin**. If you want to use the Adblock Detection Library on your own website, you can learn how to include it by visiting the project pages:

+ [npmjs.com Package for Adblock Detection](https://www.npmjs.com/package/adblock-detect-javascript-only)
+ [GitHub Page for Adblock Detection](https://github.com/NikolaiT/adblock-detect-javascript-only)

## Live Demo

<script type="text/javascript">
/**
 * Author: Nikolai Tschacher
 * Updated: 6th November 2022
 * Website: https://incolumitas.com/
 *
 * Detects uBlock Origin, Adblock Plus and AdBlocker Ultimate with JavaScript only.
 *
 * Usage: detectAdblock().then((res) => { console.log(res) });
 *
 */
function detectAdblock() {
  const adblockTests = {
    // https://github.com/uBlockOrigin/uAssets/blob/master/filters/filters-2022.txt
    uBlockOrigin: {
      url: 'https://incolumitas.com/data/yzfdmoan.js',
      id: '837jlaBksSjd9jh',
    },
    // https://github.com/easylist/easylist/blob/master/easylist/easylist_general_block.txt
    adblockPlus: {
      url: 'https://incolumitas.com/data/utep_ad.js',
      id: 'hfuBadsf3hFAk',
    },
  };

  function canLoadRemoteScript(obj) {
    return new Promise(function (resolve, reject) {
      var script = document.createElement('script');

      script.onload = function () {
        if (document.getElementById(obj.id)) {
          resolve(false);
        } else {
          resolve(true);
        }
      }

      script.onerror = function () {
        resolve(true);
      }

      script.src = obj.url;
      document.body.appendChild(script);
    });
  }

  return new Promise(function (resolve, reject) {
    let promises = [
      canLoadRemoteScript(adblockTests.uBlockOrigin),
      canLoadRemoteScript(adblockTests.adblockPlus),
    ];

    Promise.all(promises).then((results) => {
      resolve({
        uBlockOrigin: results[0],
        adblockPlus: results[1],
        usingAdblock: (results[0] === true) || (results[1] === true),
      });
    }).catch((err) => {
      reject(err);
    });
  });
}

detectAdblock().then((res) => {
  var ublockEl = document.getElementById('ublock_origin');
  var adblockEl = document.getElementById('adblock_plus');

  if (res.uBlockOrigin) {
    ublockEl.innerHTML = 'You are using uBlock Origin!';
  } else {
    ublockEl.style.backgroundColor = '#63ff85';
    ublockEl.innerHTML = 'You are not using uBlock Origin';
  }

  if (res.adblockPlus) {
    adblockEl.innerHTML = 'You are using Adblock Plus / AdBlocker Ultimate!';
  } else {
    adblockEl.style.backgroundColor = '#63ff85';
    adblockEl.innerHTML = 'You are not using Adblock Plus';
  }
});
</script>

<strong>Adblock Plus Detected:</strong> <span id="adblock_plus" style="border: 3px #4f4f4f solid;
    padding: 10px;
    background-color: #ff6363;
    margin-top: 20px;
    display: block;
    width: 300px;"></span>

<strong>uBlock Origin Detected:</strong> <span id="ublock_origin" style="border: 3px #4f4f4f solid;
    padding: 10px;
    background-color: #ff6363;
    margin-top: 10px;
    display: block;
    width: 300px;"></span>

## Source Code

This is the source code which detects uBlock Origin, Adblock Plus and AdBlocker Ultimate with JavaScript only:

```js
/**
 * Author: Nikolai Tschacher
 * Updated: 6th November 2022
 * Website: https://incolumitas.com/
 * 
 * Detects uBlock Origin, Adblock Plus and AdBlocker Ultimate with JavaScript only.
 * 
 * Usage: detectAdblock().then((res) => { console.log(res) });
 * 
 */
function detectAdblock() {
  const adblockTests = {
    // https://github.com/uBlockOrigin/uAssets/blob/master/filters/filters-2022.txt
    uBlockOrigin: {
      url: 'https://incolumitas.com/data/yzfdmoan.js',
      id: '837jlaBksSjd9jh',
    },
    // https://github.com/easylist/easylist/blob/master/easylist/easylist_general_block.txt
    adblockPlus: {
      url: 'https://incolumitas.com/data/utep_ad.js',
      id: 'hfuBadsf3hFAk',
    },
  };

  function canLoadRemoteScript(obj) {
    return new Promise(function (resolve, reject) {
      var script = document.createElement('script');

      script.onload = function () {
        if (document.getElementById(obj.id)) {
          resolve(false);
        } else {
          resolve(true);
        }
      }

      script.onerror = function () {
        resolve(true);
      }

      script.src = obj.url;
      document.body.appendChild(script);
    });
  }

  return new Promise(function (resolve, reject) {
    let promises = [
      canLoadRemoteScript(adblockTests.uBlockOrigin),
      canLoadRemoteScript(adblockTests.adblockPlus),
    ];

    Promise.all(promises).then((results) => {
      resolve({
        uBlockOrigin: results[0],
        adblockPlus: results[1],
        usingAdblock: (results[0] === true) || (results[1] === true),
      });
    }).catch((err) => {
      reject(err);
    });
  });
}
```

Use the above function:

```js
detectAdblock().then((res) => { console.log(res) });
```
