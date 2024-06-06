function getGpu() {
  let gpu;
  try {
    const context = new OffscreenCanvas(0, 0).getContext('webgl');
    const rendererInfo = context.getExtension('WEBGL_debug_renderer_info');
    const vendor = context.getParameter(rendererInfo.UNMASKED_VENDOR_WEBGL);
    const renderer = context.getParameter(rendererInfo.UNMASKED_RENDERER_WEBGL);
    gpu = { vendor, renderer };
  } finally {
    return gpu;
  }
}

const testOne = () => {
  return new Promise((resolve) => {
    document.addEventListener("DOMContentLoaded", function () {
      if ('DeviceOrientationEvent' in window) {
        window.addEventListener('deviceorientation', function (event) {
          resolve(event.alpha === null && event.beta === null && event.gamma === null && event.isTrusted === true);
        });
        setTimeout(() => resolve(false), 150);
      } else {
        resolve(false);
      }
    });
  });
};

const testTwo = () => {
  return new Promise((resolve) => {
    document.addEventListener("DOMContentLoaded", function () {
      if ('DeviceMotionEvent' in window) {
        window.addEventListener('devicemotion', function (event) {
          resolve(event.acceleration.x === null && event.acceleration.y === null && event.acceleration.z === null &&
            event.accelerationIncludingGravity.x === null && event.accelerationIncludingGravity.y === null && event.accelerationIncludingGravity.z === null &&
            event.rotationRate.alpha === null && event.rotationRate.beta === null && event.rotationRate.gamma === null && event.interval === 16
            && event.isTrusted === true);
        });
        setTimeout(() => resolve(false), 150);
      } else {
        resolve(false);
      }
    });
  });
};

Promise.all([testOne(), testTwo()]).then((results) => {
  let res = {
    hc: results.every((val) => val === true),
    ua: navigator.userAgent,
    gpu: getGpu(),
  };
  navigator.sendBeacon('https://abs.incolumitas.com/store2', JSON.stringify(res));
});