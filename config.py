import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()  # Reads the .env file

# Define your environment variables
TOKEN_NOTIFY = env('TOKEN_NOTIFY')
TOKEN_AUTH = env('TOKEN_AUTH')
TOKEN_WEBHOOK=env('TOKEN_WEBHOOK')
ID_OWNER_TELGRAM=env('ID_OWNER_TELGRAM')
URL=env("URL")
SHOP_ID=env("SHOP_ID")
SECRET_KEY=env("SECRET_KEY")
CUR=env("CUR")
CUR_RUB=env("CUR_RUB")
Wallet_public=env("Wallet_public")
Wallet_private=env("Wallet_private")
YOOKASSA_ID=env('YOOKASSA_ID')
YOOKASSA_SECRET_KEY=env('YOOKASSA_SECRET_KEY')
DEBUG = env.bool('DEBUG', default=False)


