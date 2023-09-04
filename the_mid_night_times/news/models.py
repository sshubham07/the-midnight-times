from django.db import models
from django.contrib.auth.models import User


class Block(models.Model):
    name = models.OneToOneField(User, on_delete=models.CASCADE)
    blocked = models.BooleanField(default=False)
    
    def __str__(self):
        return str(self.name)
    
class History(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    keyword = models.CharField(max_length=255)
    timestamp = models.DateTimeField(auto_now_add=True)



