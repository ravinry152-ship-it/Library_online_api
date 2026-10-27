from rest_framework import serializers
from.models import(
    BookCategory,
    Book,
    UserRead
)

class BookCategorySerializer(serializers.ModelSerializer):
    class Meta :
        model = BookCategory
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer) :
    class Meta:
        model = Book
        fields = [
            'id',
            'book_name',
            'book_image',
            'book_file',
            'category',
            'user',
            'description'
        ]
        read_only_fields = ['user']

class UserReadSerializer(serializers.ModelSerializer) :
    class Meta :
        model = UserRead
        fields = '__all__'