from rest_framework import serializers
from .models import Category, Transaction


class CategorySerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Category.
    """
    class Meta:
        model = Category
        fields = ['id', 'name', 'type', 'user']
        read_only_fields = ['user']
    
    def validate(self, data):
        """
        Проверка уникальности названия категории для пользователя.
        """
        user = self.context['request'].user
        name = data.get('name')
        
        # При создании новой категории
        if not self.instance:
            if Category.objects.filter(user=user, name=name).exists():
                raise serializers.ValidationError({
                    'name': 'Категория с таким названием уже существует.'
                })
        # При обновлении существующей категории
        else:
            if Category.objects.filter(user=user, name=name).exclude(id=self.instance.id).exists():
                raise serializers.ValidationError({
                    'name': 'Категория с таким названием уже существует.'
                })
        
        return data
    
    def create(self, validated_data):
        """
        Создание категории с автоматической привязкой к текущему пользователю.
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class TransactionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Transaction.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_type = serializers.CharField(source='category.type', read_only=True)
    
    class Meta:
        model = Transaction
        fields = [
            'id', 'user', 'category', 'category_name', 'category_type',
            'amount', 'description', 'date', 'created_at', 'updated_at'
        ]
        read_only_fields = ['user', 'created_at', 'updated_at']
    
    def validate_category(self, value):
        """
        Проверка, что категория принадлежит текущему пользователю.
        """
        user = self.context['request'].user
        if value.user != user:
            raise serializers.ValidationError(
                'Вы не можете использовать категории других пользователей.'
            )
        return value
    
    def create(self, validated_data):
        """
        Создание транзакции с автоматической привязкой к текущему пользователю.
        """
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)

