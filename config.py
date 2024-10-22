import environ

# Initialize environment variables
env = environ.Env()
environ.Env.read_env()  # Reads the .env file

# Define your environment variables
TOKEN_NOTIFY = env('TOKEN_NOTIFY')
TOKEN_AUTH = env('TOKEN_AUTH')
TOKEN_WEBHOOK=env('TOKEN_WEBHOOK')
DEBUG = env.bool('DEBUG', default=False)


