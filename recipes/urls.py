from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views.recipe_views import RecipeViewSet
from .views.rating_views import CreateRatingView
from .views.ingredient_views import TopIngredientsView


router = DefaultRouter()
router.register(r'', RecipeViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('rate', CreateRatingView.as_view(), name='rate-recipe'),
    path(
      'top-ingredients', TopIngredientsView.as_view(), name='top-ingredients'),
]
