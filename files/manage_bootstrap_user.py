#!/usr/bin/env python3
import argparse
from bioblend import galaxy

parser = argparse.ArgumentParser()
parser.add_argument("-g", "--galaxy",
                    required=True,
                    dest="galaxy_url",
                    help="Target Galaxy instance URL/IP address (required "
                            "if not defined in the tools list file)")
parser.add_argument("-a", "--apikey",
                    required=True,
                    dest="api_key",
                    help="Galaxy admin user API key (required if not "
                            "defined in the tools list file)")
parser.add_argument("-r", "--remote",
                    action="store_true",
                    help="Whether the user to be created should be a galaxy remote user, instead of a local user.")
parser.add_argument("-e", "--email",
                    required=True,
                    dest="user_email",
                    help="The email of the user to be managed.")
parser.add_argument("-u", "--username",
                    help="The username of the user to be created. Required when creating a non-remote user.")
parser.add_argument("-p", "--password",
                    dest="user_password",
                    help="The password of the user to be created. Required when creating a non-remote user.")
parser.add_argument("-d", "--delete",
                    action="store_true",
                    help="Whether to delete the user instead of creating it")
args = parser.parse_args()

if not args.remote and not args.delete and not (args.user_password and args.username):
    print("-u and -p options are required unless --remote is set.")
    exit(1)

gi = galaxy.GalaxyInstance(url=args.galaxy_url, key=args.api_key)
uc = galaxy.users.UserClient(gi)

fetched_users = gi.users.get_users(f_email=args.user_email, deleted=False)
user = None

if args.delete and len(fetched_users) != 1:
    print("User not found.")
    exit(2)

if len(fetched_users) == 1:
    user = fetched_users[0]

if args.delete:
    uc.delete_user(user['id'])
    print("Deleted user {}".format(user['username']))
    exit(0)
elif user is None:
    user = (uc.create_remote_user(user_email=args.user_email)
            if args.remote
            else uc.create_local_user(
                user_email=args.user_email,
                username=args.username,
                password=args.user_password
            ))
    print("Created user {}.".format(user['username']))

api_key = uc.get_or_create_user_apikey(user['id'])
print(api_key)
