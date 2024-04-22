data "aws_caller_identity" "current" {}

variable "MONGO_URI" {
    type = string
    sensitive = true
}

variable "environment" {
    type = string
    sensitive = false
}