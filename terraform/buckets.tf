resource "aws_s3_bucket" "wallet_api_zip" {
  bucket = "${var.environment}-backend-cryptobotunb-${data.aws_caller_identity.current.account_id}"
}

resource "aws_s3_object" "file_upload" {
  bucket      = aws_s3_bucket.wallet_api_zip.id
  key         = "lambda_zip.zip"
  source      = "${path.root}/../lambda_function.zip"
  source_hash = filemd5("${path.root}/../lambda_function.zip")
}