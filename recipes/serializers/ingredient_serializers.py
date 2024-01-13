from rest_framework import serializers
from ..models import Ingredient
import logging


logger = logging.getLogger(__name__)


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ['id', 'name']
