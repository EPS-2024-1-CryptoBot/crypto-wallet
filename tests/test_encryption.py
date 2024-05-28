from unittest.mock import patch, MagicMock
import unittest
import pytest
from wallet.encryption import *
import constants as C
import os
import json
import wallet


class Test_Encryption(unittest.TestCase):
    def setUp(self):
        pub_k = MagicMock()
        pub_k.return_value = C.BACKEND_PUB_K
        patch.object(wallet.encryption, 'backend_pub_k', new_callable=pub_k).start()
        pvt_k = MagicMock()
        pvt_k.return_value = C.BACKEND_PVT_K
        patch.object(wallet.encryption, 'backend_pvt_k', new_callable=pvt_k).start()

    def tearDown(self):
        patch.stopall()

    def test_should_pass_when_root_is_retrieved(self):
        assert root() == {"RSA Key Generator": "CryptoBot_UnB_2024.1"} 

    def test_should_pass_when_decryption_is_correct(self):
        decrypt = Decryption(
            message='9cd37e86d26735e2b401579286459dec088543c5d85b5557a72e8bbeda82fa457b581754190febf468a09c4289728b6c919b0e6379d203d76c71b9503ea4eb26db1a235beb8c646ef9e7e222600b484377031c90bb5e6ee730ee5ea31d96b5ccd349042e02fa9a582a6737f116d453a7084648c0931b4631ef325eac64a7ad5cb7311c6bb22beb30692d8f9539c78e0a8bf415845f27f052a822193cd50429b7169c1e01fddf8712fd3d857242c543808e762bdef13099c680e5428a468ee7a1881abe10f9ba3076a44ad4e946691c98db42e47d0347593e119f5ab461b02d5e7ac91c137b1e0785461a6c9388e735c88b5322144b88868c7c61d5167e14bc92',
            private_key=C.PVT_K
        )
        assert decrypt_msg(decrypt)['decrypted_message'] == "testing my encryption"
    
    def test_should_pass_when_encryption_is_correct(self):
        msg = Encryption(
            message="testing my encryption",
            public_key=C.PUB_K
        )
        encryption = encrypt_msg(msg)
        answer = {'message': 'testing my encryption', 'encrypted_message': '9cd37e86d26735e2b401579286459dec088543c5d85b5557a72e8bbeda82fa457b581754190febf468a09c4289728b6c919b0e6379d203d76c71b9503ea4eb26db1a235beb8c646ef9e7e222600b484377031c90bb5e6ee730ee5ea31d96b5ccd349042e02fa9a582a6737f116d453a7084648c0931b4631ef325eac64a7ad5cb7311c6bb22beb30692d8f9539c78e0a8bf415845f27f052a822193cd50429b7169c1e01fddf8712fd3d857242c543808e762bdef13099c680e5428a468ee7a1881abe10f9ba3076a44ad4e946691c98db42e47d0347593e119f5ab461b02d5e7ac91c137b1e0785461a6c9388e735c88b5322144b88868c7c61d5167e14bc92'}
        assert encryption['message'] == answer['message']
        assert len(encryption['encrypted_message']) == len(answer['encrypted_message'])
        decrypt = Decryption(
            message=encryption['encrypted_message'],
            private_key=C.PVT_K
        )
        assert encryption['message'] == decrypt_msg(decrypt)['decrypted_message']

    def test_should_pass_when_encrypted_keys_are_generated(self):
        result = rsa_keygen(encrypt=True)
        assert len(result.get("public_key")) == 902
        assert type(result.get("private_encrypted_key")) == list
        c = Cryptography()
        private_key = c.retrieve_pvk(result.get("private_encrypted_key"))
        c.load_keys(result.get("public_key"), private_key)
        assert c.keys.get("public_key") == result.get("public_key")
        assert c.keys.get("private_key") == private_key

    def test_should_pass_when_keys_are_generated(self):
        result = rsa_keygen(encrypt=False)
        assert len(result.get("public_key")) == 902
        assert len(result.get("private_key")) >= 3000
        assert type(result.get("private_key")) == str
        c = Cryptography()
        c.load_keys(result.get("public_key"), result.get("private_key"))
        assert c.keys.get("public_key") == result.get("public_key")
        assert c.keys.get("private_key") == result.get("private_key")
