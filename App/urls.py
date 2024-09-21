import logging, secrets
from http import HTTPStatus
from datetime import timedelta
from App.services.backend import backend
from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required


# Configure logging
logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s: %(message)s',handlers=[logging.FileHandler("app.log"),logging.StreamHandler()])

class SotruPay:
    def __init__(self):
        self.app = Flask(__name__)
        self.jwt = JWTManager(self.app)
        self.app.config['JWT_SECRET_KEY'] = secrets.token_urlsafe(32)
        self.app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=10)
        self.setup_routes()

    def setup_routes(self):
        @self.app.route('/', methods=['GET'])
        def home():
            logging.info('SotruPay Flask App Start')
            return "Hola! From SotruPay Back End -- Version 1.0", HTTPStatus.OK
        
        @self.app.route('/registerUser', methods=['POST'])
        def registerUser():
            logging.debug("Register API called with json: %s", request.get_json())
            response, status_code = backend.do_user_registration(request.get_json())
            return jsonify(response), status_code

        @self.app.route('/getUser', methods=['POST'])
        def get_user():
            if not request.get_json() or not request.get_json().get('phone_number'):
                return jsonify({"errorMsg": "Please Provide Valid Data"}), HTTPStatus.BAD_REQUEST
            responseStr, code = backend.get_user(request.get_json().get('phone_number'))
            if code == HTTPStatus.OK and responseStr.get('username'):return jsonify(responseStr), code
            else:
                logging.error("GetUser API Error with json: %s", responseStr)
                return jsonify(responseStr), code
 
        @self.app.route('/LoginUser', methods=['POST'])
        def login():
            if not request.get_json():return jsonify({"errorMsg": "Please Provide Valid Data"}), HTTPStatus.BAD_REQUEST
            responseMsg, code = backend.authenticate_user(request.get_json())
            if code == HTTPStatus.OK:
                logging.info(f"Login API Served and User authenticated for user ::{request.get_json().get('username')}:: ")
                access_token = create_access_token(identity={'username': request.get_json().get('username')})
                return jsonify({"successMsg": "User Authenticated Successfully", "access_token": access_token}), HTTPStatus.OK
            else:
                logging.error("Login API Error with json: %s", responseMsg)
                return jsonify(responseMsg), code

        @self.app.route('/getWalletBallance', methods=['POST'])
        @jwt_required()
        def get_wallet():
            if not request.get_json() or not request.get_json().get('username'):return jsonify({"errorMsg": "Please Provide Valid Data"}), HTTPStatus.BAD_REQUEST
            msg, code = backend.get_wallet(request.get_json().get('username'))
            if code :return jsonify(msg), code
        
        @self.app.route('/doTransaction', methods=['POST'])  
        # @jwt_required()  
        def do_transaction():
            if not request.get_json():return jsonify({"errorMsg": "Please Provide Valid Data"}), HTTPStatus.BAD_REQUEST
            logging.info("Do_transaction API called with json: %s", request.get_json())
            responseMsg, code = backend.do_transaction(request.get_json())
            if code == HTTPStatus.OK:
                logging.info("Do_transaction API satisfied")
                return jsonify(responseMsg), code
            else:
                logging.error("Error from do_transaction API: %s", responseMsg)
                return jsonify(responseMsg), code

        @self.app.route('/getLastFiveTransactions', methods=['POST'])
        @jwt_required()
        def get_last_five_transactions():
            data = request.get_json()
            if not data:
                logging.error("Request body is Null: %s", data)
                return jsonify({"errorMsg": "Please Provide request body(userName)"}), HTTPStatus.BAD_REQUEST

            logging.debug("get_last_five_transactions API called with json: %s", data)
            responseMsg, code = backend.getLastFiveTransactions(data)
            return jsonify(responseMsg), code

        @self.app.route('/getTransactionsByDates', methods=['POST'])
        @jwt_required()
        def get_transactions_by_dates():
            data = request.get_json()
            if not data:
                logging.error("Request body is Null: %s", data)
                return jsonify({"errorMsg": "Please Provide request body(userName,fromDt,toDt)"}), HTTPStatus.BAD_REQUEST

            logging.debug("get_transactions_by_dates API called with json: %s", data)
            responseMsg, code = backend.get_transactions_for_date(data)
            return jsonify(responseMsg), code


        @self.app.route('/callback', methods=['GET', 'POST'])
        def callback():
            if request.method == 'POST':
                data = request.get_json()
                print("Data callback:", data)
                return jsonify({"status": "success", "message": "Callback received successfully"}), HTTPStatus.OK
            elif request.method == 'GET':
                print("GET request received at /callback")
                return jsonify({"status": "success", "message": "GET request received"}), HTTPStatus.OK


        @self.app.route('/getUserWalletHistory', methods=['POST'])
        @jwt_required()
        def get_wallet_history_for_user():
            data = request.get_json()
            if not data:
                logging.error("Request body is Null: %s", data)
                return jsonify({"errorMsg": "Please Provide request body(userName)"}), HTTPStatus.BAD_REQUEST

            logging.debug("get_wallet_history_for_user API called with json: %s", data)
            responseMsg, code = backend.getWalletHistoryForUser(data)
            if code == HTTPStatus.OK:
                return jsonify(responseMsg), code
            else:
                logging.error("Failed to fetch wallet history for user: %s", responseMsg)
                return jsonify({"errorMsg": "Failed to fetch wallet history for user"}), code

        @self.app.route('/admin/login', methods=['POST'])
        def admin_login():
            data = request.get_json()
            if not data:
                logging.error("Request body is Null: %s", data)
                return jsonify({"errorMsg": "Please Provide request body(mobileNumber,password)"}), HTTPStatus.BAD_REQUEST

            logging.debug("Admin login API called with json: %s", data)
            msg, code = backend.admin_login(data)  
            if code == HTTPStatus.OK:
                logging.info("Admin LogIn API Served and User authenticated")
                access_token = create_access_token(identity={'username': msg['username']})
                return jsonify({"access_token": access_token, "userName": msg.get('username')}), HTTPStatus.OK
            else:
                logging.error("Admin login API Error with json: %s", msg)
                return jsonify(msg), code

        @self.app.route('/admin/getUsers', methods=['GET'])
        @jwt_required()
        def get_users_for_admin():
            responseMsg, code = backend.getUserForAdmin()
            if code == HTTPStatus.OK:
                return jsonify(responseMsg), code
            else:
                logging.error("Failed to fetch Users: %s", responseMsg)
                return jsonify({"errorMsg": "Failed to fetch Users"}), code

        @self.app.route('/admin/getWalletHistory', methods=['GET'])
        @jwt_required()
        def get_wallet_history_for_admin():
            data, code = backend.getWalletHistory()
            if code == HTTPStatus.OK:
                return jsonify(data), code
            else:
                logging.error("Failed to fetch wallet history for admin: %s", data)
                return jsonify({"errorMsg": "Failed to fetch wallet history for admin"}), code

        @self.app.route('/admin/getWalletHistoryForUser', methods=['POST'])
        @jwt_required()
        def get_wallet_history_for_user_by_admin():
            data = request.get_json()
            if not data:
                logging.error("Request body is Null: %s", data)
                return jsonify({"errorMsg": "Please Provide request body(userName)"}), HTTPStatus.BAD_REQUEST

            logging.debug("get_wallet_history_for_user_by_admin API called with json: %s", data)
            responseMsg, code = backend.getWalletHistoryForUser(data)
            if code == HTTPStatus.OK:
                return jsonify(responseMsg), code
            else:
                logging.error("Failed to fetch wallet history for user: %s", responseMsg)
                return jsonify({"errorMsg": "Failed to fetch wallet history for user"}), code

        @self.app.route('/admin/updateKyc', methods=['POST'])
        @jwt_required()
        def manage_user():
            data = request.get_json()
            if not data:
                logging.error("Request body is Null: %s", data)
                return jsonify({"errorMsg": "Please Provide request body"}), HTTPStatus.BAD_REQUEST

            logging.debug("manage_user API called with json: %s", data)
            responseMsg, code = backend.updateUserKycStatus(data)
            if code == HTTPStatus.OK:
                return jsonify(responseMsg), code
            else:
                logging.error("Failed to update user KYC: %s", responseMsg)
                return jsonify({"errorMsg": "Failed to update user KYC"}), code

        @self.app.route('/admin/UpdateWallet', methods=['POST'])
        @jwt_required()
        def UpdateWallet():
            data = request.get_json()
            if data:
                print("data: ", data)
                responseMsg, code= backend.UpdateWallet(data)
                if code == HTTPStatus.OK:
                    return jsonify(responseMsg), code
                else:return jsonify({"errorMsg": "Failed to do action on the user wallet"}), code