Title: Dynamic creation of S3 buckets in many regions
Date: 2020-02-26 17:50
Category: Scripts
Tags: AWS, S3, Buckets
Slug: dynamic-s3-bucket-creation-in-many-regions
Author: Nikolai Tschacher
Summary: Quick script that demonstrates how to create s3 buckets in many regions.

## Create S3 buckets dynamically with a bash script

The script below creates S3 buckets in the AWS regions that are specified at the beginning of the script.
 
 Just edit the array named `regions` and modify the slug and the script will create buckets in the form `{slug}-{aws-region}` in all the regions specified.

```bash
#!/usr/bin/env bash

# create_s3_buckets.sh
# Author: Nikolai Tschacher

regions=(us-east-2 us-east-1 eu-central-1 eu-west-1 eu-west-2 eu-west-3)

for region in "${regions[@]}"
do
    # specify your bucket name here
    bname="slug-$region"

    echo "creating $bname aws bucket"

    # https://docs.aws.amazon.com/cli/latest/reference/s3api/create-bucket.html#examples
    if [[ "$region" == "us-east-1" ]]; then
        aws s3api create-bucket --bucket $bname --region $region --acl private
    else
        aws s3api create-bucket --bucket $bname --region $region --acl private --create-bucket-configuration LocationConstraint=$region
    fi
done
```

Run the script with the following commands:

```bash
chmod +x create_s3_buckets.sh
./create_s3_buckets.sh
```