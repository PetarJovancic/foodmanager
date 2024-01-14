from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Recipe


class RecipeViewSetTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(username='cope',
                                                         password='password')
        self.client.force_authenticate(user=self.user)
        self.recipe = Recipe.objects.create(name='Pizza',
                                            recipe_text='Some text',
                                            creator=self.user)

    def test_create_recipe(self):
        """
        Test creating a new recipe.
        """
        data = {'name': 'Sarma',
                'recipe_text': 'Some text',
                "ingredient_names": ["meso"]}
        response = self.client.post('/api/recipes/', data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 2)
        self.assertEqual(Recipe.objects.latest('id').name, 'Sarma')

    def test_create_duplicate_recipe(self):
        """
        Test creating a duplicate recipe.
        """
        data = {'name': 'Pizza',
                'recipe_text': 'Some text'}
        response = self.client.post('/api/recipes/', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_recipes_by_creator(self):
        """
        Test retrieving recipes by creator.
        """
        response = self.client.get(f'/api/recipes/{self.user.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipes = response.data['results']

        recipe_names = [recipe['name'] for recipe in recipes]
        self.assertIn('Pizza', recipe_names)

    def test_search_recipes(self):
        """
        Test searching for recipes.
        """
        response = self.client.get('/api/recipes/search/?query=Pizza')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipes = response.data['results']

        recipe_names = [recipe['name'] for recipe in recipes]
        self.assertIn('Pizza', recipe_names)

    def test_filter_recipes_by_ingredients(self):
        """
        Test filtering recipes by the number of ingredients.
        """
        data = {'name': 'Sarma',
                'recipe_text': 'Some text',
                "ingredient_names": ["meso", "kupus", "biber", "so", "luk"]}
        response = self.client.post('/api/recipes/', data)
        response = self.client.get(
                        '/api/recipes/filter-by-ingredients/?min=4&max=5')
        recipes = response.data

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(recipes['count'] == 1)
