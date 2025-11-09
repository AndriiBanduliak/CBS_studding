from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from .serializers import UserRegistrationSerializer


class UserRegistrationView(generics.CreateAPIView):
    """
    API эндпоинт для регистрации нового пользователя.
    
    POST: Создать нового пользователя
    """
    serializer_class = UserRegistrationSerializer
    permission_classes = [AllowAny]  # Разрешаем регистрацию без аутентификации
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        return Response({
            'message': 'Пользователь успешно зарегистрирован.',
            'username': user.username,
            'email': user.email
        }, status=status.HTTP_201_CREATED)

