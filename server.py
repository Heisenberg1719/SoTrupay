from waitress import serve
from App.urls import SotruPay

if __name__ == "__main__":
    app_instance = SotruPay()

    app_instance.app.run(host='0.0.0.0', port=8080, debug=True)
    # serve(app_instance.app, host='0.0.0.0', port=8080)
