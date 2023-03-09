import os

from starlette.datastructures import CommaSeparatedStrings, Secret
from dotenv import loadenv
from databases import DatabaseURL

loadenv(".env")

MAX_CONNECTIONS_COUNT = int(os.getenv("MAX_CONNECTIONS_COUNT", 10))
MIN_CONNECTIONS_COUNT = int(os.getenv("MIN_CONNECTIONS_COUNT", 10))
SECRET_KEY = Secret(os.getenv("SECRET_KEY", "Secretgd1hgas"))

PROJECT_NAME = os.getenv("PROJECT_NAME", "Loggero")
ALLOWED_HOST = CommaSeparatedStrings(os.getenv("ALLOWED_HOSTS"), "")

MONGODB_URL = os.getenv("MONGO_URL", "")
if not MONGODB_URL:
    MONGO_HOST = os.getenv("MONGO_HOST", "localhost")
    MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
    MONGO_USER = os.getenv("MONGO_USER", "admin")
    MONGO_PASS = os.getenv("MONGO_PASSWORD", "admin_1234")
    MONGO_DB = os.getenv("MONGO_DB", "loggerodb")

    MONGODB_URL = DatabaseURL(
        f"mongodb://{MONGO_USER}:{MONGO_PASS}@{MONGO_HOST}:{MONGO_PORT}/{MONGO_DB}"
    )
else:
    MONGODB_URL = DatabaseURL(MONGODB_URL)

database_name = MONGO_DB
