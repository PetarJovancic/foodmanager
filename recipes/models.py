from django.db import models
from django.conf import settings
from django.db.models import Avg


class Ingredient(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200)
    recipe_text = models.TextField()
    ingredients = models.ManyToManyField(Ingredient)
    creator = models.ForeignKey(
                            settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    def average_rating(self):
        return self.ratings.aggregate(Avg('rating'))['rating__avg']

    def __str__(self):
        return self.name


class Rating(models.Model):
    recipe = models.ForeignKey(
                    Recipe, related_name='ratings', on_delete=models.CASCADE)
    user = models.ForeignKey(
                            settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(
                                         choices=[(i, i) for i in range(1, 6)])

    class Meta:
        unique_together = ['recipe', 'user']
