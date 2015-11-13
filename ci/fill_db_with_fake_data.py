import hashlib
import datetime
import os
import binascii
import argparse
import subprocess
import sys
sys.path.append("src")
from gitolite import GitoliteWrapper
from db import DatabaseWrapper

__author__ = 'shawkins'


def create_bogus_key():
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


def convert_ssh_key_to_colon_string(key):
    hexstring = hashlib.md5(key.strip().split()[1]).hexdigest()
    colonstring = ':'.join(hexstring[i:i+2] for i in range(0, len(hexstring), 2))
    return colonstring

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", "--mongo_port", help="the mongodb port to connect to", type=int)
    parser.add_argument("-pyo", "--pyolite_location", help="the folder pyolite should bind to")
    args = parser.parse_args()

    password = "verybadpw"

    dbw = DatabaseWrapper(args.pyolite_location, port=args.mongo_port)
    gw = GitoliteWrapper(args.pyolite_location)

    # give one user a REAL pubkey, so git can interact with server
    # note: this is the contents of /home/git/.ssh/test_key.pub and test_key2.pub
    test_key = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDAObvHN/F6EX4L9/ExE4LdezTD1Dx/+fX0wZdropEyx63VxBn8HpgwVcjYq5fINAUAqtNoNpIgyXpp8RhoFv488qaCL9V7qwSf1Bnv5uaZ5lxIpdfEFXhu4JsgtdphMangwvSf2ADLASFdB99Sjxo/nxmjHsvyPZXuvYMNdmKn9ZBQyimUNpERlL4/ECVRoebnL4lD/+rzreacTiZA6KvPn8f7Xh8JNHwm9ndRCxflc8fTH+0VgkC2kpQVkWOoXqhQUQpX8fYxrmCamDG4oRAKJpF2SLkRv1OAv+jY58e2fxAUqFK/u2k6XFPn9Sxmz8pZsvp8OHAuVeSdECyoKw/J git@gitsubmit"
    test_key2 = "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQC8DylxzTAc4y/AG/RCONTiZx2+2hfAgfuncXwZylUse6JkHKIIFbjkXqoAkmT0hsugMHb6IpnINcc41vXXOPTwjLrgMaO7r/eK6gs6rqUiVaJ3oVuJK9qw1PwPo/4O/eCQ3mtoDSm+U27/Q5D391jAuqngmMtYxQAUqS+Hv4/ORNbCNXl/b4UQYldUz3N2giNPCIXA78CCDwz4V/jOq6zejnt+DLoiBCTnCQWCIANX+Ij5pvqBP2pDtO9RnFVHEK1O2jXUHGiLq9AcLvDDYGnATwnXbXtPn5Ub0tLFcanO4DW93WTljhCS7TyzUq/MyAGwNmwi7OSVqpNYcHvhUg37 git@gitsubmit"

    # give the users some pkeys
    bogus_key = create_bogus_key()
    gw.add_pkey_to_user("student1", bogus_key["pubkey_contents"])
    bogus_key2 = create_bogus_key()
    gw.add_pkey_to_user("student2", bogus_key2["pubkey_contents"])
    bogus_key3 = create_bogus_key()
    gw.add_pkey_to_user("teacher1", bogus_key3["pubkey_contents"])
    bogus_key4 = create_bogus_key()
    gw.add_pkey_to_user("teacher2", bogus_key4["pubkey_contents"])
    bogus_key4 = create_bogus_key()
    gw.add_pkey_to_user("spencer", bogus_key4["pubkey_contents"])
    gw.add_pkey_to_user("teacher_usable", test_key)
    gw.add_pkey_to_user("student_usable", test_key2)

    # populate the databases with some data
    dbw.create_user("student1", "student1@gmail.com", password, "Student", "One")
    dbw.create_user("student2", "student2@gmail.com", password, "Student", "Two")
    dbw.create_user("teacher1", "teacher1@gmail.com", password, "Teacher", "One")
    dbw.create_user("teacher2", "teacher2@gmail.com", password, "Teacher", "Two")
    dbw.create_user("teacher_usable", "teacher_usable@gmail.com", password, "Teacher", "Usable")
    dbw.create_user("student_usable", "student_usable@gmail.com", password, "Student", "Usable")
    dbw.create_user("spencer", "spencer@gmail.com", password, "Spencer", "Hawkins")  # because of some hardcoded stuff, heh
    dbw.create_user("konrad", "konrad@gmail.com", password, "Konrad", "Ryce")  # because of some hardcoded stuff, heh

    dbw.create_class("intro_to_computers", "Introduction to Computers", "Introduction to Computers description", "teacher1")
    dbw.create_class("adv_computers", "Advanced Computers", "Advanced Computers description", "teacher2")
    dbw.create_class("test_class", "a test class usable for actual git tests", "description", "teacher_usable")

    dbw.add_student_to_class("intro_to_computers", "student1")
    dbw.add_student_to_class("adv_computers", "student2")
    dbw.add_student_to_class("test_class", "student_usable")

    dbw.create_project("turn_on_a_computer", "Turn on a computer", "Turn on a computer description",
                       "intro_to_computers", False, (datetime.datetime.now() + datetime.timedelta(days=5)).strftime("%Y-%m-%d"), "teacher1")

    dbw.create_project("use_a_computer", "Use a computer", "Use a computer description",
                       "adv_computers", False, (datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d"), "teacher2")

    dbw.create_project("test_project", "a test project", "description",
                       "test_class", False, (datetime.datetime.now() + datetime.timedelta(days=2)).strftime("%Y-%m-%d"), "teacher_usable")

    dbw.create_submission("turned_on_a_computer", "Student 1 turned on a computer", "turn_on_a_computer", "student1")
    dbw.create_submission("used_a_computer", "Student 2 used a computer", "use_a_computer", "student2")
    dbw.create_submission("test_submission", "a test submission", "test_project", "student_usable")



