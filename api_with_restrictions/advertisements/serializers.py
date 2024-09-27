from django.contrib.auth.models import User
from rest_framework import serializers

from advertisements.models import Advertisement


class UserSerializer(serializers.ModelSerializer):
    """Serializer для пользователя."""

    class Meta:
        model = User
        fields = ('id', 'username', 'first_name',
                  'last_name',)


class AdvertisementSerializer(serializers.ModelSerializer):
    """Serializer для объявления."""

    creator = UserSerializer(
        read_only=True,
    )

    class Meta:
        model = Advertisement
        fields = ('id', 'title', 'description', 'creator',
                  'status', 'created_at', )

    def create(self, validated_data):
        """Метод для создания"""

        # Простановка значения поля создатель по-умолчанию.
        # Текущий пользователь является создателем объявления
        # изменить или переопределить его через API нельзя.
        # обратите внимание на `context` – он выставляется автоматически
        # через методы ViewSet.
        # само поле при этом объявляется как `read_only=True`
        validated_data["creator"] = self.context["request"].user
        return super().create(validated_data)

    def validate(self, data):
        """Метод для валидации. Вызывается при создании и обновлении."""

        request = self.context.get("request")
        user = request.user
        adv = self.context.get("view").kwargs.get("pk")

        if user.is_anonymous:
            raise serializers.ValidationError("You are not authorized")

        # TODO: добавьте требуемую валидацию

        if adv:
            if request.method == "PUT":
                if Advertisement.objects.get(pk=adv).creator != user:
                    raise serializers.ValidationError("You are not authorized")
        if request.method == "POST":
            if Advertisement.objects.filter(creator=user).count() >= 10:
                raise serializers.ValidationError("You are not authorized")

        return data

    def destroy(self, instance):

        if instance.creator == self.context["request"].user:
            return super().destroy(instance)
        else:
            raise serializers.ValidationError("You are not authorized")