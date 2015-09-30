__author__ = 'Tsintsir'

from binascii import b2a_hex
from os import urandom
from pymongo import MongoClient
from pbkdf2 import PBKDF2


class UsernameAlreadyTakenError(Exception): pass
class EmailAlreadyTakenError(Exception): pass


def create_user(username, email, password):
    client = MongoClient()
    db = client.gitsubmit.users
    username_check_doc = db.find_one({"username": username})
    if username_check_doc is not None:
        raise UsernameAlreadyTakenError("That username is already taken.");
    email_check_doc = db.find_one({"email": email})
    if email_check_doc is not None:
        raise EmailAlreadyTakenError("That email address is already taken.");
    salt = urandom(256)
    db.insert_one(
        {
            "username": username,
            "email":    email,
            "salt":     salt,
            "hash":     b2a_hex(PBKDF2(password, salt).read(256))
        }
    )


def login(username, password):
    client = MongoClient()
    db = client.gitsubmit.users
    user_doc = db.find_one({"username": username})
    if user_doc is None:
        return False
    else:
        salt = user_doc["salt"]
        if b2a_hex(PBKDF2(password, salt).read(256)) == user_doc["hash"]:
            return True
        else:
            return False