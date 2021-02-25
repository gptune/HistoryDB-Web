from django.core.management.utils import get_random_secret_key
import json

with open("./historydb/django_keys.json", "w") as f_out:
    data = {"SECRET_KEY":str(get_random_secret_key())}
    f_out.write(json.dumps(data, indent=2))

def read_from_file(file_path):
    with open(file_path, "r") as f_in:
        return f_in.read()

with open("./historydb/email_settings.json", "w") as f_out:
    data = {}
    data["EMAIL_BACKEND"] = read_from_file("/secrets/email-backend")
    data["EMAIL_USE_TLS"] = read_from_file("/secrets/email-use-tls")
    data["EMAIL_PORT"] = read_from_file("/secrets/email-port")
    data["EMAIL_HOST"] = read_from_file("/secrets/email-host")
    data["EMAIL_HOST_USER"] = read_from_file("/secrets/email-host-user")
    data["EMAIL_HOST_PASSWORD"] = read_from_file("/secrets/email-host-password")
    data["SERVER_EMAIL"] = read_from_file("/secrets/server-email")

    import json
    f_out.write(json.dumps(data))
