from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from ..models import Ingredient, Recipe


class TopIngredientsViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        user = get_user_model().objects.create_user('cope', 'string')

        ingredient1 = Ingredient.objects.create(name='Meso')
        ingredient2 = Ingredient.objects.create(name='So')
        ingredient3 = Ingredient.objects.create(name='Biber')
        ingredient4 = Ingredient.objects.create(name='Vegeta')
        ingredient5 = Ingredient.objects.create(name='Ulje')
        ingredient6 = Ingredient.objects.create(name='Kupus')
        ingredient7 = Ingredient.objects.create(name='Paradajz')
        ingredient8 = Ingredient.objects.create(name='Pasta')

        recipe1 = Recipe.objects.create(name='Sarme', creator=user)
        recipe1.ingredients.add(ingredient1,
                                ingredient2,
                                ingredient3,
                                ingredient4,
                                ingredient5,
                                ingredient6)
        recipe2 = Recipe.objects.create(name='Gulas', creator=user)
        recipe2.ingredients.add(ingredient1,
                                ingredient2,
                                ingredient3,
                                ingredient4,
                                ingredient5,
                                ingredient7)
        recipe3 = Recipe.objects.create(name='Bolonjeze', creator=user)
        recipe3.ingredients.add(ingredient1,
                                ingredient2,
                                ingredient3,
                                ingredient4,
                                ingredient5,
                                ingredient8)

    def test_top_ingredients(self):
        """
        Test fetching top 5 ingredients used in recipes.
        """
        response = self.client.get('/api/recipes/top-ingredients')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 5)
        self.assertContains(response, 'Meso')
        self.assertContains(response, 'So')
        self.assertContains(response, 'Biber')
        self.assertContains(response, 'Vegeta')
        self.assertContains(response, 'Ulje')
        self.assertNotContains(response, 'Kupus')
        self.assertNotContains(response, 'Paradajz')
        self.assertNotContains(response, 'Pasta')
