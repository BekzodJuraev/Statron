import requests
import hashlib
import time
import uuid

url = "https://pay.freekassa.com/"
shop_id="56572"
amount='100.00'
secret_key="bekawhy"
currency='USD'
id_order='154'
signature_string = f"{shop_id}:{amount}:{secret_key}:{currency}:{id_order}"


# Create MD5 hash
signature = hashlib.md5(signature_string.encode()).hexdigest()
print(signature)

# Define the request payload, include necessary fields as per FreeKassa API documentation
data = {
    "shopId": shop_id,
    'nonce': '1123456498',
    'signature':signature,
    "amount": amount,  # Example amount in the required currency
    "currency": currency,  # Or the desired currency
    "order_id": id_order,  # Replace with your unique order ID
    "description": "Order description",
    "customer_email": "powerzver98@gmail.com",  # Optional, depending on FreeKassa API requirements
}

# Optionally, include headers if needed (for example, API key or authorization token)
headers = {
    "Authorization": "Bearer 6cc39cdabf55fc8d368f0916ea2e3428",  # Replace with your actual API key
    "Content-Type": "application/json"
}

# Make the POST request to create the order
response = requests.get(url, json=data)

# Check the response
if response.status_code == 200:
    print("Order created successfully:")
else:
    print("Failed to create order:")
