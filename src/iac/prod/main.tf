provider "aws" {
    region = var.aws_region
}

resource "aws_s3_bucket" "prod_bucket" {
    bucket = var.prod_bucket_name

    tags = {
        Name        = "Prod Data Bucket"
        Environment = "Production"
    }
}