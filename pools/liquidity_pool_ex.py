import os

import dotenv
from pytezos import pytezos
from pytezos.client import PyTezosClient

os.environ["KEY_FILENAME"] = '/home/aleksander/progs/hacks/defi2022/options/keys/key.json'
dotenv.load_dotenv()

SHELL = "https://rpc.tzkt.io/hangzhou2net/"
KEY_FILENAME = os.environ["KEY_FILENAME"]

CONTRACT_ADDRESS = "KT1VUB8KXc5TWxhSLrqa3AtyvPv2oCJ5xWjJ"


class ETF:
    def __init__(self, contract_address):
        self._contract_address = contract_address
        self._client: PyTezosClient = pytezos.using(key=KEY_FILENAME, shell=SHELL)
        self._contract = self._client.contract(self._contract_address)
        self._token = self._client.contract('KT1XGtPGDAvb3nsgTv2CdRgvx3vEuYQv2Xvp')

    def activate(self):
        try:
            print("activating accout...")
            op = self._client.activate_account().send()
            self._client.wait(op)
            print("activating accout complete")
        except:
            print('error in activating account')

    def reveal(self):
        try:
            print("revealing account ...")
            op = self._client.reveal().send()
            self._client.wait(op)
            print("revealing account complete")
        except:
            print('error in revealing account')

    def get_api(self):
        return self._contract.entrypoints

    def swap(self, num_tokens, num_tz):
        op = self._contract.tezToTokenPayment({
            'min_out': num_tokens,
            'receiver': 'tz1Wm6v8fom4St24eP3cZUnUD41RG8quhWmp',
        }).with_amount(num_tz)
        op.send()

    def get_balance(self):
        fa2_balance_of = {
            "requests": [{"owner": 'tz1Wm6v8fom4St24eP3cZUnUD41RG8quhWmp', "token_id": 0}],
            "callback": None,
        }
        balance = self._token.balance_of(**fa2_balance_of).callback_view()
        return balance


if __name__ == "__main__":
    api = ETF(CONTRACT_ADDRESS)
    # api.swap(1, 100)
    print(api.get_balance())
    # 2402, 353103
    # 2402, 353103
    # 2402, 348775

    # 0,012822
    # print(api.get_api())
    # api.activate()
    # api.reveal()
    # api.create_put_option(
    #     TOKEN_ADDRESS, 1, datetime(2022,5,1), 1,1
    # )
