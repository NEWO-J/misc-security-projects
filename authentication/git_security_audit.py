import re
import os
import stat

SSH_CONFIG_CHECK = re.compile(r"^IdentityFile\s+~/\.ssh/[^/\0]+$")

def check_key_perms():
    with open("/home/jblu0/.ssh/config", "r") as config:
        for line in config:
            if line.strip() == "Host github.com":
                result = None
                break
        for line in config:
            result = re.match(SSH_CONFIG_CHECK, line.strip())
            if not result:
                continue
            entry = result.group()
            private_key = entry.split(" ")[1]
            try:
                perms = os.stat(private_key)
            except FileNotFoundError:
                print(f"~/.ssh/config Private Key Path Not Found! - {private_key}")
                exit()

            match perms.st_mode:
                case 0o600:
                    return 1
                case 0o700:
                    return 1
                case _:
                    return 0


def check_repo_secrets():
    