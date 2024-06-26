from unittest.mock import patch, MagicMock
import unittest
import pytest
from wallet.blockchain import Blockchain, mongo_paths
from wallet.encryption import *
import constants as C
import os
import json


class Test_Blockchain(unittest.TestCase):
    def setUp(self):
        psql_mock = patch("wallet.blockchain.PostgresConnector").start()
        psql_mock.return_value.execute_query.return_value = [
            [(C.PUB_K), (C.PVT_K)]
        ]

        # backend_pvt_k_mock = patch("wallet.blockchain.Cryptography").start()
        # backend_pvt_k_mock.return_value.retrieve_pvk.return_value = C.BACKEND_PVT_K

        backend_pvt_k_mock = patch("wallet.blockchain.Cryptography.retrieve_pvk").start()
        backend_pvt_k_mock.return_value = C.BACKEND_PVT_K

        self.blockchain = Blockchain(
            mongo_conn=MagicMock(),
            user="EmDpl3ADFfNcuyg2KukjrC8e5Yh1",
        )

        mongo_conn_mock = MagicMock()
        patch.object(self.blockchain, 'mongo_conn', new_callable=mongo_conn_mock).start()

        with open("tests/blockchain.json", "r") as f:
            full_blockchain = json.load(f)
            self.transactions = [
                {
                        "transaction": {
                            "sender": "miner",
                            "receiver": "W64QDRYN7ROSFVbMgYl7BTLJICn2",
                            "amount": 10
                        },
                        "transaction_data": {
                            "signature": "9dafdfb60a53a17a45b0e15c682dd0af09ec424c9a4d80ab94bdef39b27bd7afdd2b3a41ae0c95cbf7524db789dd16fe4f524cdc0ff74ef16661ab496e8ab553c9367c9487a0c63054e59d88610e876885b67a906d409330fb73eb151f4847062249ea4debf0b18c306db3340a82dd5f93239e3f7780d5ae762e263f035462a58cc03531ddfb204adaa011709067d21744fee620806beca34a98c898804cbb7c776da49375aa13bf0514aee014756a1e2f80c5cf2809044e04e4978a62cd273d134d5bc5a06ed417e43d8cb7fde7c37eb67d397bcf75e6d5c5a19436a900d9a2cca4ab051d10ec9b326ebd07f57097de79f63c2f07ef98e19f69c1fe16eec56f",
                            "public_key": "2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d494942496a414e42676b71686b6947397730424151454641414f43415138414d49494243674b4341514541714a514973533048755469597362654b586a2b370a4c6f50766931574c4c74376e4c67666c4c643148354a6e5276474e755841704443744c584e503338643853536e4c51635930445a314135464a317972787853500a4d6f6d506e4c6a672f4c676e6332734569384d38304277596533385a47576a4d346834374152354437725361412f64414b6c39775375546d6565513458556d780a2f4c544f6a7166664f3458766c474e4e50724e49444e4e354c7164372f466b79697174737a78347079695373766d79456e344270683153366c514972755079720a4557386e636c70656751756670497a4931704654506879686c4559504d656a2f735555782f3541617475434c76686b5077475761474d43572f6a7850424167410a7730576c4743776931316b564969683269377645524b7152637642647035726e415073356c566d433738325666634f6a4f70434e4e6c4c495a4f6d5861664f660a39774944415141420a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d0a"
                        }
                    },
            ]

            def path_mock(*args, **kwargs):
                arg_list = list(args)
                path = arg_list[:2]
                if len(arg_list) > 2:
                    filter = arg_list[2]
                if mongo_paths["blockchain"] == path and filter == {}:
                    return full_blockchain
                elif mongo_paths["blockchain"] == path and filter != {}:
                    return [x for x in full_blockchain if x["user"] == filter["user"]]
                elif mongo_paths["transactions"] == path:
                    return self.transactions
            mongo_conn_mock.return_value.retrieve_data.side_effect = path_mock

    def tearDown(self):
        patch.stopall()

    def test_should_pass_when_chain_is_synced(self):
        self.blockchain.retrieve_users_in_chain()
        self.blockchain.retrieve_blockchain()
        self.blockchain.sync_chain()
        assert self.blockchain.chain == C.SYNCED_CHAIN

    def test_should_pass_when_transaction_is_correctly_added(self):
        self.blockchain.retrieve_transactions()
        self.blockchain.retrieve_blockchain()

        transaction_pool = [self.blockchain.transactions]
        assert transaction_pool == [self.transactions]

        mongo_conn_mock = MagicMock()
        mongo_conn_mock.return_value.insert_data.side_effect = lambda *transaction: transaction_pool.append(list(transaction)[2])
        mongo_conn_mock.return_value.retrieve_data.return_value = transaction_pool

        patch.object(self.blockchain, 'mongo_conn', new_callable=mongo_conn_mock).start()

        index = self.blockchain.add_transaction(
            amount=250,
            receiver="W64QDRYN7ROSFVbMgYl7BTLJICn2"
        )

        self.blockchain.retrieve_transactions()
        result = {'transaction': {'sender': 'EmDpl3ADFfNcuyg2KukjrC8e5Yh1', 'receiver': 'W64QDRYN7ROSFVbMgYl7BTLJICn2', 'amount': 250}, 'transaction_data': {'signature': '30dc2d36539e2051590df7b3421a83f4e800a351046263af8c64e818697a4e56c85fd464374f2632d361e990cc441f64d49baf1cbbf9599a6ad94315272b39ea8e7378b9d8d8efaab15200995bd560a4c513dfec699e44fd1546e908ce47bdbd7ae540cec8f9b9934a3d4a84595b698b21edc2694ce4705a250c460157abbf6b400d0b1c5c97b8eb38eb523764fb6e3d8964d571e6dbbe230889ea389948d2f4f12c07d9e7e505b02df573983b2c139c4817e28dec2b31a58f36ff2797bc5f0c56c8d22b1f1cec5580c1090f6068350b99fc302be8833a8f11f84f90ca363405cfac6cbfc76be89912e369860919aaf53721feeadafb06dae349cf272c13d254', 'public_key': '2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d494942496a414e42676b71686b6947397730424151454641414f43415138414d49494243674b43415145417868454f6e6f757a75356b7548706e744a44754c0a6b5830783556674d76417976454e55724c304666717551744335326b6f4d45364b4e49446f64596b5175435064334e7873764d4d665a4d6f4768744f4d5961350a3379335947746d716e41555a744e39433663353036414252702b7135465a4833544a506a3675564276356e7178613571714c70504a7a335564715430467371740a6e5659524267696e346b344a66373467536b67575132417770554964452f376d425445386c3147667772386e3743356e706649496537303231783839354b35650a75715a46686767562b5a4a307a3177775676755a6c59746a696f6b765651744d59696d6d497873583054314e76494373524c596d4a4650314854754d5734764a0a4a512b6245494948352f7777515231496d6465644f6277436c4951536666585563436e7166484c66496e334c563076354c685a66324359593379736a664d555a0a72774944415141420a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d0a'}}
        assert transaction_pool == [self.transactions, result]
        assert index == 3

    def test_should_pass_when_previous_block_is_correct(self):
        assert self.blockchain.get_previous_block() == self.blockchain.chain[-1]
        self.blockchain.retrieve_blockchain()
        assert self.blockchain.get_previous_block() == self.blockchain.chain[-1]

    def test_should_pass_when_blockchain_metrics_are_valid(self):
        self.blockchain.retrieve_blockchain()
        result = {"length": 2, "blocks": self.blockchain.chain}
        assert self.blockchain.get_chain_metrics(self.blockchain.chain) == result
    
    def test_should_pass_when_proof_of_work_is_valid(self):
        assert self.blockchain.proof_of_work(1) == 20
        assert self.blockchain.proof_of_work(25043213) == 108517
        assert self.blockchain.proof_of_work(-250) == 25041
        assert self.blockchain.proof_of_work(0) == 115558
        assert self.blockchain.proof_of_work(1.25) == 41148

    def test_should_pass_when_blockchain_is_valid(self):
        assert self.blockchain.is_chain_valid() == True

    def test_should_pass_when_blockchain_is_not_valid(self):
        self.blockchain.retrieve_blockchain()
        self.blockchain.create_block(1,20)
        assert self.blockchain.is_chain_valid() == False

    def test_should_pass_when_balance_is_right(self):
        assert self.blockchain.get_balance("W64QDRYN7ROSFVbMgYl7BTLJICn2") == 140
        assert self.blockchain.get_balance("brasil") == 0

    def test_should_pass_when_hash_is_valid(self):
        hash_result = "9ac4e1381b3633c3fadfa38830f9762000de11b5c748700f98363c14b40f3daa"
        assert (self.blockchain.hash("OI ")) != hash_result
        assert (self.blockchain.hash("OI")) == hash_result
