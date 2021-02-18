Title: Why does this Website know that I am sitting on the Toilet?
Date: 2021-02-05 22:17
Modified: 2021-02-18 22:17
Category: Security
Tags: JavaScript, deviceorientation, devicemotion
Slug: why-does-this-website-know-i-am-sitting-on-the-toilet
Author: Nikolai Tschacher
Summary: Android mobile devices give to any website device orientation and device motion data. This data is quite sensitive in nature and should not be granted to websites without obtaining explicit user consent.

Android smartphones grant websites access to the [deviceorientation](https://developer.mozilla.org/en-US/docs/Web/API/Window/deviceorientation_event) and the [devicemotion](https://developer.mozilla.org/en-US/docs/Web/API/Window/devicemotion_event) events.

Those events basically give information about the current smartphone motion data and rotation angels. This data comes from the built-in accelerometer, gyroscope, and compass in mobile devices.

So if you are visiting this website from your Android mobile phone, you can see your device motion data in the box below.

<div id="exmaple">

<strong>`deviceorientation` events</strong>
<pre id="deviceorientationOutput">{}</pre>

<hr />

<strong>`devicemotion` events</strong>
<pre id="devicemotionOutput">{}</pre>

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
      // 0.5 m/s2 in one of the axises
      if (Math.abs(x) > 0.5 || Math.abs(y) > 0.5 || Math.abs(z) > 0.5) {
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
    // only consider significant changes in rotation
    if (Math.abs(self.alpha - event.alpha) < 1 
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

### Sensitive Nature of Motion and Orientation Data

The nature motion and orientation data can possibly reveal a lot about your real live behavior. Some of the following information can be interpolated by interpreting motion and orientation data of your smartphone:

+ In what position your are interacting with the website: Sitting, lying, standing, running, ...
+ Whether you are moving around while looking at the website
+ If your smartphone is falling down (excellent point to backup some data)

For example, if you follow a video conference with your Android Smartphone or Tablet while lying in your bed, it would be possible to infer from the device orientation and motion data that you are lying in your bed, even though you disabled your camera and microphone preemptively...

Apple has a clear stance regarding the `deviceorientation` and `devicemotion` event on their iOS platform: They are [disabled by default](https://www.macrumors.com/2019/02/04/ios-12-2-safari-motion-orientation-access-toggle/) and a website needs to [ask for permission in order to use them](https://dev.to/li/how-to-requestpermission-for-devicemotion-and-deviceorientation-events-in-ios-13-46g2). Why is this not the case on the Android operating system?

### The `deviceorientation` Event

This event yields a [DeviceOrientationEvent](https://developer.mozilla.org/en-US/docs/Web/API/DeviceOrientationEvent) every 10ms. This event includes the following information:

+ `DeviceOrientationEvent.absolute` - A boolean that indicates whether or not the device is providing orientation data absolutely.
+ `DeviceOrientationEvent.alpha` -  A number representing the motion of the device around the z axis, express in degrees with values ranging from 0 (inclusive) to 360 (exclusive).

+ `DeviceOrientationEvent.beta` -  A number representing the motion of the device around the x axis, express in degrees with values ranging from -180 (inclusive) to 180 (exclusive). This represents a front to back motion of the device.
+ `DeviceOrientationEvent.gamma` -  A number representing the motion of the device around the y axis, express in degrees with values ranging from -90 (inclusive) to 90 (exclusive). This represents a left to right motion of the device.

<figure>
    <img src="/images/deviceorientation.png" alt="deviceorientation" style="width:800px" />
    <figcaption>Illustration of the device orientation (Dev Tools Simulator)</figcaption>
</figure>

### The `devicemotion` Event

This event yields a [`DeviceMotionEvent`](https://developer.mozilla.org/en-US/docs/Web/API/DeviceMotionEvent) every 10ms. This event includes the following information:

+ `DeviceMotionEvent.acceleration` - An object giving the acceleration of the device on the three axis X, Y and Z. Acceleration is expressed in m/s2.
+ `DeviceMotionEvent.accelerationIncludingGravity` - An object giving the acceleration of the device on the three axis X, Y and Z with the effect of gravity. Acceleration is expressed in m/s2.
+ `DeviceMotionEvent.rotationRate` - An object giving the rate of change of the device's orientation on the three orientation axis alpha, beta and gamma. Rotation rate is expressed in degrees per seconds.
+ `DeviceMotionEvent.interval` - A number representing the interval of time, in milliseconds, at which data is obtained from the device.


