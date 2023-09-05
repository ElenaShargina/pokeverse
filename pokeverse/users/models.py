from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings
from pokemon.models import Pokemon
# from pokeverse.pokemon.models import Pokemon


class CustomUser(AbstractUser):
    # @todo вынести в settings
    collectors_group_name = 'Collectors'

    def is_collector(self):
        print('HERE')
        print(self.groups.values_list('name', flat=True))
        if self.groups.filter(name=self.collectors_group_name).exists():
            return True
        else:
            return False

class Collection(models.Model):
    user_id = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )
    pokemons = models.ManyToManyField(Pokemon)
    name = models.CharField(max_length=100, default='Моя коллекция')

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('collection_detail')