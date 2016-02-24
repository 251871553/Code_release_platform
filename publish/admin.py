from django.contrib import admin

# Register your models here.

from .models import User,Authv1,Authv2,Authv3



admin.site.register(User)
admin.site.register(Authv1)
admin.site.register(Authv2)
admin.site.register(Authv3)
