from rest_framework import permissions, generics
from ..serializers.rating_serializers import RatingSerializer
from ..models import Rating
import logging


logger = logging.getLogger(__name__)


class CreateRatingView(generics.CreateAPIView):
    serializer_class = RatingSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        recipe = serializer.validated_data.get('recipe')
        user = self.request.user

        rating_instance = \
            Rating.objects.filter(recipe=recipe, user=user).first()

        if rating_instance:
            rating_instance.rating = serializer.validated_data.get('rating')
            rating_instance.save()
        else:
            serializer.save(user=user)
