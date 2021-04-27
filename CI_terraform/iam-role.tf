resource "aws_iam_role" "codebuild" {
  name               = local.iam_name
  assume_role_policy = data.aws_iam_policy_document.assume_role_policy.json
  path               = var.iam_path
  description        = var.description
  tags               = merge({ "Name" = local.iam_name }, var.tags)
}

data "aws_iam_policy_document" "assume_role_policy" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["codebuild.amazonaws.com"]
    }
  }
}

# https://www.terraform.io/docs/providers/aws/r/iam_policy.html
resource "aws_iam_policy" "codebuild" {
  name        = local.iam_name
  policy      = data.aws_iam_policy_document.policy.json
  path        = var.iam_path
  description = var.description
}

data "aws_iam_policy_document" "policy" {
  statement {
    effect = "Allow"

    actions = [
      "logs:CreateLogGroup",
      "logs:CreateLogStream",
      "logs:PutLogEvents",
    ]

    resources = [
      local.log_group_arn,
      "${local.log_group_arn}:*",
    ]
  }

  statement {
    effect = "Allow"

    actions = [
      "s3:PutObject",
      "s3:GetObject",
      "s3:GetObjectVersion",
      "s3:GetBucketAcl",
      "s3:GetBucketLocation"
    ]

    resources = [
      var.artifact_bucket_arn,
      "${var.artifact_bucket_arn}/*",
    ]
  }
  statement {
    effect = "Allow"
    
    actions= [
        "codebuild:CreateReportGroup",
        "codebuild:CreateReport",
        "codebuild:UpdateReport",
        "codebuild:BatchPutTestCases",
        "codebuild:BatchPutCodeCoverages"
         ]

    resources = [
      "arn:aws:codebuild:us-east-1:211252803163:report-group/uberCI-*",
    ]
  }
}

# https://www.terraform.io/docs/providers/aws/r/iam_role_policy_attachment.html
resource "aws_iam_role_policy_attachment" "codebuild" {
  role       = aws_iam_role.codebuild.name
  policy_arn = aws_iam_policy.codebuild.arn
}

resource "aws_iam_role_policy_attachment" "EC2" {
  role       = aws_iam_role.codebuild.name
  policy_arn = var.ecr_access_policy_arn1
}

resource "aws_iam_role_policy_attachment" "ECR" {
  role       = aws_iam_role.codebuild.name
  policy_arn = var.ecr_access_policy_arn2
}

# ECR provides several managed policies that you can attach to IAM users or EC2 instances
# that allow differing levels of control over Amazon ECR resources and API operations.
# https://docs.aws.amazon.com/AmazonECR/latest/userguide/ecr_managed_policies.html
resource "aws_iam_role_policy_attachment" "ecr" {
  count = var.enabled_ecr_access ? 1 : 0

  role       = aws_iam_role.codebuild.name
  policy_arn = var.ecr_access_policy_arn
}

locals {
  iam_name      = "${var.name}-codebuild"
  log_group_arn = "arn:aws:logs:${local.region}:${local.account_id}:log-group:/aws/codebuild/${var.name}"

  region     = data.aws_region.current.name
  account_id = data.aws_caller_identity.current.account_id
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}
