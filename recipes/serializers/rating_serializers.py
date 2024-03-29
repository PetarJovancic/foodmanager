from rest_framework import serializers
from ..models import Rating
import logging


logger = logging.getLogger(__name__)


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'recipe', 'rating']

    def validate_rating(self, value):
        if not (1 <= value <= 5):
            msg = "Rating must be between 1 and 5."
            logger.warning(f"Warning in RatingSerializer: {msg}")
            raise serializers.ValidationError(msg)
        return value

    def validate(self, data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            user = request.user
            if data['recipe'].creator == user:
                msg = "You cannot rate your own recipe."
                logger.warning(f"Warning in RatingSerializer: {msg}")
                raise serializers.ValidationError(msg)
        return data
