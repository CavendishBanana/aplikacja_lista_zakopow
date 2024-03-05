from django.db import models

class NormalUser(models.Model):
    nick = models.CharField(max_length = 200, blank = False, null = False)
    login = models.SlugField(max_length = 200, null = False, blank = False, unique = True)
    password = models.CharField(max_length = 600, null = False, blank = False)
    invitehash = models.CharField(max_length = 100, null=False, blank=False, unique = True, default = "aaaa")
    def __str__(self):
        return self.login


class ShoppingList(models.Model):
    name = models.CharField(max_length = 200, blank = False, null = False)
    create_date = models.DateTimeField(auto_now_add=True, null = False)
    owner = models.ForeignKey(NormalUser, on_delete =  models.CASCADE)
    editor = models.ManyToManyField(NormalUser, related_name="editionright", through="EditingUser")
    def __str__(self):
        return self.name


class EditingUser(models.Model):
    normalUser = models.ForeignKey(NormalUser, on_delete=models.CASCADE)
    shoppingList = models.ForeignKey(ShoppingList, on_delete= models.CASCADE)
    inviteAccepted = models.BooleanField(null=False, default = False)
    def __str__(self):
        return str(self.normalUser) + " " + str(self.shoppingList)

class Product(models.Model):
    description = models.CharField(max_length=300, blank = False, null = False)
    added_to_cart = models.BooleanField( default = False )
    product_list = models.ForeignKey(ShoppingList, related_name="listproducts", on_delete=models.CASCADE, null=True)
    def __str__(self):
        return self.description