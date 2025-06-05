from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework import serializers
from django.contrib.auth import authenticate
from users.models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'phone', 'password', 'date_joined']
        read_only_fields = ['id', 'date_joined']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        # Extraemos la contraseña de los datos validados
        password = validated_data.pop('password')
        email = validated_data.pop('email')

        
        # Creamos el usuario usando nuestro UserManager personalizado
        user = User.objects.create_user(
            email=email,
            password=password,
            **validated_data
        )
        return user
    
    def update(self, instance, validated_data):
        # Si se está actualizando la contraseña, la hasheamos
        password = validated_data.pop('password', None)
        
        # Actualizamos los demás campos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        # Si hay una nueva contraseña, la establecemos correctamente
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    username_field = User.EMAIL_FIELD  # Usa el email como identificador
    
    def validate(self, attrs):
        email = attrs.get("email")
        password = attrs.get("password")
        
        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError("Credenciales incorrectas o usuario inactivo", code='authorization')
        else:
            raise serializers.ValidationError("Se requiere email y contraseña", code='authorization')
        
        data = super().validate(attrs)
        data['user'] = {
            "id": user.id,
            "email": user.email,
            "first_name": user.first_name,
            "last_name": user.last_name,
        }
        return data

