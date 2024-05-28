import unittest
from unittest.mock import patch, MagicMock
from wallet.aws import retrieve_parameter


class Test_AWS(unittest.TestCase):

    def test_should_succeed_when(self):
        with patch("boto3.client") as aws_mock:
            ssm_client = MagicMock()
            aws_mock.return_value = ssm_client
            ssm_client.get_parameter.return_value = {
                "Parameter": {"Value": "parameter-value"}
            }

            result = retrieve_parameter("parameter-name")

            ssm_client.get_parameter.assert_called_once_with(
                Name="parameter-name", WithDecryption=True
            )
            assert result == "parameter-value"
