import bcrypt,random
from http import HTTPStatus
from App.utilities.queries import *
from App.services.database import MySQLDatabase
from App.services.neobiz import neobiz_payments


class backend:
    def do_user_registration(data):
      required_fields = ['username', 'email', 'phone_number', 'hashed_password', 'adhaar_number','pan_number', 'dob', 'gender', 'address', 'pincode']
      missing_fields = [field for field in required_fields if field not in data]

      if missing_fields:
        return {"Status" : "Error",  "Message": (f"Missing required fields: {', '.join(missing_fields)}")}, HTTPStatus.BAD_REQUEST

      values = (data['username'],data['email'],
      data['phone_number'],data['hashed_password'],
      data['adhaar_number'],data['pan_number'],data['dob'],
      data['gender'],data['address'], data['pincode']) 

      results = MySQLDatabase.execute_query(register_user_query, values)
      if results['status'] == HTTPStatus.OK:return {"Status" : "OK","message": "New User Updated"}, HTTPStatus.OK
      else: return {"Status" : "Error - Contact Admin",  "Message": "Issue at new user updating"}, HTTPStatus.BAD_REQUEST
    
    
    def get_user(data):
      results = MySQLDatabase.fetch_results(get_user_query, (data,))
      if results.get('data'):return results.get('data', [{}])[0], (results.get('status') if isinstance(results.get('status'), list) else [results.get('status', HTTPStatus.INTERNAL_SERVER_ERROR)])[0]
      else:return {"Status" : "Error",  "Message": "User Not Found"},  HTTPStatus.NOT_FOUND


    def authenticate_user(data):
      if (username := data.get('username')) and (password := data.get('password')):
          results = MySQLDatabase.fetch_results(authenticate_user_query, (username,))
          if results.get('data'):
              if bcrypt.checkpw(password.encode('utf-8'), results['data'][0]['password'].encode('utf-8')):
                  return {"successMsg": "User authenticated successfully"}, HTTPStatus.OK
              else:return {"errorMsg": "Invalid username or password"}, HTTPStatus.UNAUTHORIZED
      else:return {"message": "Username or password not provided"}, HTTPStatus.NOT_FOUND

    def get_wallet(data):
        results = MySQLDatabase.fetch_results(get_payout_wallet_by_username, (data,))
        if results.get('data'):return results.get('data', [{}])[0], (results.get('status') if isinstance(results.get('status'), list) else [results.get('status', HTTPStatus.INTERNAL_SERVER_ERROR)])[0]
        else:return {"errorMsg" : "Data Not Found"} , HTTPStatus.NOT_FOUND

    def check_authorization(data):
       results = MySQLDatabase.fetch_results(get_kyc_status_query, (data.get('username'),))
       if results.get("data"):
          if results['data'][0]['transaction_right'] == 1:
             if int(results['data'][0]['t_pin']) == int(data.get('t_pin')):return 1, data.pop('t_pin')
             else:return 3, data
          else:print("TRANSACTION RIGHTS are on Hold!. Contact Admin");return 2, data
       else:return 0, data

    def get_token():
      results = MySQLDatabase.fetch_results(get_neobiz_token_query,("Neobiz",))
      print("results", results)
      if results.get('data'):return results.get('data', [{}])[0], (results.get('status') if isinstance(results.get('status'), list) else [results.get('status', HTTPStatus.INTERNAL_SERVER_ERROR)])[0]
      else:return {"message" : "Data Not Found"} , HTTPStatus.NOT_FOUND

    def insert_transaction_request(data):
      required_fields = ['username', 'beneficiary_name', 'phone', 'bank_account', 'ifsc', 'amount', 'transfer_id', 'wallet_balance']
      data_tuple = tuple(data[field] for field in required_fields if data.get(field) is not None) if all(data.get(field) is not None for field in required_fields) else False
      if data_tuple:
        results = MySQLDatabase.execute_query(transaction_request_insert_query,data_tuple)
        if results['status'] == HTTPStatus.OK:return {"message" : "Transaction request inserted"},  True
      else: {"message" : "Missing Feilds, Transaction Aborted"} , False

    def do_transaction(data):
      value, updatedata = backend.check_authorization(data)
      if value == 0:return {"message": "USER NOT FOUND"}, HTTPStatus.OK
      elif value == 1:msg, status = backend.insert_transaction_request(data)
      elif value == 2:return {"message": "TRANSACTION RIGHTS are on Hold!. Contact Admin"}, HTTPStatus.OK
      elif value == 3:return {"message": "Wrong Transaction Pin"}, HTTPStatus.OK
      if not status:return {"errorMsg": "Failed to insert transaction request"}, HTTPStatus.OK

      t_response, t_code = neobiz_payments(data, backend.get_token())
      if status != 200:return {"errorMsg": "ISSUE with Bank ", "data": t_response}, t_code
