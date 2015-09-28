import hashlib
import os
import binascii
import subprocess
import requests

__author__ = 'shawkins'


class SSHKeyLib(object):
    def create_bogus_key(self):
        random_name = "bogus_key_" + binascii.b2a_hex(os.urandom(15))[:8]  # generate a random 8-char name
        callstring = "ssh-keygen -b 2048 -t rsa -f "+ random_name +" -q -N \"\""
        subprocess.call("pwd")
        subprocess.call(callstring, shell=True)
        with open(os.path.abspath(random_name + ".pub")) as pkey:
            pubkey_contents = pkey.read()
        bogus_key = {"private_path": os.path.abspath(random_name),
                     "pub_path": os.path.abspath(random_name + ".pub"),
                     "pubkey_contents": pubkey_contents}
        return bogus_key

    def convert_ssh_key_to_colon_string(self, key):
        hexstring = hashlib.md5(key.strip().split()[1]).hexdigest()
        colonstring = ':'.join(hexstring[i:i+2] for i in range(0, len(hexstring), 2))
        return colonstring
