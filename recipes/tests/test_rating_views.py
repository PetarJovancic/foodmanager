from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from rest_framework import status
from ..models import Recipe, Rating


class CreateRatingViewTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
                                                        username='cope1',
                                                        password='password')
        self.second_user = get_user_model().objects.create_user(
                                                        username='cope2',
                                                        password='password')
        self.client.force_authenticate(user=self.second_user)
        self.recipe = Recipe.objects.create(name='Gulas',
                                            recipe_text='Some text',
                                            creator=self.second_user)

    def test_user_cannot_rate_own_recipe(self):
        """
        Test that a user cannot rate their own recipe.
        """
        self.client.force_authenticate(user=self.second_user)
        data = {'recipe': self.recipe.id, 'rating': 5}
        response = self.client.post('/api/recipes/rate', data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_rating(self):
        """
        Test creating a new rating.
        """
        self.client.force_authenticate(user=self.user)
        data = {'recipe': self.recipe.id, 'rating': 5}
        response = self.client.post('/api/recipes/rate', data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Rating.objects.get().rating, 5)

    def test_update_existing_rating(self):
        """
        Test updating an existing rating by the same user.
        """
        Rating.objects.create(recipe=self.recipe,
                              user=self.user,
                              rating=3)
        self.assertEqual(Rating.objects.get(recipe=self.recipe,
                                            user=self.user).rating, 3)

        self.client.force_authenticate(user=self.user)
        data = {'recipe': self.recipe.id, 'rating': 5}
        response = self.client.post('/api/recipes/rate', data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Rating.objects.get(recipe=self.recipe,
                                            user=self.user).rating, 5)
