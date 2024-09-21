import requests
import json
from http import HTTPStatus
import random

def neobiz_payments(payload, token):
    credentials = token[0]
    url = "https://api.neobizpayments.com/client/ms-payment-imps"
    
    headers = {
        'Content-Type': 'application/json',
        'Client-Id': credentials.get('client_id'),
        'Client-SecretId': credentials.get('client_secret_key')}


    req_payload = {
        "name": payload['beneficiary_name'],
        "email": "janki@gmail.com",
        "phone": payload['phone'],
        "bankAccount": payload['bank_account'],
        "ifsc": payload['ifsc'],
        "address": "Bangalore",
        "amount": payload['amount'],
        "remarks": "NEO-BIZ",
        "transferId": payload['transfer_id'],
        "clientId": "NBC0010"
    }

    payload_json = json.dumps(req_payload, indent=4)
    try:
        response = requests.post(url, headers=headers, data=payload_json)
        response.raise_for_status()
        print(f"Status Code: {response.status_code}")
        print(f"Response Text: {response.text}")
        if response.status_code == 200:
            data = json.loads(response.text)
            status = data.get("status")
            if status == "Transaction Pending":
                print("Transaction success")
                   
        return response.text, response.status_code

    except Exception as e:
        # Log any other exceptions
        print(f"An unexpected error occurred: {e}")
        return f"An unexpected error occurred: {e}", HTTPStatus.INTERNAL_SERVER_ERROR
