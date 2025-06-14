provider "aws" {
    region = var.aws_region
}

resource "aws_s3_bucket" "dev_bucket" {
    bucket = var.dev_bucket_name

    tags = {
        Name        = "Dev Data Bucket"
        Environment = "Development"
    }
}