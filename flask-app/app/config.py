"""Application configuration."""
from environs import Env

env = Env()
env.read_env()


SECRET_KEY = env.str("SECRET_KEY")


SQLALCHEMY_DATABASE_URI = env.str("SQLALCHEMY_DATABASE_URI")
SQLALCHEMY_TRACK_MODIFICATIONS = False


CLOUDFLARE_API_TOKEN = env.str("CLOUDFLARE_API_TOKEN")
DNS_ZONE_ID = env.str("DNS_ZONE_ID")


PUSHOVER_APP_TOKEN = env.str("PUSHOVER_APP_TOKEN")
PUSHOVER_USER_KEY = env.str("PUSHOVER_USER_KEY")


UPLOAD_ROUTE = env.str("UPLOAD_ROUTE")
MAX_CONTENT_LENGTH = env.int("MAX_CONTENT_LENGTH")
DATA_ROUTE = env.str("DATA_ROUTE")
DATA_LOGS_ROUTE = env.str("DATA_LOGS_ROUTE")