# Flask Duitku Payment Gateway

This Flask application integrates with the Duitku payment gateway. It provides endpoints to request transactions, check payment methods, and handle callbacks.

## Installation

1. Clone this repository:
   ```sh
   git clone https://github.com/AkhasaDyst/DuitkuFlask.git
   ```

2. Create and activate a virtual environment:
   ```sh
   py -3 -m venv .venv
   .venv\Scripts\activate
   ```

3. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```

## Configuration

Modify the following environment variables or replace them directly in the code:

```python
MERCHANT_CODE = "YOUR_MERCHANT_CODE"
API_KEY = "YOUR_API_KEY"
YOUR_URL = "localhost:5000"
```

## Running the Application

Run the Flask app:

```sh
python duitku.py
```

The server will start at `http://localhost:5000/`.

## API Endpoints

### 1. Get Payment Methods
**GET** `/get-payment-methods`

Retrieves available payment methods from Duitku.

### 2. Request Transaction
**GET** `/request-transaction`

Initiates a transaction request to Duitku.

### 3. Handle Return URL
**GET** `/return`

Handles return URL after a payment attempt.

### 4. Handle Callback URL
**POST** `/callback`

Processes payment callbacks from Duitku.

## Logging and Debugging

- Use `print()` statements in `request_transaction()`, `check_transaction_status()`, and other functions to debug responses.
- Flask will log errors automatically when running in debug mode.

## Example Request

```sh
curl --location 'http://localhost:5000/request-transaction' \
--header 'Content-Type: application/json'
```

## Notes
- Ensure your API credentials are correct.
- Replace `sandbox` URLs with production URLs when going live.
