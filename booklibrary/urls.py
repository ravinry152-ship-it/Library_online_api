from django.urls import path
from .views import(
    Login,Register,GoogleLogin,BookCategoryView,BookCategoryViewDetail,
    BookView,BookViewDetail,ForgotPasswordView,VerifyResetOTPView,ResetPasswordView,
    UserBookHistoryView
)

from rest_framework_simplejwt.views import TokenRefreshView
urlpatterns = [
    path('login/', Login.as_view(), name='login'),
    path('register/', Register.as_view(), name='register'),
    path('google-login/', GoogleLogin.as_view(), name='google-login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('categories/', BookCategoryView.as_view(), name='book-categories'),
    path('categories/<int:pk>/', BookCategoryViewDetail.as_view(), name='book-category-detail'),
    path('books/', BookView.as_view(), name='books'),
    path('books/<int:pk>/', BookViewDetail.as_view(), name='book-detail'),
    path("forgot-password/", ForgotPasswordView.as_view(), name="forgot-password"),
    path("verify-reset-otp/",VerifyResetOTPView.as_view(),name="verify-reset-otp"),
    path("reset-password/", ResetPasswordView.as_view(), name="reset-password"),
    path('user-histrory/',UserBookHistoryView.as_view(), name="user-histrory"),
]
