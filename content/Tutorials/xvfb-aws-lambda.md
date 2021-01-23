Title: Headful Google Chrome with Xvfb on AWS Lambda Container
Date: 2021-01-23 14:40
Category: Tutorials
Tags: AWS Lambda, Xvfb, Docker, Container
Slug: run-xvfb-on-aws-lambda-container
Author: Nikolai Tschacher
Summary: The following write-up is an attempt to launch headful Google Chrome with Xvfb on AWS Lambda container.

### Introduction

In this quick tutorial, it is attempted to run **headful** Google Chrome on AWS Lambda with the `Xvfb` virtual display framebuffer server.

Sometimes headless browsers are not enough. Sometimes you need a browser that is indistinguishable from a real browser and 
it needs to run with a virtual frame buffer. The goal of this article is to run the Google Chrome browser in AWS Lambda with `Xvfb` using a Docker container.

Since December 2020, it is now possible to run [Docker images in AWS Lambda](https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/). You now have full support over the operating system stack, as long
as your container either derives a AWS Lambda base image or it implements the Lambda runtime API.

### What works

Running the specifically for AWS Lambda compiled chromium browser from the project [chrome-aws-lambda](https://github.com/alixaxel/chrome-aws-lambda) seems to work fine with Lambda Docker.

This is the Dockerfile:

```Dockerfile
FROM public.ecr.aws/lambda/nodejs:12

RUN mkdir /app
WORKDIR /app

COPY package*.json /app/
RUN npm install
COPY run.js /app/

CMD ["/app/run.handler"]
```

This is the package.json:

```json
{
  "name": "lambda-container",
  "version": "1.0.0",
  "description": "",
  "main": "run.js",
  "scripts": {
    "test": "echo \"Error: no test specified\" && exit 1"
  },
  "author": "",
  "license": "ISC",
  "dependencies": {
    "chrome-aws-lambda": "^5.5.0",
    "puppeteer-core": "^5.5.0"
  }
}

```

This is `run.js`:

```JavaScript
const chromium = require('chrome-aws-lambda');

exports.handler = async (event, context, callback) => {
  let result = null;
  let browser = null;

  try {
    browser = await chromium.puppeteer.launch({
      args: chromium.args,
      defaultViewport: chromium.defaultViewport,
      executablePath: await chromium.executablePath,
      headless: false, // we will use headful chrome
      ignoreHTTPSErrors: true,
    });

    let page = await browser.newPage();

    await page.goto(event.url || 'https://bot.incolumitas.com');

    await page.waitFor(3000);

    const new_tests = JSON.parse(await page.$eval('#new-tests', el => el.textContent));
    const old_tests = JSON.parse(await page.$eval('#detection-tests', el => el.textContent));

    result = JSON.stringify({
      new_tests: new_tests,
      old_tests: old_tests,
    }, null, 2);
  } catch (error) {
    return callback(error);
  } finally {
    if (browser !== null) {
      await browser.close();
    }
  }

  return callback(null, result);
};
```

### Build the Container

We are following the build [instructions here](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html).

First, build the docker image with:

```bash
docker build -t headful-test .
```

In case everything works, get the output: `Successfully tagged headful-test:latest`

Then test the container with:

```bash
docker container run headful-test
```

### Deploy the container to AWS Lambda

Authenticate the Docker CLI to your Amazon ECR registry.

**Update your credentials**:

+ Change the region `us-east-1` to your AWS region.
+ Change the AWS account ID `123456789012` to your AWS ID.

First login to AWS

```bash
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com   
```

Now we have to create a registry for our docker image: 

```bash
aws ecr create-repository --repository-name headful-test --image-scanning-configuration scanOnPush=true
```

Tag your image to match your repository name, and deploy the image to Amazon ECR using the docker push command.

```bash
docker tag headful-test:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/headful-test:latest

docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/headful-test:latest
```

### Google Chrome with Xvfb fails

However, if we try to run `Xvfb` with `google-chrome-stable`, we are not successful in running
it on AWS Lambda Docker.

This is the Dockerfile:

```Dockerfile
FROM public.ecr.aws/lambda/nodejs:12

# Install Xvfb
RUN yum update -y && \
    yum install -y bzip2 gtk3 dbus-glib libXt xorg-x11-server-Xvfb ImageMagick xz procps

# Install latest Google Chrome browser
RUN curl -o chrome.rpm https://dl.google.com/linux/direct/google-chrome-stable_current_x86_64.rpm
RUN yum install -y chrome.rpm

RUN mkdir /app
WORKDIR /app

COPY package*.json /app/
RUN npm install
COPY run.js /app/

# Required for Xvfb
ENV DISPLAY=":99.0"

CMD ["/app/run.handler"]
```

And this is `run.js`:


```JavaScript
const chromium = require('chrome-aws-lambda');
const exec = require('child_process').exec;

/**
 * Executes a shell command and return it as a Promise.
 * @param cmd {string}
 * @return {Promise<string>}
 */
function execShellCommand(cmd) {
  return new Promise((resolve, reject) => {
   exec(cmd, (error, stdout, stderr) => {
    if (error) {
     console.warn(error);
    }
    resolve(stdout? stdout : stderr);
   });
  });
}

exports.handler = async (event, context, callback) => {
  // Attempt to launch Xvfb
  let output = await execShellCommand('Xvfb :99 -ac -screen 0 1024x768x24 -nolisten tcp &');
  console.log(output);

  let result = null;
  let browser = null;

  try {
    browser = await chromium.puppeteer.launch({
      args: chromium.args,
      defaultViewport: chromium.defaultViewport,
      executablePath: 'google-chrome-stable',
      headless: false, // we will use headful chrome
      ignoreHTTPSErrors: true,
    });

    let page = await browser.newPage();

    await page.goto(event.url || 'https://bot.incolumitas.com');

    await page.waitFor(4000);

    const new_tests = JSON.parse(await page.$eval('#new-tests', el => el.textContent));
    const old_tests = JSON.parse(await page.$eval('#detection-tests', el => el.textContent));

    result = JSON.stringify({
      new_tests: new_tests,
      old_tests: old_tests,
    }, null, 2);
  } catch (error) {
    return callback(error);
  } finally {
    if (browser !== null) {
      await browser.close();
    }
  }

  return callback(null, result);
};
```

We get the following error message when attempting to run on AWS Lambda:

```json
{
"errorType": "Error",
"errorMessage": "Failed to launch the browser process!\nmkdir: cannot create directory ‘/.local’: Read-only file system\ntouch: cannot touch ‘/.local/share/applications/mimeapps.list’: No such file or directory\n/usr/bin//google-chrome-stable: line 45: /dev/fd/62: No such file or directory\n/usr/bin//google-chrome-stable: line 46: /dev/fd/62: No such file or directory\n[25:25:0123/133757.218681:ERROR:browser_main_loop.cc(585)] Failed to open an X11 connection.\n[25:25:0123/133757.220449:ERROR:browser_main_loop.cc(1438)] Unable to open X display.\n[25:25:0123/133757.555175:ERROR:service_utils.cc(157)] --ignore-gpu-blacklist is deprecated and will be removed in 2020Q4, use --ignore-gpu-blocklist instead.\n\n\nTROUBLESHOOTING: https://github.com/puppeteer/puppeteer/blob/main/docs/troubleshooting.md\n",
"stack": [
     "Error: Failed to launch the browser process!",
     "mkdir: cannot create directory ‘/.local’: Read-only file system",
     "touch: cannot touch ‘/.local/share/applications/mimeapps.list’: No such file or directory",
     "/usr/bin//google-chrome-stable: line 45: /dev/fd/62: No such file or directory",
     "/usr/bin//google-chrome-stable: line 46: /dev/fd/62: No such file or directory",
     "[25:25:0123/133757.218681:ERROR:browser_main_loop.cc(585)] Failed to open an X11 connection.",
     "[25:25:0123/133757.220449:ERROR:browser_main_loop.cc(1438)] Unable to open X display.",
     "[25:25:0123/133757.555175:ERROR:service_utils.cc(157)] --ignore-gpu-blacklist is deprecated and will be removed in 2020Q4, use --ignore-gpu-blocklist instead.",
     "",
     "",
     "TROUBLESHOOTING: https://github.com/puppeteer/puppeteer/blob/main/docs/troubleshooting.md",
     "",
     "    at onClose (/app/node_modules/puppeteer-core/lib/cjs/puppeteer/node/BrowserRunner.js:193:20)",
     "    at Interface.<anonymous> (/app/node_modules/puppeteer-core/lib/cjs/puppeteer/node/BrowserRunner.js:183:68)",
     "    at Interface.emit (events.js:326:22)",
     "    at Interface.close (readline.js:416:8)",
     "    at Socket.onend (readline.js:194:10)",
     "    at Socket.emit (events.js:326:22)",
     "    at endReadableNT (_stream_readable.js:1241:12)",
     "    at processTicksAndRejections (internal/process/task_queues.js:84:21)"
]
}
```

Several different things were tried (See resources below), nothing worked.

### Resources & Links

[Gist attempting to do the same on Ubuntu 18.04](https://gist.github.com/cpsubrian/3aa40f6f3d6ce2c707b9d8e34c652dcf#gistcomment-3553963). 

[Aws Lambda base images](https://github.com/aws/aws-lambda-base-images/tree/nodejs12.x)

[Some blog article](https://acloudguru.com/blog/engineering/packaging-aws-lambda-functions-as-container-images)

[Another blog article](https://aripalo.com/blog/2020/aws-lambda-container-image-support/)

Some other, related projects:

[docker-chromium-xvfb](https://github.com/atlassian/docker-chromium-xvfb/tree/master/images/base)

[chromium-xvfb-js](https://gallery.ecr.aws/q3b9l9y9/chromium-xvfb-js)

[aws-lambda-xvfb](https://github.com/nisaacson/aws-lambda-xvfb)

[Container Image Support in AWS Lambda Deep Dive](https://dev.to/eoinsha/container-image-support-in-aws-lambda-deep-dive-2keh)

[Lambda Image Page Recorder](https://github.com/fourTheorem/lambda-image-page-record)

[A very recent discussion on stack overflow](https://stackoverflow.com/questions/65429877/aws-lambda-container-running-selenium-with-headless-chrome-works-locally-but-not)