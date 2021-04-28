# 
# Resources: CodeBuild
# 
resource "aws_codebuild_project" "uberCI" {
  name          = "uberCI"
  description   = "Build and test uber docker image"
  badge_enabled  = "true"
  service_role  = aws_iam_role.codebuild.arn
  build_timeout = "10"
  

  artifacts {
    type = "NO_ARTIFACTS"
  }

  environment {
    compute_type                = "BUILD_GENERAL1_SMALL"
    image                       = "aws/codebuild/standard:4.0"
    type                        = "LINUX_CONTAINER"
    privileged_mode             = "true"
    //image_pull_credentials_type = "SERVICE_ROLE"
    environment_variable {
      name  = "AWS_ACCOUNT_ID"
      value = "211252803163"
    }
    environment_variable {
      name  = "AWS_REGION"
      value = "us-east-2"
    }
 
    resource {
      type                = "GITHUB"
      location            = "https://github.com/MouryaPratapReddyD/Uber-finalProject.git"
      git_clone_depth     = "1" 
      report_build_status = true
      auth {
        type     = "OAUTH"
        resource = "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"
      }
    } 
  } 
}

resource "aws_codebuild_webhook" "uberCI" {
  project_name = aws_codebuild_project.uberCI.name

}
