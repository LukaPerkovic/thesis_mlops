variable "aws_region" {
    description = "The AWS region to deploy resources in"
    type        = string
    default     = "eu-west-3" # Paris
}

variable "prod_bucket_name" {
    description = "The name of the S3 bucket [PRODUCTION]."
    type        = string
    default     = "prod-lp-thesis-bucket-25913513"
}