from config.settings import PAYSATCK_SECRETE_KEY
import requests

url = "https://api.paystack.co/transaction/initialize"
authorization = f"Bearer {PAYSATCK_SECRETE_KEY}"

def initiate_transaction(params):
    return requests.post(url,
                         headers={"Authorization": authorization},
                         json=params)
def verify_transaction(reference):
    return requests.get(f"https://api.paystack.co/transaction/verify/{reference}",
                        headers={"Authorization": authorization})