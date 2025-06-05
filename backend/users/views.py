from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.views import View

from http import HTTPStatus
from .serializers import UserSerializer, CustomTokenObtainPairSerializer
from .models import User

# Documentación Swagger
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

# Exportamos la funcion de crear el csv
from .utils import generar_users_csv

class UserListView(APIView):
    """
    Vista API que maneja las operaciones de listado y creación de usuarios.

    Esta vista proporciona endpoints para:
    - Listar todos los usuarios del sistema
    - Crear nuevos usuarios
    """
    permission_classes = [IsAuthenticated]  # Requiere autenticación para acceder a los endpoints
    # Esquema para documentación Swagger de la respuesta de la lista de usuarios
    user_response_schema = {
        "type": "object",
        "properties": {
            "data": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "id": {"type": "integer"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "email": {"type": "string"},
                        "phone": {"type": "string"},
                        "date_joined": {"type": "string", "format": "date-time"}
                    }
                }
            }
        }
    }
    @swagger_auto_schema(
        operation_summary="Listar usuarios",
        operation_description="Obtiene una lista de todos los usuarios registrados",
        responses={
            HTTPStatus.OK.value: openapi.Response(
                description="Lista de usuarios recuperada exitosamente",
                schema=openapi.Schema(**user_response_schema)
            ),
            HTTPStatus.UNAUTHORIZED.value: "No autorizado"
        },
        tags=['Usuarios']
    )
        
    def get(self, request):
        """
        Obtiene una lista de todos los usuarios.

        Args:
            request: Objeto de solicitud HTTP.

        Returns:
            Response: Una respuesta JSON que contiene:
                - data: Lista de objetos usuario serializados
                - status: HTTP 200 OK
        """
        users = User.objects.all()
        serializer = UserSerializer(users, many=True)
        return Response({"data": serializer.data}, status=HTTPStatus.OK)
    
    @swagger_auto_schema(
        operation_summary="Crear usuario",
        operation_description="Crea un nuevo usuario en el sistema",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'password', 'first_name', 'last_name'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'password': openapi.Schema(type=openapi.TYPE_STRING),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            HTTPStatus.CREATED.value: openapi.Response(
                description="Usuario creado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'mensaje': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            HTTPStatus.BAD_REQUEST.value: "Datos inválidos",
            HTTPStatus.UNAUTHORIZED.value: "No autorizado"
        },
        tags=['Usuarios']
    )
    
    def post(self, request):
        """
        Crea un nuevo usuario.
        Args:
            request: Objeto de solicitud HTTP que contiene los datos del usuario.
        Returns:
            Response: Una respuesta JSON que contiene:
            - mensaje: Mensaje de éxito o error
            - data: Datos del usuario serializados si la creación fue exitosa
            - error: Errores de validación si la creación falla
            - status: HTTP 201 CREATED o 400 BAD REQUEST
        """
        serializer = UserSerializer(data=request.data)
        print(request.data)
        if serializer.is_valid():
            try:
                user = serializer.save()
                response_serializer = UserSerializer(user)
                return Response({
                    "mensaje": "El usuario se creó correctamente",
                    "data": response_serializer.data
                }, status=HTTPStatus.CREATED)  
            
            except Exception as e:
                print(f"Error al crear usuario: {str(e)}")  
                return Response({
                    "mensaje": "Error interno al crear el usuario",
                    "error": str(e)
                }, status=HTTPStatus.INTERNAL_SERVER_ERROR) 
        
        return Response({
            "mensaje": "Error al crear el usuario",
            "error": serializer.errors
        }, status=HTTPStatus.BAD_REQUEST)
                
