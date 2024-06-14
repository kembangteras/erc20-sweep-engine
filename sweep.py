import json
import time
from web3 import Web3

RPC_URL = "https://mainnet.infura.io/v3/YOUR_INFURA_KEY"
PRIVATE_KEYS = ["0xPRIVATEKEY1", "0xPRIVATEKEY2"]
VAULT_ADDRESS = "0xYourVaultAddress"
TOKEN_ADDRESS = "0xTokenContractAddress"
GAS_LIMIT = 80000

w3 = Web3(Web3.HTTPProvider(RPC_URL))

ERC20_ABI = json.loads('[{"constant":true,"inputs":[{"name":"_owner","type":"address"}],"name":"balanceOf","outputs":[{"name":"","type":"uint256"}],"type":"function"},{"constant":false,"inputs":[{"name":"_to","type":"address"},{"name":"_value","type":"uint256"}],"name":"transfer","outputs":[],"type":"function"}]')

token = w3.eth.contract(address=TOKEN_ADDRESS, abi=ERC20_ABI)

def sweep_token(pk):
    acct = w3.eth.account.from_key(pk)
    balance = token.functions.balanceOf(acct.address).call()
    if balance > 0:
        nonce = w3.eth.get_transaction_count(acct.address)
        tx = token.functions.transfer(VAULT_ADDRESS, balance).build_transaction({
            'from': acct.address,
            'gas': GAS_LIMIT,
            'gasPrice': w3.eth.gas_price,
            'nonce': nonce,
        })
        signed = w3.eth.account.sign_transaction(tx, private_key=pk)
        tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
        print(f"[✓] Swept {balance} tokens from {acct.address} → {VAULT_ADDRESS}, tx = {tx_hash.hex()}")
        return tx_hash.hex()
    else:
        print(f"[–] No balance on {acct.address}")
        return None

if __name__ == "__main__":
    for key in PRIVATE_KEYS:
        try:
            sweep_token(key)
            time.sleep(1)
        except Exception as e:
            print(f"[!] Error: {e}")
