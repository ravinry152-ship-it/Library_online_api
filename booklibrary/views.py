import hashlib
import secrets
import logging
from datetime import timedelta
from django.contrib.auth.hashers import make_password, check_password
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from django.utils import timezone
from .models import PasswordResetOTP
from rest_framework.views import APIView  
from rest_framework.response import Response
from rest_framework import  status
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from .models import (
    BookCategory,
    Book,
    UserRead
)
from django.contrib.auth.models import User
from dj_rest_auth.registration.views import SocialLoginView # pyright: ignore[reportMissingImports]
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.github.views import GitHubOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from .serializer import(
    BookCategorySerializer,
    BookSerializer,
    UserReadSerializer
)
from django.core.cache import cache
from rest_framework.parsers import MultiPartParser, FormParser
class Register(APIView) :
    authentication_classes = []
    def post(self , request , format =None) :
        try :
            username = request.data.get('username')
            email = request.data.get('email')
            password = request.data.get('password')
            if not email or not password or not username :
                return Response({
                    'error': "Username, email, and password are required"
                }, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(username=username).exists():
                return Response({'error': 'គណនីនេះត្រូវបានចុះឈ្មោះរួចហេីយ'}, status=status.HTTP_400_BAD_REQUEST)
            if User.objects.filter(email=email).exists():
                return Response({'error': 'គណនីនេះធ្លាប់បានចុះឈ្មោះរួចហេីយ'}, status=status.HTTP_400_BAD_REQUEST)
            user = User.objects.create_user(username=username, email=email, password=password)
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)
        except Exception as e :
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
#====================================Login_api======================================

class Login(APIView) :
    authentication_classes = []
    def post(self , request , format=None) :
        email = request.data.get('email')
        password = request.data.get('password')
        
        # កែប្រែលក្ខខណ្ឌឆែកត្រឹមតែ email និង password
        if not email or not password :
            return Response({
                'error': "សូមបញ្ចូល Email និងលេខសម្ងាត់ឱ្យបានត្រឹមត្រូវ"   
            }, status=status.HTTP_400_BAD_REQUEST)
            
        try :
            user_obj = User.objects.get(email=email)
            username = user_obj.username 
        except User.DoesNotExist :
            return Response({
                'error': "មិនមានគណនីប្រើប្រាស់អ៊ីម៉ែលនេះទេ"
            }, status=status.HTTP_404_NOT_FOUND)
            
        if user_obj is not None :
            if user_obj.check_password(password):
                refresh = RefreshToken.for_user(user_obj)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                    'username': username
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    'error': "ពាក្យសម្ងាត់មិនត្រឹមត្រូវទេ"
                }, status=status.HTTP_400_BAD_REQUEST)

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://127.0.0.1:8000/accounts/google/login/callback/" 
    client_class = OAuth2Client

# 2. Facebook Login View
class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter

# 3. GitHub Login View
class GitHubLogin(SocialLoginView):
    adapter_class = GitHubOAuth2Adapter
    callback_url = "http://127.0.0.1:8000/accounts/github/login/callback/"
    client_class = OAuth2Client

class BookCategoryView(APIView) :
    permission_classes = [IsAuthenticated]
    def get(self, request):
        cache_key = "category_book_List"
        bookcategory_cache = cache.get(cache_key)
        if bookcategory_cache is not None:
            print("Load Data from Cache")
            return Response(bookcategory_cache, status=status.HTTP_200_OK)

        else :
            print("Load data from DB")
            bookcategory = BookCategory.objects.all()
            serializer = BookCategorySerializer(bookcategory, many=True)
            cache.set(cache_key, serializer.data, timeout=900)
            return Response(serializer.data, status=status.HTTP_200_OK)


    def post(self, request) :
        serializer = BookCategorySerializer(data = request.data)
        if serializer.is_valid() :
            serializer.save()
            cache.delete("category_book_List")
            return Response(serializer.data, status= status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status= status.HTTP_400_BAD_REQUEST)

