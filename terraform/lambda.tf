resource "aws_lambda_function" "terraform_lambda_func" {
    s3_bucket                      = aws_s3_bucket.wallet_api_zip.id
    s3_key                         = aws_s3_object.file_upload.key
    function_name                  = "Wallet_API_Backend"
    role                           = aws_iam_role.wallet_api_role.arn
    handler                        = "main.handler"
    runtime                        = "python3.8"
    depends_on                     = [aws_iam_role_policy_attachment.Wallet_API_Attach]
    source_code_hash               = base64sha256(aws_s3_object.file_upload.key)
    timeout                        = 10

    # vpc_config {
    #     subnet_ids         = [aws_subnet.api_public_subnet.id]
    #     security_group_ids = [aws_security_group.lambda_internet_access_sec_group.id]
    # }

    environment {
        variables = {
            MONGO_URI = var.MONGO_URI
        }
    }
}