resource "aws_iam_policy" "wallet_api_policy" {
    name         = "Wallet_API_Policy"
    path         = "/"
    description  = "AWS IAM Policy for managing aws lambda role"
    policy = jsonencode(
        {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": [
                    "logs:CreateLogGroup",
                    "logs:CreateLogStream",
                    "logs:PutLogEvents",
                    ],
                    "Resource": "arn:aws:logs:*:*:*",
                    "Effect": "Allow"
                },
                {
                    "Effect": "Allow",
                    "Action": [
                        "lambda:*",
                    ],
                    "Resource": "*"
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

resource "aws_iam_role_policy_attachment" "Wallet_API_Attach" {
 role        = aws_iam_role.wallet_api_role.name
 policy_arn  = aws_iam_policy.wallet_api_policy.arn
}

resource "aws_iam_role_policy_attachment" "AWSLambdaVPCAccessExecutionRole" {
 role       = aws_iam_role.wallet_api_role.name
 policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaVPCAccessExecutionRole"
}