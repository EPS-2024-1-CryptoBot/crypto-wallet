import boto3


def retrieve_parameter(parameter_name):
    ssm_client = boto3.client("ssm")
    response = ssm_client.get_parameter(Name=parameter_name, WithDecryption=True)
    return response["Parameter"]["Value"]


if __name__ == "__main__":  # pragma: no cover
    parameter_value = retrieve_parameter("your-parameter-name")
    print(parameter_value)
