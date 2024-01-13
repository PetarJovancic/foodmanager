from rest_framework import serializers
from ..models import Recipe, Ingredient
from django.db import IntegrityError, transaction
from ..serializers.ingredient_serializers import IngredientSerializer
import logging


logger = logging.getLogger(__name__)


class RecipeSerializer(serializers.ModelSerializer):
    ingredient_names = serializers.ListField(
        child=serializers.CharField(),
        write_only=True
    )
    ingredients = IngredientSerializer(many=True, read_only=True)
    average_rating = serializers.FloatField(read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'recipe_text', 'ingredients',
                  'ingredient_names', 'creator', 'average_rating']
        read_only_fields = ['creator']

    def create(self, validated_data):
        ingredient_names = validated_data.pop('ingredient_names')
        ingredients = []

        try:
            with transaction.atomic():
                for name in ingredient_names:
                    ingredient, created = \
                                    Ingredient.objects.get_or_create(name=name)
                    ingredients.append(ingredient)

                recipe = Recipe.objects.create(**validated_data)
                logger.info(f"Recipe is created: {recipe}")
                recipe.ingredients.set(ingredients)
                return recipe

        except IntegrityError as e:
            logger.error(f"Error in RecipeSerializer: {e}")
            raise serializers.ValidationError(
                    {"An error occurred during recipe creation: " + str(e)})
        except Exception as e:
            logger.error(f"Error in RecipeSerializer: {e}")
            raise serializers.ValidationError(
                    {"An error occurred during recipe creation: " + str(e)})
