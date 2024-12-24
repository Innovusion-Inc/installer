# Copyright 2016 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file
# except in compliance with the License. A copy of the License is located at
#
#     http://aws.amazon.com/apache2.0/
#
# or in the "license" file accompanying this file. This file is distributed on an "AS IS"
# BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations under the License.
"""
A BitBucket Builds template for deploying an application revision to AWS CodeDeploy
narshiva@amazon.com
v1.0.0
"""
from __future__ import print_function
import boto3
import argparse
import os
import sys


def upload_to_s3(region, bucket, artifact, bucket_key, access_key, secret_key):
    """
    Uploads an artifact to Amazon S3 using credentials
    """
    print("Upload {} to {}/{}/{}".format(artifact, "https://s3-" +
          region + ".amazonaws.com", bucket, bucket_key))
    try:
        client = boto3.client(
            's3',
            region_name=region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key
        )
    except ClientError as err:
        print("Failed to create boto3 client.\n" + str(err))
        return False
    try:
        client.put_object(
            Body=open(artifact, 'rb'),
            Bucket=bucket,
            Key=bucket_key
        )
    except ClientError as err:
        print("Failed to upload artifact to S3.\n" + str(err))
        return False
    except IOError as err:
        print("Failed to access artifact in this directory.\n" + str(err))
        return False
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--bucket", help="Name of the existing S3 bucket", default="iv-release")
    parser.add_argument("--artifact", nargs='+',
                        help="Names of the artifact to be uploaded to S3")
    parser.add_argument(
        "--bucket_key", help="Name of the S3 Bucket key", default="perception/virtualloop/")
    parser.add_argument("--region", help="AWS Region", default="us-west-2")
    parser.add_argument("--access_key", help="AWS access key ID")
    parser.add_argument("--secret_key", help="AWS secret access key")
    args = parser.parse_args()

    access_key = os.getenv('AWS_ACCESS_KEY_ID') or args.access_key
    secret_key = os.getenv('AWS_SECRET_ACCESS_KEY') or args.secret_key

    if not access_key or not secret_key:
        sys.exit(
            "Access key and secret key not provided. Set them as environment variables or provide them as arguments.")

    print("total files to upload {}".format(len(args.artifact)))
    for f in args.artifact:
        full_key = args.bucket_key + os.path.basename(f)
        if not upload_to_s3(args.region, args.bucket, f, full_key, access_key, secret_key):
            sys.exit(1)


if __name__ == "__main__":
    main()
