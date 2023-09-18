import logging

from django.shortcuts import render
from django.shortcuts import get_object_or_404
from .models import Pokemon, Ability, TypePokemon, SpeciesPokemon
from django.views import generic
from django.views.generic.edit import UpdateView
from django.db.models import Q
from django.contrib.auth.mixins import LoginRequiredMixin

class CollectionInfoMixin():
    def add_collection_info(self, context):
        # если пользователь залогинен, накладываем информацию про его коллекцию
        user = self.request.user
        if user.is_authenticated and context.get('object_list', None):
            user_collection = user.get_or_create_collection()[0].pokemons.all()
            object_list_ids = []
            if type(context['object_list'][0]) == Pokemon:
                object_list_ids = [p.id for p in context['object_list']]
            elif type(context['object_list'][0]) == dict:
                object_list_ids = [p['id'] for p in context['object_list']]
            context['in_collection'] = {key: False for key in object_list_ids}
            for p in object_list_ids:
                if user_collection.filter(id = p):
                    context['in_collection'][p] = True

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
        return {'query':query,'pokemon_list':pokemon_list, 'ability_list':ability_list,'types_list':types_list}

class PokemonIndexView(generic.ListView, CollectionInfoMixin):
    model = Pokemon
    paginate_by = 60
    ordering = ['name']
    
    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(object_list=object_list, **kwargs)
        self.add_collection_info(context)
        return context

class PokemonDetailView(generic.DetailView, CollectionInfoMixin):
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
        if context['object'].species!=None:
            context['object_list'] = context['object'].species.pokemons.all()
            self.add_collection_info(context)
            context['object_list'] = context['object_list'].exclude(pokeapi_id=context['object'].pokeapi_id)
        return context


class AbilityIndexView(generic.ListView):
    model = Ability


class AbilityDetailView(generic.DetailView, CollectionInfoMixin):
    model = Ability

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chars_dict'] = {
            'Название': context['object'].name,
            'PokeApi ID': context['object'].pokeapi_id,
            'Полное описание': context['object'].effect_entry,
        }
        context['object_list'] = [{'id': x.id, 'name': x.name, 'image_big': x.image_big} for x in
                               context['object'].pokemons.all()]
        self.add_collection_info(context)
        return context

class SpeciesPokemonIndexView(generic.ListView):
    model = SpeciesPokemon

class SpeciesPokemonDetailView(generic.DetailView, CollectionInfoMixin):
    model = SpeciesPokemon

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['chars_dict'] = {
            'Название': context['object'].name,
            'Текст': context['object'].text,
        }
        context['object_list'] = [{'id': x.id, 'name': x.name, 'image_big': x.image_big} for x in
                               context['object'].pokemons.all()]
        self.add_collection_info(context)
        return context

class TypePokemonIndexView(generic.ListView):
    model = TypePokemon

class TypePokemonDetailView(generic.DetailView, CollectionInfoMixin):
    model = TypePokemon

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_list'] = [{'id': x.id, 'name': x.name, 'image_big': x.image_big} for x in
                               context['object'].pokemons.all()]
        context['len_pokemons'] = str(len(context['object_list']))
        self.add_collection_info(context)
        return context
