from yookassa import Configuration, Payment

# Set Shop ID and Secret Key
Configuration.account_id = '479313'
Configuration.secret_key = 'live_j8dRklV6-E1rbvAlBNSzdYTmWEyiOiptLLEtlz3iWkg'

# Create a payment
payment = Payment.create({
    "amount": {
        "value": "100.00",  # Amount in RUB
        "currency": "RUB"   # Currency
    },
    "confirmation": {
        "type": "redirect",  # Use redirect for payment confirmation
        "return_url": "https://stattron.ru/success"  # URL after successful payment
    },
})

# Get the confirmation URL
payment_url = payment.confirmation.confirmation_url
print(f"Payment URL: {payment_url}")
