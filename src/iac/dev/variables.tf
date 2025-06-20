variable "aws_region" {
    description = "The AWS region to deploy resources in"
    type        = string
    default     = "eu-west-3" # Paris
}

variable "bucket_name" {
    description = "The name of the S3 bucket [DEVELOPMENT]."
    type        = string
    default     = "dev-lp-thesis-bucket-25913513"
}

variable "github_actions_role_name" {
    description = "The name of the IAM role for GitHub Actions."
    type        = string
    default     = "GitHubActionsRoleDev"
}

variable "account_id" {
    description = "The AWS account ID."
    type        = string
}