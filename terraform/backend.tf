terraform {
  backend "s3" {
    bucket          = "cryptobotunb-terraform-prod-state"
    key             = "terraform/terraform.tfstate"
    region          = "us-east-1"
    dynamodb_table  = "cryptobotunb-terraform-prod-db"
    encrypt         = true
  }
}