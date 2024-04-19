resource "aws_iam_role" "wallet_api_role" {
    name   = "Wallet_API_Role"
    assume_role_policy = jsonencode(
            {
                "Version": "2012-10-17",
                "Statement": [
                {
                    "Action": "sts:AssumeRole",
                    "Principal": {
                    "Service": "lambda.amazonaws.com"
                    },
                    "Effect": "Allow",
                    "Sid": ""
                }
                ]
            }
        )
}