Title: Headful Browser with Xvfb on AWS Lambda
Date: 2021-01-18 20:01
Category: Tutorials
Tags: AWS Lambda, Xvfb
Slug: run-Xvfb-on-AWS-Lambda
Author: Nikolai Tschacher
Summary: In this tutorial I demonstrate how to launch Headful Browsers with Xvfb on AWS Lambda

### Introduction

In this quick tutorial, I will demonstrate how to run a headful browser on AWS Lambda with a Xvfb server.

Sometimes headless browsers are not enough. Sometimes you need a browser that is indistinguishable from a real browser.

We will make use of [this very helpful information](https://gist.github.com/cpsubrian/3aa40f6f3d6ce2c707b9d8e34c652dcf#gistcomment-3553963). 

Since December 2020, it is possible to run [containers in AWS Lambda](https://aws.amazon.com/blogs/aws/new-for-aws-lambda-container-image-support/). Here is a link to the [development documents](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html).

Aws Lambda base images: https://github.com/aws/aws-lambda-base-images/tree/nodejs12.x

Read this guide completely: https://docs.aws.amazon.com/lambda/latest/dg/images-create.html

https://docs.aws.amazon.com/lambda/latest/dg/lambda-images.html

https://hub.docker.com/r/amazon/aws-lambda-nodejs

https://hub.docker.com/r/amazon/aws-lambda-nodejs

This is the docker file `Dockerfile`:

```Bash
FROM ubuntu:18.04

RUN apt-get update
RUN DEBIAN_FRONTEND=noninteractive apt-get -y install unzip wget xvfb \
 libcairo2-dev libjpeg-dev libpango1.0-dev libgif-dev build-essential g++ libgl1-mesa-dev libxi-dev \
 libx11-dev dbus-x11 pulseaudio curl udev google-chrome-stable

RUN DEBIAN_FRONTEND=noninteractive apt -y install dirmngr apt-transport-https lsb-release ca-certificates

RUN curl -sL https://deb.nodesource.com/setup_12.x | sudo -E bash -
RUN node --version

COPY entry.sh app.js /
RUN chmod 755 /entry.sh

ENTRYPOINT [ "/entry.sh" ]
CMD [ "app.lambdaHandler" ]
```

And this is the entry point script `entry.sh`:

```Bash
#!/bin/sh

# launch Xvfb server
nohup Xvfb :99 -ac -screen 0 1920x1080x24 -nolisten tcp &

# launch google chrome browser
google-chrome-stable --remote-debugging-port=9222 --no-first-run --no-default-browser-check 2> browser.log &
```

### Steps

We are following the [instructions here](https://docs.aws.amazon.com/lambda/latest/dg/images-create.html).

Build the docker image with:

```
docker build -t lambda-xvfb .   
```

We get the output: `Successfully tagged lambda-xvfb:latest`

Test the container with:

```
docker container run lambda-xvfb
```

Authenticate the Docker CLI to your Amazon ECR registry.

Change the region `us-east-1` to your region.
Change the AWS account ID `123456789012` to your AWS id.

```
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789012.dkr.ecr.us-east-1.amazonaws.com    
```

Tag your image to match your repository name, and deploy the image to Amazon ECR using the docker push command.

```
docker tag  hello-world:latest 123456789012.dkr.ecr.us-east-1.amazonaws.com/hello-world:latest
docker push 123456789012.dkr.ecr.us-east-1.amazonaws.com/hello-world:latest 
```