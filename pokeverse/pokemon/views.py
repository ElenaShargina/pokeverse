import logging

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Pokemon, Ability, Collection, TypePokemon, SpeciesPokemon
from django.views import generic
from django.views.generic.edit import UpdateView
from django.db.models import Q


class MainIndex(generic.View):
    template_name = 'main.html'

    def get(self, request):
        return render(request, self.template_name, {})

class SearchResultsView(generic.ListView):
    model = Pokemon
    template_name = 'search_results.html'

    def get_queryset(self):  # new
        query = self.request.GET.get("q")
        pokemon_list = Pokemon.objects.filter(
            Q(name__icontains=query)
        )
        ability_list = Ability.objects.filter(
            Q(name__icontains=query)
        )
        types_list = TypePokemon.objects.filter(
            Q(name__icontains=query)
        )
        print(pokemon_list,ability_list,types_list)
        return {'query':query,'pokemon_list':pokemon_list, 'ability_list':ability_list,'types_list':types_list}

class PokemonIndexView(generic.ListView):
    model = Pokemon
    paginate_by = 60


class PokemonDetailView(generic.DetailView):
    model = Pokemon

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chars_dict'] = {
            'Имя': context['object'].name,
            'PokeApi ID': context['object'].pokeapi_id,
            'Вес': context['object'].weight,
            'Рост': context['object'].height,
            'Базовый опыт': context['object'].base_experience,
        }
        context['pokemons'] = context['object'].species.pokemons.exclude(pokeapi_id=context['object'].pokeapi_id)

        return context


class AbilityIndexView(generic.ListView):
    model = Ability


class AbilityDetailView(generic.DetailView):
    model = Ability

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chars_dict'] = {
            'Название': context['object'].name,
            'PokeApi ID': context['object'].pokeapi_id,
            'Полное описание': context['object'].effect_entry,
        }
        context['pokemons'] = [{'id': x.id, 'name': x.name, 'image_big': x.image_big} for x in
                               context['object'].pokemon_set.all()]
        return context

class SpeciesPokemonIndexView(generic.ListView):
    model = SpeciesPokemon

class SpeciesPokemonDetailView(generic.DetailView):
    model = SpeciesPokemon

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chars_dict'] = {
            'Название': context['object'].name,
            'Текст': context['object'].text,
        }
        context['pokemons'] = [{'id': x.id, 'name': x.name, 'image_big': x.image_big} for x in
                               context['object'].pokemons.all()]
        return context

class TypePokemonIndexView(generic.ListView):
    model = TypePokemon

class TypePokemonDetailView(generic.DetailView):
    model = TypePokemon

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['pokemons'] = [{'id': x.id, 'name': x.name, 'image_big': x.image_big} for x in
                               context['object'].pokemon_set.all()]
        context['len_pokemons'] = str(len(context['pokemons']))
        return context


# https://docs.djangoproject.com/en/4.1/topics/forms/#using-a-form-in-a-view
# https://docs.djangoproject.com/en/4.1/topics/class-based-views/generic-editing/

class CollectionDetailView(generic.DetailView):
    model = Collection

    # slug_field = 'user_id'

    def get_object(self, queryset=None):
        return get_object_or_404(Collection, user_id=self.request.user.id)


# https://docs.djangoproject.com/en/4.1/topics/forms/modelforms/#django.forms.ModelForm
# https://docs.djangoproject.com/en/4.1/topics/forms/
# https://docs.djangoproject.com/en/4.1/topics/class-based-views/generic-editing/
class CollectionEditView(UpdateView):
    model = Collection
    fields = ['name', 'pokemons']

    # https://stackoverflow.com/questions/7778143/whats-easiest-way-to-use-filter-horizontal-outside-of-the-admin-in-django

    def get_object(self, queryset=None):
        return get_object_or_404(Collection, user_id=self.request.user.id)
