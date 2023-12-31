from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import CustomUser, Collection
from pokemon.admin import CountPokemons

@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ['email', 'username',]

@admin.register(Collection)
class CollectionAdmin(CountPokemons, admin.ModelAdmin):
    model = Collection
    list_display = ['user_id', 'name', 'number_of_pokemons']