class BookCategoryViewDetail(APIView) :
    permission_classes = [IsAuthenticated]
    def get_object(self, request, pk) :
        try :
            return BookCategory.objects.get(pk=pk)
        except BookCategory.DoesNotExist :
            return Response({
                'error': "Category not found"
            }, status=status.HTTP_404_NOT_FOUND)

    def get(self, request, pk) :
        bookcategory = self.get_object(request, pk)
        if bookcategory is None :
            return Response({
                "error": "Category not found"
            }, status=status.HTTP_404_NOT_FOUND)
        serializer= BookCategorySerializer(bookcategory)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request,pk) :
        bookcategory = self.get_object(request,pk)
        if bookcategory is None :
            return Response({
                "error": "Category not found"
            }, status=status.HTTP_404_NOT_FOUND)
        serializer = BookCategorySerializer(bookcategory, data=request.data)
        if serializer.is_valid() :
            serializer.save()
            cache.delete("category_book_List")
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk) :
        bookcategory = self.get_object(request,pk)
        if bookcategory is None :
            return Response({
                "error": "Category not found"
            }, status=status.HTTP_404_NOT_FOUND)
        bookcategory.delete()
        cache.delete("category_book_List")
        return Response({
            "message": "Category deleted successfully"
        }, status=status.HTTP_200_OK)


class BookView(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]
    def get(self, request):
        cache_key = "book_List"
        book_cache = cache.get(cache_key)

        if book_cache is not None:
            print("Load Data from Cache")
            return Response(book_cache, status=status.HTTP_200_OK)

        print("Load data from DB")

        books = Book.objects.all().order_by("-id")
        serializer = BookSerializer(books, many=True)

        cache.set(cache_key, serializer.data, timeout=900)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def post(self, request):
        serializer = BookSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save(user=request.user)

            cache.delete("book_List")

            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )

        print(serializer.errors)

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


