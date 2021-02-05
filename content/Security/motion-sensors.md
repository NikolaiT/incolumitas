Title: Why does this Website know that I am sitting on the Toilet?
Date: 2021-02-05 22:17
Category: Security
Tags: JavaScript, deviceorientation, devicemotion
Slug: why-does-this-website-know-i-am-sitting-on-the-toilet
Author: Nikolai Tschacher
Summary: Android mobile devices give any website device orientation and device motion data. This data is quite sensitive in nature and should not be granted to the website without asking for explicit user consent.

I try to make this blog article short.

Android smartphones give websites access to the [deviceorientation](https://developer.mozilla.org/en-US/docs/Web/API/Window/deviceorientation_event) and the [devicemotion](https://developer.mozilla.org/en-US/docs/Web/API/Window/devicemotion_event) events.

Those events basically reveal smartphone motion data and the rotation angel of your smartphone. This data comes from the built-in accelerometer, gyroscope, and compass in mobile devices.

So if you are visiting this website from your Android mobile phone, you can see your device motion data in the box below.

<div id="exmaple">

<h3>Example</h3>

<strong>deviceorientation</strong>
<pre id="deviceorientationOutput"></pre>

<hr />

<strong>devicemotion</strong>
<pre id="devicemotionOutput"></pre>

<script>
(function() {
  var isAndroid = /(android)/i.test(navigator.userAgent);
  if (!isAndroid) {
    document.getElementById('exmaple').innerHTML = '<strong>You\'re not visiting from an Android device</strong>';
    return;
  }

  function round2(num) {
		return +(Math.round(num + "e+2")  + "e-2");
	}

  window.addEventListener('devicemotion', function(event) {
    var x = event.acceleration.x;
    var y = event.acceleration.y;
    var z = event.acceleration.z;

    // An object giving the rate of change of the device's orientation 
    // on the three orientation axis alpha, beta and gamma.
    // Rotation rate is expressed in degrees per seconds.
    var rotationRate = event.rotationRate;

    // A number representing the interval of time, in milliseconds, at which data is obtained from the device.
    var interval = event.interval;

    if (x !== null && y !== null && z !== null) {
      // only emit the event if device motion is more than 
      // 1 m/s2 in one of the axises
      if (Math.abs(x) > 1 || Math.abs(y) > 1 || Math.abs(z) > 1) {
        var el = document.getElementById('devicemotionOutput');
        el.innerHTML = JSON.stringify({
          event: 'devicemotion',
          accelerationX: round2(x),
          accelerationY: round2(y),
          accelerationZ: round2(z),
          interval: interval,
        }, null, 2);
      }
    }
  })

  window.addEventListener('deviceorientation', function(event) {
    // only cosider significant changes in rotation
    if (Math.abs(self.alpha - event.alpha) < 2 
      || Math.abs(self.gamma - event.gamma) < 1
      || Math.abs(self.beta - event.beta) < 1) {
      return;
    }

    this.alpha = event.alpha;
    this.beta = event.beta;
    this.gamma = event.gamma;

    if (event.alpha !== null && event.beta !== null && event.gamma !== null) {
      var el = document.getElementById('deviceorientationOutput');
      el.innerHTML = JSON.stringify({
        event: 'deviceorientation',
        alpha: round2(event.alpha),
        beta: round2(event.beta),
        gamma: round2(event.gamma),
        absolute: event.absolute,
      }, null, 2);
    }
  })
})();
</script>

</div>

### deviceorientation

This event yields a [`DeviceOrientationEvent`](https://developer.mozilla.org/en-US/docs/Web/API/DeviceOrientationEvent) in every 10ms time interval. This event includes the following information:

+ *DeviceOrientationEvent.absolute* -  A boolean that indicates whether or not the device is providing orientation data absolutely.
+ *DeviceOrientationEvent.alpha* -  A number representing the motion of the device around the z axis, express in degrees with values ranging from 0 (inclusive) to 360 (exclusive).

+ *DeviceOrientationEvent.beta* -  A number representing the motion of the device around the x axis, express in degrees with values ranging from -180 (inclusive) to 180 (exclusive). This represents a front to back motion of the device.
+ *DeviceOrientationEvent.gamma* -  A number representing the motion of the device around the y axis, express in degrees with values ranging from -90 (inclusive) to 90 (exclusive). This represents a left to right motion of the device.

<figure>
    <img src="/images/deviceorientation.png" alt="deviceorientation" style="width:400px" />
    <figcaption>Illustration of the device orientation</figcaption>
</figure>

### devicemotion

This event yields a [`DeviceMotionEvent`](https://developer.mozilla.org/en-US/docs/Web/API/DeviceMotionEvent) in every 10ms time interval. This event includes the following information:

+ *DeviceMotionEvent.acceleration* - An object giving the acceleration of the device on the three axis X, Y and Z. Acceleration is expressed in m/s2.
+ *DeviceMotionEvent.accelerationIncludingGravity* - An object giving the acceleration of the device on the three axis X, Y and Z with the effect of gravity. Acceleration is expressed in m/s2.
+ *DeviceMotionEvent.rotationRate* - An object giving the rate of change of the device's orientation on the three orientation axis alpha, beta and gamma. Rotation rate is expressed in degrees per seconds.
+ *DeviceMotionEvent.interval* - A number representing the interval of time, in milliseconds, at which data is obtained from the device.


