from django.db import models

# Create your models here.


class Guestbook(models.Model):
    name = models.CharField(max_length=20)
    contents = models.CharField(max_length=200)
    password = models.CharField(max_length=20)
    reg_date = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Guestbook({self.name},{self.reg_date},{self.contents})'