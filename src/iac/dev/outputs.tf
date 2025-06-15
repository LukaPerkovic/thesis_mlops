output "s3_dev_bucket_name" {
    value       = aws_s3_bucket.dev_bucket.bucket
    description = "The name of the S3 bucket for develpment environment."
}

output "github_actions_role_arn" {
    value       = aws_iam_role.dev_github_actions_role.arn
    description = "The ARN of the IAM role for GitHub Actions."
}