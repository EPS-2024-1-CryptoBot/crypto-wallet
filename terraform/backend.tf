terraform {
  backend "s3" {
    bucket          = "cryptobotunb-terraform-${var.environment}-state"
    key             = "terraform/terraform.tfstate"
    region          = "us-east-1"
    dynamodb_table  = "cryptobotunb-terraform-${var.environment}-db"
    encrypt         = true
  }
}