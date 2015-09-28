import hashlib
from config import GITOLITE_ADMIN_PATH
from pyolite import Pyolite
import sshpubkeys
from sshpubkeys import InvalidKeyException

__author__ = 'shawkins'


# Exceptions
class UserDoesNotExistError(Exception): pass
class KeyDoesNotExistError(Exception): pass
class KeyAlreadyExistsError(Exception): pass
class CannotDeleteOnlyKeyError(Exception): pass


# static functions
def validate_pkey_or_error(key):
    try:
        hashlib.md5(key.strip().split()[1]).hexdigest()
    except IndexError:
        raise InvalidKeyException(str(key) + " is not a valid public key!")
    # Now that we've verified that it CAN be hexdigested, let's validate with sshpubkeys
    # this will raise an InvalidKeyException if the key is... invalid
    sshpubkeys.SSHKey(key.strip())


def hexify_public_key_from_path(pubkey_path):
    with open(pubkey_path) as key_file:
        key_text = key_file.read().strip()
    return hexify_public_key_string(key_text)


def hexify_public_key_string(pubkey_string):
    # This comes from pyolite, very elegant:
    # https://github.com/PressLabs/pyolite/blob/master/pyolite/models/lists/keys.py#L22
    return hashlib.md5(pubkey_string.strip().split()[1]).hexdigest()


def add_colons_to_hash(hash_string):
    return ':'.join(hash_string[i:i+2] for i in range(0, len(hash_string), 2))


class GitoliteWrapper(object):

    def __init__(self, admin_repo):
        self.olite = Pyolite(admin_repository=admin_repo)

    def user_exists(self, username):
        return self.olite.users.get(username) is not None

    def get_user_or_error(self, username):
        if not self.user_exists(username):
            raise UserDoesNotExistError(str(username) + " does not exist in gitolite!")
        return self.olite.users.get(username)

    def add_pkey_to_user(self, username, pkey):
        validate_pkey_or_error(pkey)
        key_hex = hexify_public_key_string(pkey)
        pretty_key_hex = add_colons_to_hash(key_hex)
        if not self.user_exists(username):
            self.olite.users.create(username, key=pkey)
            return pretty_key_hex
        else:
            u = self.olite.users.get(username)
            if pretty_key_hex in self.get_list_of_pretty_key_strings(username):
                raise KeyAlreadyExistsError(str(pkey) + " already exists for user "+str(username))
            u.keys.append(pkey)
            return pretty_key_hex

    def get_list_of_key_strings(self, username):
        user = self.get_user_or_error(username)
        clean_keys = map(hexify_public_key_from_path, user.keys)
        return clean_keys

    def get_list_of_pretty_key_strings(self, username):
        pretty_keys = map(add_colons_to_hash, self.get_list_of_key_strings(username))
        return pretty_keys

    def remove_key_from_user_by_pretty_string(self, username, pretty_string):
        user = self.get_user_or_error(username)
        if len(user.keys) < 2:
            raise CannotDeleteOnlyKeyError(str(pretty_string) + " is the only key!")
        if pretty_string not in self.get_list_of_pretty_key_strings(username):
            raise KeyDoesNotExistError(str(pretty_string) + " does not exist for user "+str(username))
        for key_path in user.keys:
            pretty_key = add_colons_to_hash(hexify_public_key_from_path(key_path))
            if pretty_string == pretty_key:
                # Pyolite's keylist thing only removes by WHOLE KEY file (silly) but
                with open(key_path) as key_file:
                    key_contents = key_file.read()
                user.keys.remove(key_contents)
                return True
        return False

