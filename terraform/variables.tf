data "aws_caller_identity" "current" {}

variable "MONGO_URI" {
    type = string
    sensitive = true
}

variable "PG_USER" {
    type = string
    sensitive = true
}

variable "PG_PASS" {
    type = string
    sensitive = true
}

variable "PG_HOST" {
    type = string
    sensitive = true
}

variable "PG_DB" {
    type = string
    sensitive = true
}

variable "PG_SSL" {
    type = string
    sensitive = false
}

variable "environment" {
    type = string
    sensitive = false
}