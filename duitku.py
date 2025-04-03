from flask import Flask, jsonify, request, redirect, render_template
import requests
import hashlib
import datetime
from flask_cors import CORS, cross_origin

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

YOUR_URL = "localhost:5000"

DUITKU_GETPAYMENTMETHOD_URL = "https://sandbox.duitku.com/webapi/api/merchant/paymentmethod/getpaymentmethod"
DUITKU_REQUESTTRANSACTION_URL = "https://sandbox.duitku.com/webapi/api/merchant/v2/inquiry"
DUITKU_TRANSACTIONSTATUS_URL = "https://sandbox.duitku.com/webapi/api/merchant/transactionStatus"

MERCHANT_CODE = "YOUR_MERCHANT_CODE"
API_KEY = "YOUR_API_KEY"
AMOUNT = "10000"

def request_transaction():
    merchantCode = MERCHANT_CODE
    apiKey = API_KEY
    amount = AMOUNT
    now = datetime.datetime.now()
    merchantOrderId = str(int(now.timestamp()))  #Your Merchant Order ID
    raw_signature = merchantCode + merchantOrderId + amount + apiKey
    signature = hashlib.md5(raw_signature.encode()).hexdigest()

    paymentMethod = "I1" #Payment Method for VA BNI, change it by the payment method returned by getpaymentmethod

    payload = {
        "merchantCode": merchantCode,
        "paymentAmount":amount,
        "paymentMethod":paymentMethod,
        "merchantOrderId":merchantOrderId,
        "productDetails":"Tetsing using python",
        "additionalParam":"",
        "merchantUserInfo":"",
        "customerVaName":"John Doe",
        "email":"test@test.com",
        "phoneNumber":"08123456789",
        "itemDetails":[ 
            { 
                "name":"Test Item 1",
                "price":amount,
                "quantity":1
            },
        ],
        "customerDetail":{ 
            "firstName":"John",
            "lastName":"Doe",
            "email":"test@test.com",
            "phoneNumber":"08123456789",
            "billingAddress":{ 
                "firstName":"John",
                "lastName":"Doe",
                "address":"Jl. Kembangan Raya",
                "city":"Jakarta",
                "postalCode":"11530",
                "phone":"08123456789",
                "countryCode":"ID"
            },
            "shippingAddress":{ 
                "firstName":"John",
                "lastName":"Doe",
                "address":"Jl. Kembangan Raya",
                "city":"Jakarta",
                "postalCode":"11530",
                "phone":"08123456789",
                "countryCode":"ID"
            }
        },
        "callbackUrl":f"http://{YOUR_URL}/callback",
        "returnUrl":f"http://{YOUR_URL}/return",
        "signature": signature,
        "expiryPeriod":10
    }   

    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(DUITKU_REQUESTTRANSACTION_URL, json=payload, headers=headers)
    print(response)
    data = response.json()

    if response.status_code != 200:
        return jsonify({"error":  data.get("Message")}), 500
    
    print("Response Data:", data)
    if data.get("statusCode") == "00":
        return jsonify(data)  # Redirect to payment URL
    else:
        return jsonify({"error": data.get("statusMessage", "Transaction Failed")}), 400

def get_payment_methods():
    merchantCode = MERCHANT_CODE
    apiKey = API_KEY
    amount = AMOUNT
    dateTime = str(datetime.datetime.now())
    raw_signature = merchantCode + amount + dateTime + apiKey
    signature = hashlib.sha256(raw_signature.encode()).hexdigest()

    payload = {
        "merchantcode": merchantCode,
        "amount": amount,
        "datetime": dateTime,
        "signature": signature
    }   
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(DUITKU_GETPAYMENTMETHOD_URL, json=payload, headers=headers)
    
    return response.json()

def check_transaction_status(merchantOrderId):
    merchantCode = MERCHANT_CODE
    apiKey = API_KEY
    raw_signature = merchantCode + merchantOrderId + apiKey
    signature = hashlib.md5(raw_signature.encode()).hexdigest()

    payload = {
        "merchantcode": merchantCode,
        "merchantOrderId": merchantOrderId,
        "signature": signature
    } 
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(DUITKU_TRANSACTIONSTATUS_URL, json=payload, headers=headers)

    return response.json()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-payment-methods', methods=['GET'])
def get_payment():
    try:
        data = get_payment_methods()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/request-transaction', methods=['GET', 'OPTIONS'])
def get_request():
    try:
        data = request_transaction()
        return data
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/return', methods=['GET'])
def return_page():
    merchantOrderId = request.args.get("merchantOrderId")
    resultCode = request.args.get("resultCode")
    try:
        data = check_transaction_status(merchantOrderId)
        print(f"Received data from check_transaction_status: {data}")
        if resultCode == "00":
            message = f"Payment with Merchant Order Id {merchantOrderId} is SUCCESS"
            status_class = "success"
        elif resultCode == "01":
            message = f"Payment with Merchant Order Id {merchantOrderId} is PENDING"
            status_class = "pending"
        else:
            message = f"Payment with Merchant Order Id {merchantOrderId} is FAILED"
            status_class = "failed"
        return render_template('return.html', message=message, status_class=status_class)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/callback', methods=['POST'])
def callback():
    merchantCode = request.form.get("merchantCode")
    apiKey = API_KEY
    amount = request.form.get("amount")
    signature = request.form.get("signature")
    merchantOrderId = request.form.get("merchantOrderId")
    resultCode = request.form.get("resultCode")

    if all([merchantCode, amount, merchantOrderId, signature]):  # Check if all parameters are provided
        # Generate MD5 signature
        params = merchantCode + amount + merchantOrderId + apiKey
        calcSignature = hashlib.md5(params.encode()).hexdigest()
        if signature == calcSignature:
            try:
                data = check_transaction_status(merchantOrderId)
                if resultCode == "00":
                    if data.get("statusCode") == "00":
                        # Apply succes condition
                        return f"Payment with Merchant Order Id {merchantOrderId} is SUCCESS"
                    else:
                        return f"Payment with Merchant Order Id {merchantOrderId} is FORCE TO BE SUCCESS", 400
                else:
                    return f"Payment with Merchant Order Id {merchantOrderId} is FAILED", 400
            except Exception as e:
                return jsonify({"error something": str(e)}), 500
        else:
            raise Exception("Bad Signature")
    else:
        raise Exception("Missing required parameters")

if __name__ == '__main__':
    app.run(debug=True)
