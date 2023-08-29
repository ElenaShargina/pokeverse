from django.contrib.auth.models import Group
from django.test import TestCase
from users.models import CustomUser
from pokemon.models import Pokemon
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.contrib import auth

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
        # @TODO вставить импорт тестовых покемонов
        p = Pokemon.objects.get_or_create(name='Pikachu')
        # print(tu.groups.values_list('name', flat=True))


    def testTopMenuAuthorized(self):
        """
проверка, что авторизованным пользователям показывается соответствующий вид верхнего меню
        """
        login = self.client.login(  username=self.users_dict['test_user_1']['username'],
                                    password=self.users_dict['test_user_1']['password']
                                    )
        resp = self.client.get(reverse('main_index'))
        self.assertTemplateUsed(resp,'top_menu_user_authorized.html')

    def testTopMenuUnauthorized(self):
        """
проверка, что неавторизованным пользователям показывается соответствующий вид верхнего меню
        """
        resp = self.client.get(reverse('main_index'))
        self.assertTemplateUsed(resp,'top_menu_user_unauthorized.html')

    def testCollectionMenuItemAuthorized(self):
        """
проверка, что авторизованным пользователям показывается пункт верхнего меню "Коллекция"
        """
        login = self.client.login(username=self.users_dict['test_user_1']['username'],
                                  password=self.users_dict['test_user_1']['password']
                                  )
        resp = self.client.get(reverse('main_index'))
        self.assertTemplateUsed(resp, 'base_top_menu_collection_item.html')

    def testCollectionMenuItemUnauthorized(self):
        """
проверка, что неавторизованным пользователям не показывается пункт верхнего меню "Коллекция"
        """
        resp = self.client.get(reverse('main_index'))
        self.assertTemplateNotUsed(resp, 'base_top_menu_collection_item.html')

    def testPokemonListBoxAuthorized(self):
        """
проверка, что авторизованным пользователям показывается всплывающий блок действий в списке покемонов
        """
        self.client.login(username=self.users_dict['test_user_1']['username'],
                                  password=self.users_dict['test_user_1']['password']
                                  )
        resp = self.client.get(reverse('pokemons_index'))
        self.assertTemplateUsed(resp, 'base_pokemon_square_add_box.html')

    def testPokemonListBoxUnAuthorized(self):
        """
проверка, что неавторизованным пользователям не показывается всплывающий блок действий в списке покемонов
                """
        resp = self.client.get(reverse('pokemons_index'))
        self.assertTemplateNotUsed(resp, 'base_pokemon_square_add_box.html')

    def testCollectionPageUnauthorizedUser(self):
        """
проверка, что неавторизованным пользователям  не показывается страница коллекции
(переадресация на страницу логина с дальнейшим переходом обратно на страницу коллекции)
        """
        resp = self.client.get(reverse('collection_detail'))
        expected_redirection = reverse('users:login')+'?next='+reverse('collection_detail')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, expected_redirection)

    def testCollectionPageAuthorizedUser(self):
        """
проверка, что авторизованным пользователям  показывается страница коллекции
        """
        self.client.login(username=self.users_dict['test_user_1']['username'],
                          password=self.users_dict['test_user_1']['password']
                          )
        resp = self.client.get(reverse('collection_detail'))
        self.assertEqual(resp.status_code,200)

    def testLogout(self):
        """
проверка, что авторизованныe пользователи
        1) переходят на первую страницу при переходе на users:logout
        2) оказываются разлогинированными
        """
        # логинимся как пользователь
        self.client.login(username=self.users_dict['test_user_1']['username'],
                          password=self.users_dict['test_user_1']['password']
                          )
        # проверяем, что пользователь залогинен
        self.assertEqual(auth.get_user(self.client).is_authenticated, True)
        # переходим на главную страницу
        resp = self.client.get(reverse('main_index'))
        # переходим по ссылке разлогирования
        resp = self.client.get(reverse('users:logout'))
        # проверяем, что перенаправлены
        self.assertEqual(resp.status_code, 302)
        # проверяем, что пользователь больше не авторизован
        self.assertEqual(auth.get_user(self.client).is_authenticated,False)
