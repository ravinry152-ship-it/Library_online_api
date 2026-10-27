from django.db import models
from django.contrib.auth.models import User
from django.conf import settings

class BookCategory(models.Model) :
    id = models.AutoField(primary_key= True)
    book_category = models.CharField(max_length=100, db_index=True)
    def __str__(self) :
        return self.book_category

class Book(models.Model) :
    id = models.AutoField(primary_key= True)
    book_name = models.CharField(max_length=200)
    book_image = models.ImageField(upload_to='book_images/', max_length=200)
    book_file = models.FileField(upload_to='book/',max_length=500)
    description = models.TextField(null=True, blank=True)
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    category = models.ForeignKey(BookCategory, on_delete=models.CASCADE)
    def __str__(self) :
        return self.book_name

class UserRead(models.Model) :
    id = models.AutoField(primary_key =True)
    user = models.ForeignKey(User, on_delete= models.CASCADE)
    book = models.ForeignKey(Book, on_delete = models.CASCADE)

class PasswordResetOTP(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="password_reset_otps",
    )

    otp_hash = models.CharField(max_length=256)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    attempts = models.PositiveSmallIntegerField(default=0)
    verified_at = models.DateTimeField(null=True, blank=True)

    reset_token_hash = models.CharField(
        max_length=64,
        blank=True,
        default="",
    )
    reset_token_expires_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    used_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Password reset OTP for user {self.user_id}"