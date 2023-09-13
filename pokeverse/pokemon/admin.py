from django.contrib import admin
from .models import Pokemon, Ability, SpeciesPokemon, TypePokemon
from django.urls import reverse
from django.utils.html import format_html
from django.db import models

def url_to_edit_object(obj):
    url = reverse(f'admin:{obj._meta.app_label}_{obj._meta.model_name}_change',args=[obj.pk])
    return u'<a href="%s">%s</a>' % (url,  obj.name)

class CountPokemons:
    @admin.display()
    def number_of_pokemons(self, obj):
        return obj.number_of_pokemons

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        qs = qs.annotate(models.Count('pokemons'))
        return qs

    number_of_pokemons.admin_order_field = 'pokemons__count'

class PokemonModelAdmin(admin.ModelAdmin):
    list_display = ['pokeapi_id', 'name', 'base_experience', 'height', 'weight']
    fieldsets = [
        (None, {'fields':['pokeapi_id', 'name']}),
        ('Chars', {'fields':['base_experience', 'height', 'weight']}),
        ('Abilities',{'fields':['abilities']}),
        ('Images',{'fields':['image_big', 'image_small_front', 'image_small_back']})
    ]

    list_display_links = ['name']
    search_fields = ['name', 'pokeapi_id', 'name']
    filter_vertical = ['abilities',]

    class Meta:
         model = Pokemon

class AbilityModelAdmin(CountPokemons, admin.ModelAdmin):

    @admin.display(description='Name')
    def capitalize_name(self, obj):
        return str.capitalize(obj.name)

    list_display = ['pokeapi_id','capitalize_name', 'effect_entry_short', 'number_of_pokemons']
    list_display_links = ['capitalize_name']
    search_fields = ['effect_entry']



class TypePokemonModelAdmin(CountPokemons, admin.ModelAdmin):
    list_display = ['show_image', 'name', 'number_of_pokemons']

    @admin.display()
    def show_image(self, obj):
        return format_html(f'<img src="{obj.image.url}" height=50 />')
    show_image.short_description = 'Image'

    @admin.display()
    def get_pokemons(self, obj):
        url_to_edit_object(obj)
        print('sss')
        return format_html(", ".join([url_to_edit_object(p) for p in obj.pokemons.all()]))
    get_pokemons.short_description = 'Pokemons with this type:'

    readonly_fields = ['get_pokemons']

class SpeciesPokemonModelAdmin(CountPokemons, admin.ModelAdmin):
    list_display = ['name', 'number_of_pokemons']


admin.site.register(Pokemon, PokemonModelAdmin)
admin.site.register(Ability, AbilityModelAdmin)
admin.site.register(SpeciesPokemon, SpeciesPokemonModelAdmin)
admin.site.register(TypePokemon, TypePokemonModelAdmin)
