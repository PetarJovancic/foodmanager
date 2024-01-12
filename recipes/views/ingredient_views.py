from rest_framework import status
from ..models import Ingredient
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Count
import logging


logger = logging.getLogger(__name__)


class TopIngredientsView(APIView):
    def get(self, request):
        try:
            top_ingredients = Ingredient.objects.annotate(
                num_recipes=Count('recipe')
            ).order_by('-num_recipes')[:5]

            data = [
                {"ingredient": ingredient.name, 
                 "recipes_count": ingredient.num_recipes}
                for ingredient in top_ingredients
            ]
            logger.info('Top 5 ingredients: ', data)

            return Response(data)

        except Exception as e:
            logger.error(f"Error in TopIngredientsView: {e}")
            return Response(
                {"error": "An error occurred while fetching top ingredients."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
