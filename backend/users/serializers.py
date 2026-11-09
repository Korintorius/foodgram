from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError
from djoser.serializers import (
    TokenCreateSerializer as DjoserCreateTokenSerializer
)
from rest_framework import serializers

from foodgram.fields import Base64ImageField
from users.constants import RECIPES_LIMIT_DEFAULT, RECIPES_LIMIT_MAX

User = get_user_model()


class TokenCreateSerializer(DjoserCreateTokenSerializer):
    """Реализация входа по email и паролю."""

    def __init__(self, *args, **kwargs):
        """Обязательность полей email и password."""
        super().__init__(*args, **kwargs)
        self.fields['email'] = serializers.EmailField(required=True)
        self.fields['password'] = serializers.CharField(
            required=True,
            write_only=True,
            style={'input_type': 'password'},
            trim_whitespace=False,
        )


class UserCreateSerializer(serializers.ModelSerializer):
    """Регистрация нового пользователя."""

    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'},
        trim_whitespace=False,
    )

    class Meta:
        model = User
        fields = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        )
        extra_kwargs = {
            'email': {'required': True, 'max_length': 254},
            'username': {'required': True, 'max_length': 150},
            'first_name': {'required': True, 'max_length': 150},
            'last_name': {'required': True, 'max_length': 150},
        }

    def validate(self, attrs):
        """Проверка введенного пароля стандартными валидаторам Django."""
        try:
            validate_password(attrs['password'], User(**attrs))
        except DjangoValidationError as error:
            raise serializers.ValidationError(
                {'password': list(error.messages)}
            )
        return attrs

    def create(self, validated_data):
        """Создание пользователя."""
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Получение данных пользователя для чтения."""

    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields: tuple[str, ...] = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

        read_only_fields: tuple[str, ...] = (
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'avatar',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        """Показывает факт подписания текущего
        пользователя на автора рецепта."""
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            return False
        return obj.subscribers.filter(subscriber=user).exists()


class UserWithRecipesSerializer(UserSerializer):
    """Пользователь вместе с его рецептами для подписок."""

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        fields = UserSerializer.Meta.fields + ('recipes_count', 'recipes')
        read_only_fields = fields

    def get_recipes_count(self, obj):
        """Возвращение количества рецептов пользователя."""
        annotated = getattr(obj, 'recipes_count', None)
        if annotated is not None:
            return annotated
        return obj.recipes.count()

    def get_recipes(self, obj):
        """Возвращение лимитированного количества рецептов."""
        from recipes.serializers import RecipeMinifiedSerializer

        request = self.context.get('request')
        raw_limit = (
            request.query_params.get('recipes_limit')
            if request else None
        )
        try:
            limit = int(raw_limit)
        except (TypeError, ValueError):
            limit = RECIPES_LIMIT_DEFAULT
        limit = max(min(limit, RECIPES_LIMIT_MAX), 0)

        return RecipeMinifiedSerializer(
            obj.recipes.all()[:limit],
            many=True,
            context=self.context
        ).data


class AvatarSerializer(serializers.ModelSerializer):
    """Загрузка аватара в формате base64-строки."""

    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)


class AvatarResponseSerializer(serializers.ModelSerializer):
    """Ответ с URL сохраненного аватара."""

    avatar = serializers.ImageField(read_only=True)

    class Meta:
        model = User
        fields = ('avatar',)
