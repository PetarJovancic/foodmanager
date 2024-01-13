from rest_framework.exceptions import ValidationError
from pyhunter import PyHunter
from django.conf import settings
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, LoginSerializer
import requests
import logging


logger = logging.getLogger(__name__)


class CreateUserView(generics.CreateAPIView):
    serializer_class = UserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data.get('email')

        try:
            # Email verification with PyHunter
            hunter = PyHunter(settings.HUNTER_API_KEY)
            hunter_response = hunter.email_verifier(email)
            logger.debug(f"hunter_response: {hunter_response['status']}")
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error occurred during API calls: {e}")
            return Response({'error': 'Network error occurred'},
                            status=status.HTTP_503_SERVICE_UNAVAILABLE)

        if hunter_response['status'] != 'valid':
            return Response({'error': 'Invalid email address'},
                            status=status.HTTP_400_BAD_REQUEST)

        # Clearbit enrichment
        clearbit_data = self.lookup_email(email)
        if clearbit_data and 'person' in clearbit_data:
            person_data = clearbit_data.get('person', {})
            serializer.save(
                first_name=person_data.get('name', {}).get('givenName', ''),
                last_name=person_data.get('name', {}).get('familyName', ''),
                bio=person_data.get('bio', ''),
                location=person_data.get('location', ''),
                phone=person_data.get('phone', '')
            )
        else:
            serializer.save()

        logger.info("User is being registered")
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @staticmethod
    def lookup_email(email):
        clearbit_key = settings.CLEARBIT_API_KEY[0]
        base_url = \
            'https://person.clearbit.com/v2/combined/find?email=' + email

        try:
            response = requests.get(base_url, auth=(clearbit_key, ''))

            if response.status_code == 200:
                return response.json()
            else:
                return None
        except Exception as e:
            logger.error(f"Error occured while fetching clearbit data: {e}")
            return None


class LoginView(generics.GenericAPIView):
    serializer_class = LoginSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except ValidationError as e:
            logger.info(
               f"Failed login attempt for {request.data.get('username')}: {e}")

            return Response({'error': 'Invalid credentials'},
                            status=status.HTTP_401_UNAUTHORIZED)

        user = serializer.validated_data
        refresh = RefreshToken.for_user(user)

        logger.info(f"User {user.username} logged in successfully")
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
        })
