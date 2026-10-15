import boto3
import hmac
import json
import os
from botocore.config import Config

s3 = boto3.client("s3", region_name="ap-south-1",
                  config=Config(signature_version="s3v4"))
BUCKET = os.environ["BUCKET_NAME"]
API_KEY = os.environ["API_KEY"]


def handler(event, context):
    headers = event.get("headers") or {}
    supplied = headers.get("x-api-key", "")
    if not hmac.compare_digest(supplied, API_KEY):
        return {"statusCode": 401, "body": json.dumps({"error": "unauthorized"})}

    params = event.get("queryStringParameters") or {}
    key = params.get("key")
    action = params.get("action", "upload")

    if not key:
        return {"statusCode": 400, "body": json.dumps({"error": "key is required"})}

    method = "put_object" if action == "upload" else "get_object"
    url = s3.generate_presigned_url(
        method, Params={"Bucket": BUCKET, "Key": key}, ExpiresIn=300
    )
    return {"statusCode": 200, "body": json.dumps({"url": url})}
