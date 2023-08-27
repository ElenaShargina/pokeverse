from django.contrib.auth.models import Group
from django.test import TestCase
from users.models import CustomUser
from django.contrib.auth import authenticate, login
from django.urls import reverse


class CustomUserTest(TestCase):
    # Данные для создания тестовых пользователей
    collectors_group_name = 'Collectors'
    users_dict = {
        'test_user_1': {'username': 'test_user_1',
                        'email': 'test_user_1@mail.ru',
                        'password': 'test_user_1_password'}

    }


    @classmethod
    def setUpTestData(cls):
        test_user_1 = CustomUser.objects.create_user(cls.users_dict['test_user_1']['username'],
                                       cls.users_dict['test_user_1']['email'],
                                       cls.users_dict['test_user_1']['password'],
                                       )
        collector_group,_ = Group.objects.get_or_create(name=cls.collectors_group_name)
        test_user_1.groups.add(collector_group)
        test_user_1.save()
        tu = CustomUser.objects.get(username='test_user_1')
        # print(tu.groups.values_list('name', flat=True))


    def testTopMenuAuthorized(self):
        login = self.client.login(  username=self.users_dict['test_user_1']['username'],
                                    password=self.users_dict['test_user_1']['password']
                                    )
        resp = self.client.get(reverse('main_index'))
        self.assertTemplateUsed(resp,'top_menu_user_authorized.html')

    def testTopMenuUnauthorized(self):
        resp = self.client.get(reverse('main_index'))
        self.assertTemplateUsed(resp,'top_menu_user_unauthorized.html')

    def testPokemonListBoxAuthorized(self):
        self.client.login(username=self.users_dict['test_user_1']['username'],
                                  password=self.users_dict['test_user_1']['password']
                                  )
        resp = self.client.get(reverse('pokemons_index'))
        self.assertTemplateUsed(resp, 'base_pokemon_square_add_box.html')