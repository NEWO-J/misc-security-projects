import paramiko

bad_keys = set(['ssh-rsa', 'ssh-dss'])

def auditKeys(host, user, passw):
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(
        hostname=host, 
        username=user, 
        password=passw
    )

    transport = client.get_transport()

    key = transport.get_remote_server_key().get_name()
    if key in bad_keys:
        return True

    return False

if __name__ == "__main__":
    result = auditKeys("localhost", "anonymous", "password")
    if result:
        print("Server selected a weak key!")
    else:
        print("No weak/deprecated key found")