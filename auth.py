import bcrypt


def hash_password(password):
    password = password.encode("utf-8")
    return bcrypt.hashpw(password, bcrypt.gensalt())
