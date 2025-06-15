variable "aws_region" {
    description = "The AWS region to deploy resources in"
    type        = string
    default     = "eu-west-3" # Paris
}

variable "bucket_name" {
    description = "The name of the S3 bucket [PRODUCTION]."
    type        = string
    default     = "prod-lp-thesis-bucket-25913513"
}

variable "github_actions_role_name" {
    description = "The name of the IAM role for GitHub Actions."
    type        = string
    default     = "GitHubActionsRoleProd"
}

variable "account_id" {
    description = "The AWS account ID."
    type        = string
}