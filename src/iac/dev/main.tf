provider "aws" {
    region = var.aws_region
}

resource "aws_s3_bucket" "dev_bucket" {
    bucket = var.bucket_name
    force_destroy = true

    tags = {
        Name        = "Dev Data Bucket"
        Environment = "Development"
    }
}

resource "aws_s3_bucket_public_access_block" "dev_bucket_block" {
    bucket = aws_s3_bucket.dev_bucket.id

    block_public_acls       = true
    block_public_policy     = true
    ignore_public_acls      = true
    restrict_public_buckets = true
}


resource "aws_s3_object" "training_data" {
    bucket = aws_s3_bucket.dev_bucket.bucket
    key = "training_data/*"
    source = "/dev/null"
}


resource "aws_s3_object" "inference_input_data" {
    bucket = aws_s3_bucket.dev_bucket.bucket
    key = "inference_data/input_data/*"
    source = "/dev/null"
}

resource "aws_s3_object" "inference_output_data" {
    bucket = aws_s3_bucket.dev_bucket.bucket
    key = "inference_data/output_data/*"
    source = "/dev/null"
}


resource "aws_iam_role" "dev_github_actions_role" {
    name = var.github_actions_role_name

    assume_role_policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Action = [
                    "sts:AssumeRole",
                    "sts:TagSession",
                ],
                Effect = "Allow"
                Principal = {
                    AWS: "arn:aws:iam::${var.account_id}:user/github_actions_robot"
                }
            }
        ]
    })

    tags = {
        Environment = "Development"
    }
}

resource "aws_iam_policy" "github_actions_robot_policy" {
    name = "github_actions_robot_policy"
    description = "Policy for GitHub Actions Robot to access development resources"
    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Action = [
                    "sts:AssumeRole",
                    "sts:TagSession",
                ],
                Resource = "arn:aws:iam::${var.account_id}:role/${aws_iam_role.dev_github_actions_role.name}"
            }
        ]
    })
}

resource "aws_iam_policy" "dev_github_actions_policy" {
    name = "dev_policy"
    description = "Policy for development S3"
    policy = jsonencode({
        Version = "2012-10-17"
        Statement = [
            {
                Effect = "Allow"
                Action = [
                    "s3:ListBucket",
                    "s3:GetObject",
                    "s3:PutObject",
                    "s3:DeleteObject"
                ],
                Resource = [
                    aws_s3_bucket.dev_bucket.arn,
                    "${aws_s3_bucket.dev_bucket.arn}/*"
                ]

            }
        ]
    })
}

resource "aws_iam_user_policy_attachment" "dev_github_actions_robot_policy_attach" {
    user       = "github_actions_robot"
    policy_arn = aws_iam_policy.github_actions_robot_policy.arn
}

resource "aws_iam_role_policy_attachment" "github_actions_policy_attach" {
    role       = aws_iam_role.dev_github_actions_role.name
    policy_arn = aws_iam_policy.dev_github_actions_policy.arn
}