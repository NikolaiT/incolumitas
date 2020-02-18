Title: Scraping with puppeteer and headless chrome deployed to AWS Lambda
Date: 2019-8-31 22:30
Category: Scraping
Tags: puppeteer, web scraping, AWS lambda, headless chrome
Slug: web-scraping-puppeteer-aws-lambda
Author: Nikolai Tschacher
Summary: In this blog post, we demonstrate how a web scraping function is deployed to the AWS cloud with puppeteer and headless chrome.

One of the most pressing issues with web scraping/crawling is the part where you get detected and blocked from the website. When scraping is implemented with raw http requests, it is usually pretty straightforward to detect the scraper by delivering a piece of javascript, that when not executed with a modern javascript engine, blocks all further access. There are a myriad of other strategies to distinguish bots from real human beings (Captchas, mouse movement, rendering functionality, ...). For those reasons, it is usually a smart idea to use a real browser such as headless chrome to accomplish web scraping projects.

This comes with the benefits of simplicity. It is much simpler to handle login functionality and complex browsing actions by programming a real web browser. The library to control headless chrome is called [puppeteer](https://github.com/GoogleChrome/puppeteer).

In this short blog post, it is demonstrated how a simple Google Scraper can be deployed to the AWS cloud. All you need is some knowledge of Javascript, an AWS account and one hour of your time. In the you will have a scraper that allows you to scrape any keywords on Google. The huge advantage of deploying the scraping is to the cloud. You can massively parallelize your crawling/scraping algorithms. 

All code can be found in the [respective GitHub repository](https://github.com/NikolaiT/aws-scraper-example).

## Setting up the project

The required javascript libraries are `user-agents`, `chrome-aws-lambda`, `aws-sdk` and `puppeteer-core`. You can install them with the `npm` node package manager. Alternatively, you can clone the [following git repository]() where I have already setup everything. You also need to install the serverless package globally. You can [read up the instructions here how to do so](https://serverless.com/framework/docs/providers/aws/guide/quick-start/).

After you cloned the repository with the command `git clone git@github.com:NikolaiT/aws-scraper-example.git`, it is time to setup you AWS credentials. Enter them into the file `.env`. The `.env` file has the following boilerplate structure: 

```text
export AWS_ACCESS_KEY=
export AWS_SECRET_KEY=
export AWS_REGION=us-east-1
export AWS_PROFILE=
export AWS_FUNCTION_URN=
```

you need to enter the user and secret key credentials that you received when you created your AWS account. After that, you are all set to deploy the scraper to AWS Lambda cloud:

```bash
source .env
serverless deploy
```

After a successful deployment, `serverless` outputs a message such as the following:

```bash
$ serverless deploy
Serverless: Packaging service...
Serverless: Excluding development dependencies...
Serverless: Creating Stack...
Serverless: Checking Stack create progress...
.....
Serverless: Stack create finished...
Serverless: Uploading CloudFormation file to S3...
Serverless: Uploading artifacts...
Serverless: Uploading service google-aws-scraper.zip file to S3 (39.4 MB)...
Serverless: Validating template...
Serverless: Updating Stack...
Serverless: Checking Stack update progress...
...............
Serverless: Stack update finished...
Service Information
service: google-aws-scraper
stage: dev
region: us-east-1
stack: google-aws-scraper-dev
resources: 5
api keys:
  None
endpoints:
  None
functions:
  google-aws-scraper: google-aws-scraper-dev-google-aws-scraper
layers:
  None
Serverless: Run the "serverless" command to setup monitoring, troubleshooting and testing
```

Now you need to update the `.env` file with the correct function name of your deployed scraper. You can look up the function name in the AWS console in the Lambda tab of the correct region.

## Testing the cloud scraper

After the successful lambda function deployment, we can test if it is possible to search google with our headless chrome function living in the AWS cloud. For this task, we create a `test.js` script that invokes the AWS function. The test script has the following contents:

```js

var AWS = require('aws-sdk');
const fs = require('fs');

const invokeLambda = (lambda, params) => new Promise((resolve, reject) => {
    lambda.invoke(params, (error, data) => {
        if (error) {
            reject(error);
        } else {
            resolve(data);
        }
    });
});

const main = async () => {
    
    let region = process.env.AWS_REGION;
    let functionURN = process.env.AWS_FUNCTION_URN;
    
    // You shouldn't hard-code your keys in production!
    // http://docs.aws.amazon.com/AWSJavaScriptSDK/guide/node-configuring.html
    AWS.config.update({
        accessKeyId: process.env.AWS_ACCESS_KEY,
        secretAccessKey: process.env.AWS_SECRET_KEY,
        region: region,
    });

    const lambda = new AWS.Lambda();

    let keywords = ['weather berlin', 'news germany', 'what else', 'some keyword'];
    let promises = [];

    for (let kw of keywords) {
        let event = { keyword: kw };
        let params = {
            FunctionName: functionURN,
            InvocationType: "RequestResponse",
            Payload: JSON.stringify(event),
        };
        console.log(params);
        promises.push(
            invokeLambda(lambda, params)
        )
    }

    console.log(`Invoked ${promises.length} lambda requests!`);

    var start = new Date();
    let results = await Promise.all(promises);
    var end = new Date() - start;

    console.log(`invokeLambda() in region ${region} took ${end/1000} seconds`);

    for (let result of results) {
        let data = result.Payload;
        data = JSON.parse(data);
        console.dir(data, {depth: null, colors: true});
        console.log(`invokeLambda() in region ${region} took ${end / 1000} seconds`);
    }
};

main().catch(error => console.error(error));
```

You need to first source the `.env` file with the correct parameters in order for the test script to properly work. After that, execute the test script and the four keywords will be searched on Google via AWS Lambda cloud:

`node test.js`

This command should output four array of urls obtained from the Google SERP.

## Conclusion

In this tutorial we learned how to deploy a scraping function to the AWS Lambda cloud. One big advantage of the cloud is that you only pay for the computing time that your function needed. The free tier includes a large computing volume, such that you may develop whatever your scraping heart desires.

If you want to only focus on the scraping logic and don't want to hassle with scalability issues, intelligent request retries and infrastructure problems, you can direct use the web scraper service on [scrapeulous.com](https://scrapeulous.com/). It comes with many practical examples how to quickly create a scraper of crawler for any website in the Internet.


