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
                },
                {
                    "Effect": "Allow",
                    "Action": "ssm:GetParameter",
                    "Resource": [
                        "arn:aws:ssm:us-east-1:381492146586:parameter/BACKEND_PUB_K",
                        "arn:aws:ssm:us-east-1:381492146586:parameter/BACKEND_PVT_K"
                    ]
                }
                ]
            }
        )
}