class BookViewDetail(APIView):
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_object(self, pk):
        try:
            return Book.objects.get(pk=pk)
        except Book.DoesNotExist:
            return None

    def get(self, request, pk):
        book = self.get_object(pk)

        if book is None:
            return Response(
                {"error": "Book not found"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = BookSerializer(book)

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    def put(self, request, pk):
        book = self.get_object(pk)

        if book is None:
            return Response(
                {"error": "Book not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        if book.user != request.user:
            return Response(
                {"error": "You do not have permission to edit this book."},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = BookSerializer(
            book,
            data=request.data,
            partial=True
        )

        if serializer.is_valid():
            serializer.save(user=request.user)

            cache.delete("book_List")

            return Response(
                serializer.data,
                status=status.HTTP_200_OK
            )

        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )

    def delete(self, request, pk):
        book = self.get_object(pk)

        if book is None:
            return Response(
                {"error": "Book not found"},
                status=status.HTTP_404_NOT_FOUND
            )
        #  ឆែកមើលសិទ្ធិម្ចាស់សៀវភៅមុននឹងលុប
        if book.user != request.user:
            return Response(
                {"error": "You do not have permission to delete this book."},
                status=status.HTTP_403_FORBIDDEN
            )

        book.delete()

        cache.delete("book_List")

        return Response(
            {"message": "Book deleted successfully"},
            status=status.HTTP_200_OK
        )

class UserBookHistoryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # ទាញយកតែសៀវភៅណាដែលបង្ហោះដោយ User កំពុង Login ស្រាប់
        books = Book.objects.filter(user=request.user)
        serializer = BookSerializer(books, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


    
logger = logging.getLogger(__name__)


def hash_reset_token(token):
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


class ForgotPasswordView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip()

        if not email:
            return Response(
                {"error": "សូមបញ្ចូល Email"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # ប្រើសារទូទៅ ដើម្បីកុំបង្ហាញថា Email មានគណនីឬអត់
        response_data = {
            "message": (
                "បើ Email នេះមានគណនី "
                "អ្នកនឹងទទួលបាន OTP តាម Email។"
            )
        }

        user = User.objects.filter(
            email__iexact=email,
            is_active=True,
        ).first()

        if user is None:
            return Response(response_data, status=status.HTTP_200_OK)

        now = timezone.now()

        # លុប OTP ចាស់ដែលមិនទាន់បានប្រើ
        PasswordResetOTP.objects.filter(
            user=user,
            used_at__isnull=True,
        ).delete()

        otp = f"{secrets.randbelow(1_000_000):06d}"

        record = PasswordResetOTP.objects.create(
            user=user,
            otp_hash=make_password(otp),
            expires_at=now + timedelta(minutes=10),
        )

        try:
            send_mail(
                subject="Password Reset OTP",
                message=(
                    f"Your password reset OTP is: {otp}\n\n"
                    "This code expires in 10 minutes.\n"
                    "If you did not request this, ignore this email."
                ),
                from_email=None,
                recipient_list=[user.email],
                fail_silently=False,
            )
        except Exception:
            logger.exception("Failed to send password reset OTP")
            record.delete()

            # កុំបង្ហាញព័ត៌មានលម្អិតរបស់ SMTP ទៅ Client
            return Response(
                {"error": "មិនអាចផ្ញើ OTP បានទេ។ សូមសាកល្បងម្ដងទៀត។"},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        return Response(response_data, status=status.HTTP_200_OK)


class VerifyResetOTPView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip()
        otp = (request.data.get("otp") or "").strip()

        if not email or len(otp) != 6 or not otp.isdigit():
            return Response(
                {"error": "សូមបញ្ចូល Email និង OTP 6 ខ្ទង់ឱ្យបានត្រឹមត្រូវ"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(
            email__iexact=email,
            is_active=True,
        ).first()

        if user is None:
            return Response(
                {"error": "OTP មិនត្រឹមត្រូវ ឬផុតកំណត់"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        record = PasswordResetOTP.objects.filter(
            user=user,
            expires_at__gt=now,
            verified_at__isnull=True,
            used_at__isnull=True,
        ).order_by("-created_at").first()

        if record is None or record.attempts >= 5:
            return Response(
                {"error": "OTP មិនត្រឹមត្រូវ ឬផុតកំណត់"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        record.attempts += 1

        if not check_password(otp, record.otp_hash):
            record.save(update_fields=["attempts"])
            return Response(
                {"error": "OTP មិនត្រឹមត្រូវ ឬផុតកំណត់"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # បង្កើត Token សម្រាប់ Reset Password
        reset_token = secrets.token_urlsafe(32)

        record.verified_at = now
        record.reset_token_hash = hash_reset_token(reset_token)
        record.reset_token_expires_at = now + timedelta(minutes=10)

        record.save(update_fields=[
            "attempts",
            "verified_at",
            "reset_token_hash",
            "reset_token_expires_at",
        ])

        return Response(
            {
                "message": "OTP ត្រឹមត្រូវ",
                "reset_token": reset_token,
            },
            status=status.HTTP_200_OK,
        )


class ResetPasswordView(APIView):
    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        email = (request.data.get("email") or "").strip()
        reset_token = request.data.get("reset_token") or ""
        new_password = request.data.get("new_password") or ""

        if not email or not reset_token or not new_password:
            return Response(
                {"error": "សូមបំពេញព័ត៌មានឱ្យបានគ្រប់គ្រាន់"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user = User.objects.filter(
            email__iexact=email,
            is_active=True,
        ).first()

        if user is None:
            return Response(
                {"error": "Reset Token មិនត្រឹមត្រូវ ឬផុតកំណត់"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        now = timezone.now()

        record = PasswordResetOTP.objects.filter(
            user=user,
            verified_at__isnull=False,
            used_at__isnull=True,
            reset_token_expires_at__gt=now,
        ).order_by("-verified_at").first()

        if (
            record is None
            or not secrets.compare_digest(
                record.reset_token_hash,
                hash_reset_token(reset_token),
            )
        ):
            return Response(
                {"error": "Reset Token មិនត្រឹមត្រូវ ឬផុតកំណត់"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            validate_password(new_password, user=user)
        except ValidationError as exc:
            return Response(
                {"error": list(exc.messages)},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(new_password)
        user.save(update_fields=["password"])

        record.used_at = now
        record.save(update_fields=["used_at"])

        # លុប OTP/Token ដែលនៅសល់សម្រាប់គណនីនេះ
        PasswordResetOTP.objects.filter(
            user=user,
            used_at__isnull=True,
        ).delete()

        return Response(
            {"message": "កំណត់ Password ថ្មីបានជោគជ័យ"},
            status=status.HTTP_200_OK,
        )
