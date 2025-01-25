from yookassa import Configuration, Payment

Configuration.account_id = '1020174'
Configuration.secret_key = 'test_QRyhopWIZ8ekUd7zVMTWDkUImjT-N8ajEplU3a5bXa8'

payment = Payment.create({
    "amount": {
        "value": "100.00",
        "currency": "RUB"
    },
    "confirmation": {
        "type": "redirect",  # Use redirect for payment confirmation
        "return_url": "https://stattron.ru/"  # URL after successful payment
    },
    "receipt": {
        "customer": {
            "email": "john.doe@example.com"  # Optional
        },

    }
})

# Get the confirmation URL
payment_url = payment.confirmation.confirmation_url
print(f"Payment URL: {payment_url}")
