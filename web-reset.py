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
    data["EMAIL_BACKEND"] = read_from_file("/email-setting/email-backend")
    data["EMAIL_USE_TLS"] = read_from_file("/email-setting/email-use-tls")
    data["EMAIL_PORT"] = read_from_file("/email-setting/email-port")
    data["EMAIL_HOST"] = read_from_file("/email-setting/email-host")
    data["EMAIL_HOST_USER"] = read_from_file("/email-setting/email-host-user")
    data["EMAIL_HOST_PASSWORD"] = read_from_file("/email-setting/email-host-password")
    data["SERVER_EMAIL"] = read_from_file("/email-setting/server-email")

    import json
    f_out.write(json.dumps(data))

with open("./historydb/google_recaptcha_keys.json", "w") as f_out:
    data = {}
    data["SITE_KEY"] = read_from_file("/recaptcha-setting/google_recaptcha_site_key")
    data["SECRET_KEY"] = read_from_file("/recaptcha-setting/google_recaptcha_secret_key")

    import json
    f_out.write(json.dumps(data))
