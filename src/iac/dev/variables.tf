variable "aws_region" {
    description = "The AWS region to deploy resources in"
    type        = string
    default     = "eu-west-3" # Paris
}

variable "dev_bucket_name" {
    description = "The name of the S3 bucket [DEVELOPMENT]."
    type        = string
    default     = "dev-lp-thesis-bucket-25913513"
}