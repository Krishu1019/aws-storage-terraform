# Serverless Secure File Storage on AWS (Terraform)

A private S3-based file storage service built entirely with Terraform. Users upload and download files through short-lived presigned URLs issued by an API, so the bucket is never public.

## Architecture

```
Client
  |  GET /url?key=file.txt&action=upload|download
  v
API Gateway (HTTP API)
  |
  v
Lambda (Python) -- creates presigned URL (expires in 5 min)
  |
  v
Client --(presigned URL)--> S3 bucket (private, encrypted, versioned)
```

## AWS services

- **S3**: file storage (public access blocked, AES-256 encryption, versioning, lifecycle rule)
- **Lambda**: generates presigned URLs (Python 3.12)
- **API Gateway (HTTP API)**: public endpoint that triggers the Lambda
- **IAM**: least-privilege role for the Lambda
- **CloudWatch Logs**: Lambda logs
- **S3 backend**: Terraform remote state with native locking

## Security decisions

- Bucket has all public access blocked; direct requests return 403
- The Lambda role can only `GetObject` and `PutObject` on this one bucket
- Presigned URLs expire after 5 minutes
- Server-side encryption (AES-256) and versioning enabled
- Old object versions expire after 30 days
- Terraform state lives in a separate bucket, isolated from user data

## Project structure

```
.
├── providers.tf    # Terraform, provider and S3 backend
├── variables.tf    # region and bucket name
├── s3.tf           # storage bucket and its security settings
├── lambda.tf       # IAM, Lambda, API Gateway
├── outputs.tf      # API URL
└── lambda/
    └── handler.py  # presigned URL logic
```

## Deploy

Requirements: Terraform 1.10+, AWS CLI configured, an S3 bucket for remote state.

```bash
terraform init
terraform plan
terraform apply
```

## Test

```bash
API=$(terraform output -raw api_url)
echo "hello cloud" > hello.txt

# Upload
URL=$(curl -s "$API/url?key=hello.txt&action=upload" | jq -r .url)
curl -X PUT --upload-file hello.txt "$URL"

# Download
URL=$(curl -s "$API/url?key=hello.txt&action=download" | jq -r .url)
curl "$URL"

# Direct access is denied (expect 403)
curl -i https://<bucket-name>.s3.ap-south-1.amazonaws.com/hello.txt
```

## Known limitations and next steps

- The API has no authentication yet; anyone with the URL can request links
- Planned: API authentication, CloudWatch alarm on Lambda errors, GitHub Actions pipeline (fmt, validate, plan) with OIDC

## Clean up

```bash
terraform destroy
```
Empty the bucket first if versioned objects remain.
