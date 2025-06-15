output "s3_prod_bucket_name" {
    value       = aws_s3_bucket.prod_bucket.bucket
    description = "The name of the S3 bucket for production environment."
}

output "github_actions_role_arn" {
    value       = aws_iam_role.prod_github_actions_role.arn
    description = "The ARN of the IAM role for GitHub Actions."
}