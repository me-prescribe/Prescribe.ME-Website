from django.db import models
from django.contrib.auth.models import User

class FeedModel(models.Model):
	name=models.CharField(max_length=200)
	em=models.EmailField(max_length=254)
	message=models.CharField(max_length=500)

class Doctor(models.Model):
	user = models.OneToOneField(User,null=True,blank=True,on_delete=models.CASCADE)
	fname = models.CharField(max_length=250,null=True)
	lname = models.CharField(max_length=250,null=True)
	sign = models.ImageField(null=True,blank=True)
	qualification = models.CharField(max_length=250,null=True)
	hname = models.CharField(max_length=250,null=True)
	reg = models.CharField(max_length=250,null=True)
	def __str__(self):
		return self.fname