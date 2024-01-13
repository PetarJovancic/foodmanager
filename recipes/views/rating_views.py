from rest_framework import permissions, generics
from ..serializers.rating_serializers import RatingSerializer
import logging


logger = logging.getLogger(__name__)


class CreateRatingView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]
