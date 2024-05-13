resource "aws_lambda_function" "terraform_lambda_func" {
    s3_bucket                      = aws_s3_bucket.wallet_api_zip.id
    s3_key                         = aws_s3_object.file_upload.key
    function_name                  = "Wallet_API_Backend"
    role                           = aws_iam_role.wallet_api_role.arn
    handler                        = "main.handler"
    runtime                        = "python3.8"
    depends_on                     = [aws_iam_role_policy_attachment.Wallet_API_Attach]
    source_code_hash               = base64sha256(aws_s3_object.file_upload.key)
    timeout                        = 30

    environment {
        variables = {
            MONGO_URI = var.MONGO_URI
            PG_USER = var.PG_USER
            PG_PASS = var.PG_PASS
            PG_HOST = var.PG_HOST
            PG_DB = var.PG_DB
        }
    }
}

resource "aws_lambda_function" "terraform_rsa_keygen" {
    s3_bucket                      = aws_s3_bucket.wallet_api_zip.id
    s3_key                         = aws_s3_object.file_upload.key
    function_name                  = "RSA_KeyGen_API"
    role                           = aws_iam_role.wallet_api_role.arn
    handler                        = "encryption.handler"
    runtime                        = "python3.8"
    depends_on                     = [aws_iam_role_policy_attachment.Wallet_API_Attach]
    source_code_hash               = base64sha256(aws_s3_object.file_upload.key)
    timeout                        = 10
}