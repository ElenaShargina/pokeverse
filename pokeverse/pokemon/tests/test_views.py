from django.test import TestCase

from pokemon.models import Pokemon, Ability, TypePokemon, SpeciesPokemon
from django.urls import reverse

class PokemonViewTest(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.num_of_pokemons_with_species_1 = 3
        sp1 = SpeciesPokemon.objects.create(name=f'sp{cls.num_of_pokemons_with_species_1}')
        sp2 = SpeciesPokemon.objects.create(name='spno')
        cls.number_of_pokemons = 63
        created_pokemons = []
        for pokemon_num in range(cls.number_of_pokemons):
            created_pokemons.append(Pokemon.objects.create(name=f'Pokemon #{pokemon_num}', pokeapi_id=pokemon_num))
        for i in range(cls.num_of_pokemons_with_species_1):
            created_pokemons[0+i].species = sp1
            created_pokemons[0+i].save()

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/pokemons/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('pokemons_index'))
        self.assertEqual(resp.status_code, 200)

    def test_view_uses_correct_template(self):
        resp = self.client.get(reverse('pokemons_index'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'pokemon/pokemon_list.html')

    def test_pagination_is_sixty(self):
        resp = self.client.get(reverse('pokemons_index'))
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue(len(resp.context['object_list']) == 60)

    def test_lists_all_pokemons(self):
        #Get second page and confirm it has (exactly) remaining 3 items
        resp = self.client.get(reverse('pokemons_index')+'?page=2')
        self.assertEqual(resp.status_code, 200)
        self.assertTrue('is_paginated' in resp.context)
        self.assertTrue(resp.context['is_paginated'] == True)
        self.assertTrue( len(resp.context['object_list']) == 3)

    def test_detail_species_related(self):
        resp = self.client.get(reverse('pokemons_detail',args=[1]))
        self.assertEqual(len(resp.context['pokemons']),self.num_of_pokemons_with_species_1-1)

    def test_detail_no_species_related(self):
        resp = self.client.get(reverse('pokemons_detail', args=[self.number_of_pokemons-2]))
        self.assertEqual(resp.context.get('pokemons', None),None)

    def test_detail_template_used(self):
        resp = self.client.get(reverse('pokemons_detail',args=[1]))
        self.assertTemplateUsed(resp, 'pokemon/pokemon_detail.html')

    def test_detail_no_pokemon_found(self):
        resp = self.client.get(reverse('pokemons_detail',args=[12300]))
        self.assertEqual(resp.status_code,404)

    def test_detail_pokemon_found(self):
        resp = self.client.get(reverse('pokemons_detail',args=[1]))
        self.assertEqual(resp.status_code,200)

class AbilityViewTest(TestCase):
    number_of_abilities = 10
    num_of_pokemons_with_ability_0 = 3
    num_of_pokemons_with_ability_1 = 4
    num_of_pokemons_with_no_abilities = 2

    @classmethod
    def setUpTestData(cls):
        created_abilities = []
        for ability_num in range(cls.number_of_abilities):
            created_abilities.append(Ability.objects.create(name=f'Ability #{ability_num}', pokeapi_id=ability_num))
        cls.ability_0_id = created_abilities[0].id
        cls.ability_1_id = created_abilities[1].id
        cls.ability_2_id = created_abilities[2].id
        for pokemon_num in range(cls.num_of_pokemons_with_ability_0):
            p = Pokemon.objects.create(name=f'Pokemon #{pokemon_num} with ability 0')
            p.abilities.add(created_abilities[0])
        for pokemon_num in range(cls.num_of_pokemons_with_ability_1):
            p = Pokemon.objects.create(name=f'Pokemon #{pokemon_num} with ability 1')
            p.abilities.add(created_abilities[1])
        for pokemon_num in range(cls.num_of_pokemons_with_no_abilities):
            Pokemon.objects.create(name=f'Pokemon #{pokemon_num} with no abilities')

    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/abilities/')
        self.assertEqual(resp.status_code, 200)

    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('abilities_index'))
        self.assertEqual(resp.status_code, 200)

    def test_view_list_uses_correct_template(self):
        resp = self.client.get(reverse('abilities_index'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'pokemon/ability_list.html')

    def test_view_detail_uses_correct_template(self):
        resp = self.client.get(reverse('abilities_detail',args=[self.ability_0_id]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'pokemon/ability_detail.html')

    def test_view_show_all_abilities(self):
        resp = self.client.get(reverse('abilities_index'))
        self.assertEqual(self.number_of_abilities, len(resp.context['object_list']))

    def test_view_ability_detail_no_found(self):
        resp = self.client.get(reverse('abilities_detail',args=[123]))
        self.assertIsNotNone(resp.context['exception'])

    def test_view_show_ability_with_pokemons(self):
        resp = self.client.get(reverse('abilities_detail',args=[self.ability_0_id]))
        self.assertEqual(self.num_of_pokemons_with_ability_0, len(resp.context['pokemons']))
        resp = self.client.get(reverse('abilities_detail', args=[self.ability_1_id]))
        self.assertEqual(self.num_of_pokemons_with_ability_1, len(resp.context['pokemons']))

    def test_view_show_ability_with_no_pokemons(self):
        resp = self.client.get(reverse('abilities_detail', args=[self.ability_2_id]))
        self.assertEqual(0, len(resp.context['pokemons']))

class TypePokemonViewTest(TestCase):
    number_of_types = 20
    num_of_pokemons_with_type_0 = 3
    num_of_pokemons_with_type_1 = 4
    num_of_pokemons_with_no_types = 2

    @classmethod
    def setUpTestData(cls):
        created_types = []
        for type_num in range(cls.number_of_types):
            created_types.append(TypePokemon.objects.create(name=f'Type #{type_num}'))
        cls.type_0_name = created_types[0].name
        cls.type_1_name = created_types[1].name
        cls.type_2_name = created_types[2].name
        for pokemon_num in range(cls.num_of_pokemons_with_type_0):
            p = Pokemon.objects.create(name=f'Pokemon #{pokemon_num} with type 0')
            p.types.add(created_types[0])
        for pokemon_num in range(cls.num_of_pokemons_with_type_1):
            p = Pokemon.objects.create(name=f'Pokemon #{pokemon_num} with ability 1')
            p.types.add(created_types[1])
        for pokemon_num in range(cls.num_of_pokemons_with_no_types):
            Pokemon.objects.create(name=f'Pokemon #{pokemon_num} with no types')


    def test_view_url_exists_at_desired_location(self):
        resp = self.client.get('/types/')
        self.assertEqual(resp.status_code, 200)


    def test_view_url_accessible_by_name(self):
        resp = self.client.get(reverse('types_index'))
        self.assertEqual(resp.status_code, 200)


    def test_view_list_uses_correct_template(self):
        resp = self.client.get(reverse('types_index'))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'pokemon/typepokemon_list.html')

    def test_view_detail_uses_correct_template(self):
        resp = self.client.get(reverse('types_detail', args=[self.type_1_name]))
        self.assertEqual(resp.status_code, 200)
        self.assertTemplateUsed(resp, 'pokemon/typepokemon_detail.html')


    def test_view_show_all_types(self):
        resp = self.client.get(reverse('types_index'))
        self.assertEqual(self.number_of_types, len(resp.context['object_list']))


    def test_view_type_detail_no_found(self):
        resp = self.client.get(reverse('types_detail', args=[123]))
        self.assertIsNotNone(resp.context['exception'])


    def test_view_show_type_with_pokemons(self):
        resp = self.client.get(reverse('types_detail', args=[self.type_0_name]))
        self.assertEqual(self.num_of_pokemons_with_type_0, len(resp.context['pokemons']))
        resp = self.client.get(reverse('types_detail', args=[self.type_1_name]))
        self.assertEqual(self.num_of_pokemons_with_type_1, len(resp.context['pokemons']))


    def test_view_show_type_with_no_pokemons(self):
        resp = self.client.get(reverse('types_detail', args=[self.type_2_name]))
        self.assertEqual(0, len(resp.context['pokemons']))