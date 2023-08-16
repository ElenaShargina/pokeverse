from django.contrib import admin
from .models import Pokemon
from .models import Ability
from .models import Collection


class PokemonModelAdmin(admin.ModelAdmin):
    list_display = ['pokeapi_id', 'name', 'base_experience', 'height', 'weight']
    fieldsets = [
        (None, {'fields':['pokeapi_id', 'name']}),
        ('Chars', {'fields':['base_experience', 'height', 'weight']}),
        ('Abilities',{'fields':['abilities']}),
        ('Images',{'fields':['image_big', 'image_small_front', 'image_small_back']})
    ]

    list_display_links = ['name']
    # list_filter = ['pokeapi_id']
    search_fields = ['name', 'pokeapi_id', 'name']
    filter_vertical = ['abilities',]

    class Meta:
         model = Pokemon

class CollectionModelAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'name']
    list_display_links = ['user_id']
    # list_filter = ['pokeapi_id']
    search_fields = ['user_id']

class AbilityModelAdmin(admin.ModelAdmin):

    @admin.display(description='Name')
    def capitalize_name(self, obj):
        return str.capitalize(obj.name)

    list_display = ['pokeapi_id','capitalize_name', 'effect_entry_short', 'number_of_users']
    list_display_links = ['capitalize_name']
    search_fields = ['effect_entry']


admin.site.register(Pokemon, PokemonModelAdmin)
admin.site.register(Collection, CollectionModelAdmin)
admin.site.register(Ability, AbilityModelAdmin)