class UserDetailView(APIView):
    """
    Vista API que maneja operaciones para usuarios individuales.

    Esta vista proporciona endpoints para:
    - Actualizar usuarios existentes
    - Eliminar usuarios
    """
    permission_classes = [IsAuthenticated]  # Requiere autenticación para acceder a los endpoints

    @swagger_auto_schema(
        operation_summary="Actualizar usuario",
        operation_description="Actualiza los datos de un usuario existente",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID del usuario",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'first_name': openapi.Schema(type=openapi.TYPE_STRING),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING),
                'email': openapi.Schema(type=openapi.TYPE_STRING),
                'phone': openapi.Schema(type=openapi.TYPE_STRING),
            }
        ),
        responses={
            HTTPStatus.OK.value: openapi.Response(
                description="Usuario actualizado exitosamente",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        'mensaje': openapi.Schema(type=openapi.TYPE_STRING),
                        'data': openapi.Schema(type=openapi.TYPE_OBJECT)
                    }
                )
            ),
            HTTPStatus.NOT_FOUND.value: "Usuario no encontrado",
            HTTPStatus.BAD_REQUEST.value: "Datos inválidos",
            HTTPStatus.UNAUTHORIZED.value: "No autorizado"
        },
        tags=['Usuarios']
    )
    
    def put(self, request, id):
        """
        Actualiza un usuario existente.

        Args:
            request: Objeto de solicitud HTTP con los datos actualizados del usuario.
            id: El ID del usuario a actualizar.

        Returns:
            Response: Una respuesta JSON que contiene:
                - mensaje: Mensaje de éxito o error
                - data: Datos actualizados del usuario si fue exitoso
                - error: Errores de validación si la actualización falla
                - status: HTTP 200 OK o 400 BAD REQUEST

        Raises:
            User.DoesNotExist: Si no se encuentra el usuario con el ID proporcionado.
        """
        try:
            user = User.objects.get(id=id)
            serializer = UserSerializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                user = serializer.save()
                return Response({
                    "mensaje": "El usuario se actualizó correctamente",
                    "data": UserSerializer(user).data
                }, status=HTTPStatus.OK)
            return Response({
                "mensaje": "Error al actualizar el usuario",
                "error": serializer.errors
            }, status=HTTPStatus.BAD_REQUEST)
        except User.DoesNotExist:
            return Response({
                "mensaje": "El usuario no existe"
            }, status=HTTPStatus.NOT_FOUND)     

    @swagger_auto_schema(
        operation_summary="Eliminar usuario",
        operation_description="Elimina un usuario existente",
        manual_parameters=[
            openapi.Parameter(
                'id',
                openapi.IN_PATH,
                description="ID del usuario",
                type=openapi.TYPE_INTEGER,
                required=True
            )
        ],
        responses={
            HTTPStatus.NO_CONTENT.value: "Usuario eliminado exitosamente",
            HTTPStatus.NOT_FOUND.value: "Usuario no encontrado",
            HTTPStatus.UNAUTHORIZED.value: "No autorizado"
        },
        tags=['Usuarios']
    )
    def delete(self, request, id):
        """
        Elimina un usuario existente.

        Args:
            request: Objeto de solicitud HTTP.
            id: El ID del usuario a eliminar.

        Returns:
            Response: Una respuesta JSON que contiene:
                - mensaje: Mensaje de éxito
                - status: HTTP 204 NO CONTENT

        Raises:
            User.DoesNotExist: Si no se encuentra el usuario con el ID proporcionado.
        """
        try:
            user = User.objects.get(id=id)
            user.delete()
            return Response({
                "mensaje": "El usuario se eliminó correctamente"
            }, status=HTTPStatus.NO_CONTENT)
        except User.DoesNotExist:
            return Response({
                "mensaje": "El usuario no existe"
            }, status=HTTPStatus.NOT_FOUND)
            
# clase para la vista del JWT personalizada
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer
    
class UserCSVExportView(View):
    """
    Vista para exportar usuarios a un archivo CSV.
    
    Esta vista maneja la generación y descarga de un archivo CSV con los datos de los usuarios.
    """
    @swagger_auto_schema(
        operation_summary="Exportar usuarios a CSV",
        operation_description="Descarga un archivo CSV con todos los usuarios",
        responses={
            HTTPStatus.OK.value: "Archivo CSV generado exitosamente",
            HTTPStatus.UNAUTHORIZED.value: "No autorizado"
        },
        tags=['Usuarios']
    )
    def get(self, request):
        """
        Maneja la solicitud GET para generar y descargar el archivo CSV.
        
        Args:
            request: Objeto de solicitud HTTP.
        
        Returns:
            HttpResponse: Archivo CSV con la información de los usuarios.
        """
        
        users = User.objects.all()
        return generar_users_csv(users)