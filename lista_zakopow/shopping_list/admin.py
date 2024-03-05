from django.contrib import admin

from .models import *
# Register your models here.


admin.site.register(NormalUser)
admin.site.register(ShoppingList)
admin.site.register(EditingUser)
admin.site.register(Product)

