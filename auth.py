import bcrypt
import uuid


def create_token():
    token = str(uuid.uuid4())
    return token


def hash_password(password):
    password = password.encode("utf-8")
    return bcrypt.hashpw(password, bcrypt.gensalt())
