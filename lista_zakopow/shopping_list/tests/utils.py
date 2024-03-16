from django.contrib.auth.models import User
from shopping_list.views import hash_password

class EnvironmentSetup:
    def prepare_environment(self):
        users = User.objects.all()
        #for u in users:
        #    print(u.username)
        users_count = len( users )
        if users_count == 0:
            User.objects.create(username="adminuser", password=hash_password("!Q2w3e4r5t6y"), email = "123@example.com")
            users_count += 1
        if users_count == 1:
            User.objects.create(username="defaultuser", password=hash_password("!Q2w3e4r5t6y"), email = "123@example.com")