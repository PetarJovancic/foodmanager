from rest_framework import viewsets, permissions, status
from ..models import Recipe
from accounts.models import User
from ..serializers.recipe_serializers import RecipeSerializer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Count, Q
from django.db import DatabaseError
from rest_framework.exceptions import ValidationError, NotFound
import logging


logger = logging.getLogger(__name__)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        recipe_name = serializer.validated_data.get('name')
        user = self.request.user

        if Recipe.objects.filter(name=recipe_name, creator=user).exists():
            response = {'error': 'A recipe with this name already exists.'}
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

        try:
            serializer.save(creator=user)
        except DatabaseError as e:
            logger.error(f"Database error during recipe creation: {e}")
            return Response({
                        'error': 'An error occurred during recipe creation.'},
                        status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        except Exception as e:
            logger.error(f"Unexpected error during recipe creation: {e}")
            return Response({'error': 'An unexpected error occurred.'},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path=r'(?P<creator_id>\d+)')
    def recipes_by_creator(self, request, creator_id=None):
        try:
            if creator_id is None:
                return Response({'message': 'Creator id is not provided'},
                                status=status.HTTP_400_BAD_REQUEST)

            else:
                creator_id = int(creator_id)

                if not User.objects.filter(id=creator_id).exists():
                    raise NotFound("Creator not found")

                try:
                    recipes = self.queryset.filter(creator__id=creator_id)
                except DatabaseError as e:
                    logger.error(
                      f"Database error while fetching recipes by creator: {e}")
                    raise ValidationError(
                        "An error occurred while querying the database")

                page = self.paginate_queryset(recipes)
                serializer = self.get_serializer(page or recipes, many=True)

                result = self.get_paginated_response(serializer.data) \
                    if page else Response(serializer.data)
                logger.info(f"Filtered recipes by creator: {result}")

                return result

        except ValidationError as e:
            logger.error(f"Validation error in recipes_by_creator: {e}")
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)

        except NotFound as e:
            logger.error(
                    f"NotFound exception raised in recipes_by_creator: {e}")
            return Response({"error": e}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Unexpected error in recipes_by_creator: {e}")
            return Response({"error": "An unexpected error occurred"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='search')
    def search_recipes(self, request):
        try:
            query = request.query_params.get('query', '')
            if not query:
                return Response({'message': 'No search query provided'},
                                status=status.HTTP_400_BAD_REQUEST)

            try:
                recipes = Recipe.objects.filter(
                    Q(name__icontains=query) |
                    Q(recipe_text__icontains=query) |
                    Q(ingredients__name__icontains=query)
                ).distinct()
            except DatabaseError as e:
                logger.error(f"Database error during search: {e}")
                raise ValidationError(
                            "An error occurred while querying the database")

            page = self.paginate_queryset(recipes)
            serializer = self.get_serializer(page or recipes, many=True)

            result = self.get_paginated_response(serializer.data) \
                if page else Response(serializer.data)
            logger.info(f"Searched recipes: {result}")

            return result

        except ValidationError as e:
            return Response({"error": e}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Unexpected error in search_recipes: {e}")
            return Response({"error": "An unexpected error occurred"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='filter-by-ingredients')
    def filter_recipes_by_ingredients(self, request):
        try:
            try:
                min_count = int(request.query_params.get('min', 0))
                max_count = int(request.query_params.get('max', 10))
            except ValueError as e:
                logger.error(f"Invalid query parameters: {e}")
                raise ValidationError("Invalid query parameters")

            try:
                recipes = Recipe.objects.annotate(
                    ingredients_count=Count('ingredients')).filter(
                    ingredients_count__gte=min_count,
                    ingredients_count__lte=max_count
                )
            except DatabaseError as e:
                logger.error(f"Database error while filtering recipes: {e}")
                raise ValidationError(
                            "An error occurred while querying the database")

            page = self.paginate_queryset(recipes)
            if page is not None:
                serializer = self.get_serializer(page, many=True)
            else:
                serializer = self.get_serializer(recipes, many=True)

            result = self.get_paginated_response(serializer.data) \
                if page else Response(serializer.data)
            logger.info(f"Filtered recipes by ingredients: {result}")

            return result

        except ValidationError as e:
            return Response({'error': e}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(
                    f"Unexpected error in filter_recipes_by_ingredients: {e}")
            return Response({"error": "An unexpected error occurred"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)
