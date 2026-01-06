from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from .serializers import UserRegistrationSerializer, LoginSerializer, AuthTokenResponseSerializer
from drf_spectacular.utils import extend_schema, OpenApiTypes


class RegisterView(APIView):
    permission_classes = [AllowAny]


    @extend_schema(
        auth=[],  # public endpoint
        request= UserRegistrationSerializer,
        responses={
            201: AuthTokenResponseSerializer,
            400: OpenApiTypes.OBJECT,
        },
        summary="Register a new user",
        description=(
            "Creates a new user account and returns an authentication token. "
            "This endpoint is public and does not require authentication."
        ),
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "id": user.id,
                "username": user.username,
                "token": token.key,
            },
            status=201,
        )



class LoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        auth=[],  # public endpoint
        request=LoginSerializer,
        responses={
            200: AuthTokenResponseSerializer,
            401: OpenApiTypes.OBJECT,
        },
        summary="Login",
        description=(
            "Authenticates a user using username and password and "
            "returns an authentication token."
        ),
        tags=["Authentication"],
    )
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.validated_data["user"]
        token, _ = Token.objects.get_or_create(user=user)

        return Response(
            {
                "token": token.key,
                "user_id": user.id,
                "username": user.username,
            }
        )
