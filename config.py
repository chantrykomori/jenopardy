import os
from dotenv import load_dotenv

load_dotenv()

class Config():
    LOCALHOST = os.getenv("HOST")
    LOCALUSER = os.getenv("USER")
    LOCALPASSWORD = os.getenv("PASSWORD")
    DATABASE = os.getenv("DATABASE")

    SSH_HOST = os.getenv("SSH_HOST")
    SSH_USERNAME = os.getenv("SSH_USERNAME")
    SSH_PASSWORD = os.getenv("SSH_PASSWORD")
    SSH_REMOTE_BIND_ADDRESS = os.getenv("SSH_REMOTE_BIND_ADDRESS")

    VALUE_REGULAR = [200, 400, 600, 800, 1000]
    VALUE_DOUBLE = [400, 800, 1200, 1600, 2000]

    ADMIN_ID = int(os.getenv("ADMIN_ID")) #type: ignore