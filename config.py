import configparser


_config = configparser.ConfigParser()
_config.read(["config.cfg"])

CLIENT_ID = _config["microsoft"]["client_id"]
CLIENT_SECRET = _config["microsoft"]["client_secret"]
REDIRECT_URI = _config["microsoft"]["redirect_uri"]
AUTHORITY = f"https://login.microsoftonline.com/{_config['microsoft']['tenant_id']}"

APP_SECRET_KEY = _config["flask"]["app_secret_key"]

DOWNLOAD_FOLDER = _config["archive"]["download_folder"]
