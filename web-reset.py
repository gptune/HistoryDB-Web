from django.core.management.utils import get_random_secret_key
import json

with open("./historydb/django_keys.json", "w") as f_out:
    data = {"SECRET_KEY":str(get_random_secret_key())}
    f_out.write(json.dumps(data, indent=2))
