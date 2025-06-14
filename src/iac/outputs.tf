output "s3_dev_bucket_name" {
    value       = aws_s3_bucket.dev_data_bucket.bucket
    description = "The name of the S3 bucket for develpment environment."
}


output "s3_prod_bucket_name" {
    value       = aws_s3_bucket.prod_data_bucket.bucket
    description = "The name of the S3 bucket for production environment."
}