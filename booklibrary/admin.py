from django.contrib import admin
from .models import *

admin.site.register(BookCategory)
admin.site.register(Book)
admin.site.register(UserRead)
admin.site.register(PasswordResetOTP)
