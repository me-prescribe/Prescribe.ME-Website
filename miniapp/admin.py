from django.contrib import admin
from .models import FeedModel, Doctor

# Register your models here.

admin.site.register(Doctor)
admin.site.register(FeedModel)
