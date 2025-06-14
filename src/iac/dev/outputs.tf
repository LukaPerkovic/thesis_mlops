output "s3_dev_bucket_name" {
    value       = aws_s3_bucket.dev_bucket.bucket
    description = "The name of the S3 bucket for develpment environment."
}