---
title : Pipeline Architecture
description : Architecture diagrams and pipeline components.
weight : 2
---

## Pipeline Architecture 

Under the hood, Git Docs is powered by AWS.

At its core it is a set of [AWS Lambda](https://aws.amazon.com/lambda/) functions which are configured (via [CloudWatch Events](https://docs.aws.amazon.com/AmazonCloudWatch/latest/events/WhatIsCloudWatchEvents.html)) to trigger periodically and publish any documentation changes to a hosted S3 Bucket. 

In chronological order, the AWS services utilized are:

1. CloudWatch Events trigger our Lambda function 

2. Lambda function executes pushing updated site to S3

3. S3 is configured to host, making changes live immediately

4. Execution logs are written to CloudWatch Logs

