from django.contrib import admin

from account.models import MyUser
from .models import MyUser

admin.site.register(MyUser)


