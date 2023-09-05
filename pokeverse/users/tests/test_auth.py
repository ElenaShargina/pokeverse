import os

from django.contrib.auth.models import Group
from django.test import TestCase
from users.models import CustomUser
from pokemon.models import Pokemon, SpeciesPokemon, TypePokemon, Ability, Pokemon
from django.contrib.auth import authenticate, login
from django.urls import reverse
from django.contrib import auth
from django.core import serializers

class CustomUserTest(TestCase):
    # Данные для создания тестовых пользователей
    users_dict = {
        'test_user_1':  'test_user_1_password',
        'test_user_2':  'test_user_2_password'
    }

    def login_as_test_user(self, username):
        return self.client.login(username=username,
                          password=self.users_dict[username]
                          )


    @classmethod
    def setUpTestData(cls):
        def import_from_xml(filename):
            file_xml = open(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample/'+filename), 'r')
            for obj in serializers.deserialize("xml", file_xml):
                obj.save()

        # tus = CustomUser.objects.all()
        # print(tus)
        # file_xml = open(
        #     os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample/users.xml' ), 'w')
        # XMLSerializer = serializers.get_serializer("xml")
        # xml_serializer = XMLSerializer()
        # xml_serializer.serialize(queryset=tus, stream = file_xml)
        # file_xml.close()

        # загружаем тестовые данные из подготовленных файлов с сериализованными данными
        for f in ['speciespokemon.xml', 'typepokemon.xml', 'ability.xml', 'pokemon.xml', 'users.xml']:
            import_from_xml(f)

        # pokemons = Pokemon.objects.filter(types='grass')
        # print(len(pokemons))
        # pokemons = Pokemon.objects.filter(abilities='295')
        # print(pokemons)
        # pokemons = Pokemon.objects.filter(species='bulbasaur')
        # print(pokemons)

        # p = Pokemon.objects.get_or_create(name='Pikachu')
        # print(tu.groups.values_list('name', flat=True))


    def testTopMenuAuthorized(self):
        """
проверка, что авторизованным пользователям показывается соответствующий вид верхнего меню
        """
        login = self.login_as_test_user('test_user_1')
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
        login = self.login_as_test_user('test_user_1')
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
        login = self.login_as_test_user('test_user_1')
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
        resp = self.client.get(reverse('users:collection_detail'))
        expected_redirection = reverse('users:login')+'?next='+reverse('users:collection_detail')
        self.assertEqual(resp.status_code, 302)
        self.assertRedirects(resp, expected_redirection)

    def testCollectionPageAuthorizedUser(self):
        """
проверка, что авторизованным пользователям  показывается страница коллекции
        """
        login = self.login_as_test_user('test_user_1')
        resp = self.client.get(reverse('users:collection_detail'))
        self.assertEqual(resp.status_code,200)

    def testLogout(self):
        """
проверка, что авторизованныe пользователи
        1) переходят на первую страницу при переходе на users:logout
        2) оказываются разлогинированными
        """
        # логинимся как пользователь
        login = self.login_as_test_user('test_user_1')
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

    def testProfilePageUnathorizedUser(self):
        """
проверка, что неавторизованным пользователям не показывается страница профиля
        """
        resp = self.client.get(reverse('users:profile'))
        # проверяем, что перенаправлены
        self.assertEqual(resp.status_code, 302)
        expected_redirection = reverse('users:login') + '?next=' + reverse('users:profile')
        self.assertRedirects(resp, expected_redirection)

    def testRegisterNewUser(self):
        """
проверка регистрации нового пользователя - перенаправление и залоггированность нового пользователя
штатные функции джанго не проверяем
        """
        resp = self.client.get(reverse('users:register'))
        self.assertEqual(resp.status_code, 200)
        sample_data = {
            'username':'TestUser12345',
            'email':'testuser@gmail.com',
            'password1':'SamplePassword1233',
            'password2':'SamplePassword1233'
        }
        resp = self.client.post(reverse('users:register'), data=sample_data, follow=True)
        # проверяем, что произошло перенаправление
        self.assertRedirects(resp, reverse('users:profile'))
        # проверяем, что пользователь теперь залогинен
        self.assertEqual(auth.get_user(self.client).is_authenticated, True)

    def testRegisterPageNotSeenByAuthorizedUser(self):
        """
проверка, что авторизованным пользователям не показывается страница регистрации
        """
        # логинимся как пользователь
        login = self.login_as_test_user('test_user_1')
        resp = self.client.get(reverse('users:register'))
        # проверяем, что произошла переадресация на главную страницу
        self.assertEqual(resp.status_code, 302)
        expected_redirection = reverse('main_index')
        self.assertRedirects(resp, expected_redirection)

    def testChangePassword(self):
        """
проверка, что пользователь может сменить пароль. После успешной смены он переадресуется на страницу профиля
        """
        # логинимся как пользователь
        login = self.login_as_test_user('test_user_1')
        sample_data = {
            'old_password':self.users_dict['test_user_1'],
            'new_password1':'NewPassword123',
            'new_password2': 'NewPassword123',
        }
        resp = self.client.post(reverse('users:change_password'), data=sample_data, follow=True)
        self.assertRedirects(resp, reverse('users:profile'))

    def testCollectionEmpty(self):
        """
    проверка, что у пользователя с пустой коллекцией будет показана пустая коллекция
        """
        # логинимся как пользователь
        login = self.login_as_test_user('test_user_1')
        resp = self.client.get(reverse('users:collection_detail'))
        self.assertEqual(0, len(resp.context['object'].pokemons.values_list()))

    def testCollectionNotEmpty(self):
        """
    проверка, что у пользователя с НЕпустой коллекцией будет показана НЕпустая коллекция из заданного количества покемонов
        """
        # добавляем пользователю test_user_2 в коллекцию 3 покемонов
        tu = CustomUser.objects.get(username='test_user_2')
        pokemon_names = sorted(['bulbasaur', 'venusaur', 'oddish'])
        for p in pokemon_names:
            tu.add_pokemon(Pokemon.objects.get(name=p))

        # логинимся как пользователь
        login = self.login_as_test_user('test_user_2')
        resp = self.client.get(reverse('users:collection_detail'))
        self.assertEqual(3, len(resp.context['object'].pokemons.values_list()))
        self.assertEqual(list(resp.context['object'].pokemons.values_list("name",flat=True).order_by("name")), pokemon_names)