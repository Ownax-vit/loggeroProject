import os

from dotenv import load_dotenv
from starlette.datastructures import CommaSeparatedStrings
from starlette.datastructures import Secret

load_dotenv(".env")

JWT_TOKEN_PREFIX = "Bearer"
JWT_REFRESH_TOKEN_NAME = "refresh_token"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # one week
API_KEY_EXPIRE_DAYS = 180

SECRET_KEY = Secret(os.getenv("SECRET_KEY", "Secretgd1hgas"))

PROJECT_NAME = os.getenv("PROJECT_NAME", "Loggero")
ALLOWED_HOST = CommaSeparatedStrings(os.getenv("ALLOWED_HOSTS", "*"))

MONGODB_URL = os.getenv("MONGO_URL", "")
MONGO_DB = os.getenv("MONGO_DB", "loggerodb")

if not MONGODB_URL:
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
    MONGO_USER = os.getenv("MONGO_USER", "admin")
    MONGO_PASS = os.getenv("MONGO_PASSWORD", "admin_1234")

    MONGODB_URL = f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}?authSource=admin"

else:
    MONGODB_URL = MONGODB_URL

database_name = MONGO_DB
users_collection_name = "users"
key_collection_name = "keys"
journal_collection_name = "journals"
log_collection_name = "logs"
