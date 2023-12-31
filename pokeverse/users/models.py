from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from pokemon.models import Pokemon


class CustomUser(AbstractUser):

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.get_or_create_collection()

    def get_or_create_collection(self):
        collection = Collection.objects.get_or_create(user_id=self)
        return collection

    def add_pokemon(self, p:Pokemon):
        my_collection = self.get_or_create_collection()[0]
        my_collection.add_pokemon(p)

    def remove_pokemon(self, p:Pokemon):
        my_collection = self.get_or_create_collection()[0]
        my_collection.remove_pokemon(p)

    def get_pokemons(self):
        my_collection = self.get_or_create_collection()[0]
        return [p for p in my_collection.pokemons.all()]

class Collection(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    pokemons = models.ManyToManyField(Pokemon, related_name='pokemons')
    name = models.CharField(max_length=100, default='Моя коллекция')

    @property
    def number_of_pokemons(self):
        return self.pokemons.count()
    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('users:collection_detail')

    def add_pokemon(self, p):
        self.pokemons.add(p)

    def remove_pokemon(self,p):
        self.pokemons.remove(p)