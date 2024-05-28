from unittest.mock import patch, MagicMock
import unittest
import pytest
import wallet.blockchain
from wallet.main import *
from wallet.blockchain import Blockchain, mongo_paths
import constants as C
import os
import json
import wallet


class Test_Main(unittest.TestCase):
    def setUp(self):
        pub_k = MagicMock()
        pub_k.return_value = C.BACKEND_PUB_K
        patch.object(wallet.encryption, 'backend_pub_k', new_callable=pub_k).start()
        pvt_k = MagicMock()
        pvt_k.return_value = C.BACKEND_PVT_K
        patch.object(wallet.encryption, 'backend_pvt_k', new_callable=pvt_k).start()

        def psql_execution_mock(*args, **kwargs):
            args_list = list(args)
            return [[(C.PUB_K), (C.PVT_K)]]
        
        psql_mock = patch("wallet.blockchain.PostgresConnector").start()
        # psql_mock.return_value.execute_query.return_value = [
        #     [(C.PUB_K), (C.PVT_K)]
        # ]
        psql_mock.return_value.execute_query.side_effect = psql_execution_mock

        # backend_pvt_k_mock = patch("wallet.blockchain.Cryptography").start()
        # backend_pvt_k_mock.return_value.retrieve_pvk.return_value = C.BACKEND_PVT_K

        backend_pvt_k_mock = patch("wallet.blockchain.Cryptography.retrieve_pvk").start()
        backend_pvt_k_mock.return_value = C.BACKEND_PVT_K

        wallet.main.blockchain = Blockchain(
            mongo_conn=MagicMock(),
            user="EmDpl3ADFfNcuyg2KukjrC8e5Yh1",
        )

        mongo_conn_mock = MagicMock()
        patch.object(wallet.main.blockchain, 'mongo_conn', new_callable=mongo_conn_mock).start()

        with open("tests/blockchain.json", "r") as f:
            self.full_blockchain = json.load(f)
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
                    return self.full_blockchain
                elif mongo_paths["blockchain"] == path and filter != {}:
                    return [x for x in self.full_blockchain if x["user"] == filter["user"]]
                elif mongo_paths["transactions"] == path:
                    return self.transactions
            mongo_conn_mock.return_value.retrieve_data.side_effect = path_mock

    def tearDown(self):
        patch.stopall()

    def test_should_pass_when_blockchain_is_not_valid(self):
        mongo_conn_mock = MagicMock()
        patch.object(wallet.main.blockchain, 'mongo_conn', new_callable=mongo_conn_mock).start()
        mongo_conn_mock.return_value.retrieve_data.return_value = [x for x in self.full_blockchain if x["user"] == "EmDpl3ADFfNcuyg2KukjrC8e5Yh1"]
        response = validate_chain()
        response_data = response.body.decode()
        response_data = json.loads(response_data)
        assert response.status_code == 200
        assert response_data['message'] == 'The blockchain is not valid.'

    def test_should_pass_when_blockchain_is_valid(self):
        mongo_conn_mock = MagicMock()
        patch.object(wallet.main.blockchain, 'mongo_conn', new_callable=mongo_conn_mock).start()
        mongo_conn_mock.return_value.retrieve_data.return_value = [x for x in self.full_blockchain if x["user"] == "brasil"]
        response = validate_chain()
        response_data = response.body.decode()
        response_data = json.loads(response_data)
        assert response.status_code == 200
        assert response_data['message'] == 'The blockchain is valid.'

    def test_should_pass_when_transactions_are_retrieved_correctly(self):
        response = get_transactions()
        assert response == [{'sender': 'miner', 'receiver': 'EmDpl3ADFfNcuyg2KukjrC8e5Yh1', 'amount': 10}]
        assert len(response) == 1

    def test_should_pass_when_balance_is_retrieved_correctly(self):
        response = get_balance()
        response_data = response.body.decode()
        response_data = json.loads(response_data)
        assert response.status_code == 200
        assert response_data == {'balance': 10}

    def test_should_pass_when_block_is_mined(self):
        response = mine_block()
        answer = {'message': 'Congrats! You have minered a block!', 'block': {'index': 3, 'timestamp': '2024-05-28 20:23:48.349648', 'proof': 7935, 'previous_hash': '45cdb05fdab81632c95500f1a356ac920c4852fbe74f6a00b5e88af9f517a75e', 'transactions': [{'transaction': {'sender': 'miner', 'receiver': 'W64QDRYN7ROSFVbMgYl7BTLJICn2', 'amount': 10}, 'transaction_data': {'signature': '9dafdfb60a53a17a45b0e15c682dd0af09ec424c9a4d80ab94bdef39b27bd7afdd2b3a41ae0c95cbf7524db789dd16fe4f524cdc0ff74ef16661ab496e8ab553c9367c9487a0c63054e59d88610e876885b67a906d409330fb73eb151f4847062249ea4debf0b18c306db3340a82dd5f93239e3f7780d5ae762e263f035462a58cc03531ddfb204adaa011709067d21744fee620806beca34a98c898804cbb7c776da49375aa13bf0514aee014756a1e2f80c5cf2809044e04e4978a62cd273d134d5bc5a06ed417e43d8cb7fde7c37eb67d397bcf75e6d5c5a19436a900d9a2cca4ab051d10ec9b326ebd07f57097de79f63c2f07ef98e19f69c1fe16eec56f', 'public_key': '2d2d2d2d2d424547494e205055424c4943204b45592d2d2d2d2d0a4d494942496a414e42676b71686b6947397730424151454641414f43415138414d49494243674b4341514541714a514973533048755469597362654b586a2b370a4c6f50766931574c4c74376e4c67666c4c643148354a6e5276474e755841704443744c584e503338643853536e4c51635930445a314135464a317972787853500a4d6f6d506e4c6a672f4c676e6332734569384d38304277596533385a47576a4d346834374152354437725361412f64414b6c39775375546d6565513458556d780a2f4c544f6a7166664f3458766c474e4e50724e49444e4e354c7164372f466b79697174737a78347079695373766d79456e344270683153366c514972755079720a4557386e636c70656751756670497a4931704654506879686c4559504d656a2f735555782f3541617475434c76686b5077475761474d43572f6a7850424167410a7730576c4743776931316b564969683269377645524b7152637642647035726e415073356c566d433738325666634f6a4f70434e4e6c4c495a4f6d5861664f660a39774944415141420a2d2d2d2d2d454e44205055424c4943204b45592d2d2d2d2d0a'}}]}}
        assert response['message'] == answer['message']
        assert response['block']['index'] == answer['block']['index']
        assert response['block']['proof'] == answer['block']['proof']
        assert response['block']['previous_hash'] == answer['block']['previous_hash']
        assert len(response['block']['transactions']) == len(answer['block']['transactions'])

    def test_should_pass_when_receiver_does_not_exist(self):
        wallet.main.blockchain.retrieve_transactions()
        wallet.main.blockchain.retrieve_blockchain()

        transaction_pool = [wallet.main.blockchain.transactions]
        assert transaction_pool == [self.transactions]

        mongo_conn_mock = MagicMock()
        mongo_conn_mock.return_value.insert_data.side_effect = lambda *transaction: transaction_pool.append(list(transaction)[2])

        def path_mock(*args, **kwargs):
                arg_list = list(args)
                path = arg_list[:2]
                if len(arg_list) > 2:
                    filter = arg_list[2]
                if mongo_paths["blockchain"] == path and filter == {}:
                    return self.full_blockchain
                elif mongo_paths["blockchain"] == path and filter != {}:
                    return [x for x in self.full_blockchain if x["user"] == filter["user"]]
                elif mongo_paths["transactions"] == path:
                    return transaction_pool
                
        mongo_conn_mock.return_value.retrieve_data.side_effect = path_mock
        patch.object(wallet.main.blockchain, 'mongo_conn', new_callable=mongo_conn_mock).start()

        transaction_instance = Transaction(
            amount=5,
            receiver="non_existing_user"
        )

        response = add_transaction(transaction_instance)
        response_data = response.body.decode()
        response_data = json.loads(response_data)
        
        assert response.status_code == 400
        assert response_data == {'message': 'Receiver not found in the blockchain.', 'blockchain_users': ['brasil', 'EmDpl3ADFfNcuyg2KukjrC8e5Yh1', None, 'fKhB1D6BBNMQpoGw7ogSwp4U8Z62', 'W64QDRYN7ROSFVbMgYl7BTLJICn2', '66mia9DFH0dRwqngfGCFgkjk2hq1', 'rQG7VAYoSYSZPzCykJXwFCFxSx92', 'NEv5Ilxgz0dR9m9RFTwZHs5EQaE2', 'p1McWPhB5RcfPV7BG1PrHBRY9si2', 'p1McWPhB5RcfPV7BG1PrHBRY9si2', 'p1McWPhB5RcfPV7BG1PrHBRY9si2']}

    def test_should_pass_when_transaction_is_added(self):
        wallet.main.blockchain.retrieve_transactions()
        wallet.main.blockchain.retrieve_blockchain()

        transaction_pool = [wallet.main.blockchain.transactions]
        assert transaction_pool == [self.transactions]

        mongo_conn_mock = MagicMock()
        mongo_conn_mock.return_value.insert_data.side_effect = lambda *transaction: transaction_pool.append(list(transaction)[2])

        def path_mock(*args, **kwargs):
                arg_list = list(args)
                path = arg_list[:2]
                if len(arg_list) > 2:
                    filter = arg_list[2]
                if mongo_paths["blockchain"] == path and filter == {}:
                    return self.full_blockchain
                elif mongo_paths["blockchain"] == path and filter != {}:
                    return [x for x in self.full_blockchain if x["user"] == filter["user"]]
                elif mongo_paths["transactions"] == path:
                    return transaction_pool
                
        mongo_conn_mock.return_value.retrieve_data.side_effect = path_mock
        patch.object(wallet.main.blockchain, 'mongo_conn', new_callable=mongo_conn_mock).start()

        transaction_instance = Transaction(
            amount=5,
            receiver="W64QDRYN7ROSFVbMgYl7BTLJICn2"
        )

        response = add_transaction(transaction_instance)
        response_data = response.body.decode()
        response_data = json.loads(response_data)
        
        assert response.status_code == 200
        assert response_data == {'message': 'This transaction will be included in the CBU blockchain in the block 3 when it is minerated by someone.', 'transaction': {'receiver': 'W64QDRYN7ROSFVbMgYl7BTLJICn2', 'amount': 5.0}}

    def test_should_pass_when_transaction_is_not_added_due_to_insufficient_balance(self):
        wallet.main.blockchain.retrieve_transactions()
        wallet.main.blockchain.retrieve_blockchain()

        transaction_pool = [wallet.main.blockchain.transactions]
        assert transaction_pool == [self.transactions]

        mongo_conn_mock = MagicMock()
        mongo_conn_mock.return_value.insert_data.side_effect = lambda *transaction: transaction_pool.append(list(transaction)[2])

        def path_mock(*args, **kwargs):
                arg_list = list(args)
                path = arg_list[:2]
                if len(arg_list) > 2:
                    filter = arg_list[2]
                if mongo_paths["blockchain"] == path and filter == {}:
                    return self.full_blockchain
                elif mongo_paths["blockchain"] == path and filter != {}:
                    return [x for x in self.full_blockchain if x["user"] == filter["user"]]
                elif mongo_paths["transactions"] == path:
                    return transaction_pool
                
        mongo_conn_mock.return_value.retrieve_data.side_effect = path_mock
        patch.object(wallet.main.blockchain, 'mongo_conn', new_callable=mongo_conn_mock).start()

        transaction_instance = Transaction(
            amount=250,
            receiver="W64QDRYN7ROSFVbMgYl7BTLJICn2"
        )

        response = add_transaction(transaction_instance)
        response_data = response.body.decode()
        response_data = json.loads(response_data)
        
        assert response.status_code == 400
        assert response_data["message"] == "Insufficient balance."
        assert response_data == {'message': 'Insufficient balance.', 'user': 'EmDpl3ADFfNcuyg2KukjrC8e5Yh1', 'balance:': 10}

    def test_should_pass_when_chain_is_retrieved_correctly(self):
        before = wallet.main.blockchain.chain
        response = get_chain()
        assert before != wallet.main.blockchain.chain

        response_data = response.body.decode()
        response_data = json.loads(response_data)
        assert response_data["chain"] == wallet.main.blockchain.chain
        assert response.status_code == 200

    def test_should_pass_when_user_is_properly_changed(self):
        assert wallet.main.blockchain.user == "EmDpl3ADFfNcuyg2KukjrC8e5Yh1"
        set_user('new_user_id')
        assert wallet.main.blockchain.user == "new_user_id"

    def test_should_pass_when_root_is_retrieved(self):
        assert read_root() == {"WalletAPI": "CryptoBot_UnB_2024.1"} 