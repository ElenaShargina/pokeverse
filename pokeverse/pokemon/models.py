from django.db import models
from django.conf import settings
from django.contrib import admin
from django.core.exceptions import ObjectDoesNotExist
from django.core.files import File

import requests
import os
import logging


# TODO добавить slug к покемонам и способностям

class Ability(models.Model):
    pokeapi_id = models.IntegerField()
    name = models.CharField(max_length=100)
    effect_entry = models.CharField(max_length=500)
    effect_entry_short = models.CharField(max_length=500)

    def __str__(self):
        return str.capitalize(self.name) + f' ({self.pokeapi_id})'

    @property
    def number_of_users(self):
        return len(self.pokemon_set.all())


class TypePokemon(models.Model):
    name = models.CharField(primary_key=True, max_length=100, null=False)
    image = models.ImageField(upload_to='type_image/', null=True, blank=True)

class SpeciesPokemon(models.Model):
    name = models.CharField(primary_key=True, max_length=100, null=False)
    text = models.CharField(max_length=2000)

class Pokemon(models.Model):
    from django.core.validators import MinValueValidator

    pokeapi_id = models.IntegerField(default=0)
    name = models.CharField(max_length=100)
    base_experience = models.IntegerField(default=0, null=True)
    height = models.IntegerField(default=0, null=True)
    weight = models.IntegerField(default=0, validators=[MinValueValidator(1)], null=True)
    abilities = models.ManyToManyField(Ability)
    types = models.ManyToManyField(TypePokemon)
    species = models.ForeignKey(SpeciesPokemon, models.SET_NULL, blank=True, null=True, related_name='pokemons')

    image_big = models.ImageField(upload_to='pokemon_images_big/', null=True, blank=True)
    image_small_front = models.ImageField(upload_to='pokemon_images_small_front/', null=True, blank=True)
    image_small_back = models.ImageField(upload_to='pokemon_images_small_back/', null=True, blank=True)

    def delete(self, *args, **kwargs):
        if self.image_big != None:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.image_big.name))
        if self.image_small_front != None:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.image_small_front.name))
        if self.image_small_back != None:
            os.remove(os.path.join(settings.MEDIA_ROOT, self.image_small_back.name))
        super().delete(*args, **kwargs)

    def add_images(self, images_dir, url_prefix_pokemon):
        """
        Добавляет картинки к покемону.
        Картинки сначала ищутся в указанной предзагруженной папке, если там нет - загружаются с указанного сайта.
        """

        def add_image(field_name: str, source_file_postfix: str, target_file_postfix: str) -> bool:
            """
            Добавляет картинку в соответствующее поля покемона
            :param field_name: название поля
            :param source_file_postfix: постфикс файла из семпловой папки image_dir
            :param target_file_postfix: постфикс файла, как он будет сохранен в системе
            :return True, если файл с картинкой был найден, False иначе
            """
            sf = os.path.join(settings.MEDIA_ROOT, images_dir, str(self.pokeapi_id) + source_file_postfix)
            try:
                f = open(file=sf, mode='rb')
                setattr(self, field_name, File(f, name=str(self.pokeapi_id) + target_file_postfix))
                self.save()
                f.close()
                return True
            except Exception as exc:
                logging.info(f'No file for {sf} \n {exc}')
                return False

        def add_image_big_from_pokeapi(source_file_postfix: str, target_file_postfix: str):
            """
            Добавляет картинку в поле image_big , загружая его из pokeapi
            :param source_file_postfix: постфикс файла для сохранения в папке images_dir (чтобы использовать потом)
            :param target_file_postfix: постфикс файла для сохранения в системе
            """
            url = f'{url_prefix_pokemon}{self.pokeapi_id}/'
            result = requests.get(url).json()
            new_image = None
            # пытаемся добыть картинки из Pokeapi, пути выведены методом проб и ошибок
            possible_images = [result['sprites']['other']['home']['front_default'],
                               result['sprites']['other']['official-artwork']['front_default'],
                               result['sprites']['front_default']
                               ]
            for i in possible_images:
                if i:
                    new_image = requests.get(i).content
                    break

            # если картинка была найдена, используем её
            if new_image:
                # сохраняем картинку в папке sample
                sf = os.path.join(settings.MEDIA_ROOT, images_dir, str(self.pokeapi_id) + source_file_postfix)
                try:
                    f = open(file=sf, mode='wb')
                    f.write(new_image)
                    f.close()
                except Exception as exc:
                    logging.info(f'Can not open file {sf} for saving new image {exc}')
                # добавляем эту картинку в поле текущего покемона
                try:
                    f = open(file=sf, mode='rb')
                    self.image_big = File(f, name=str(self.pokeapi_id) + target_file_postfix)
                    self.save()
                    f.close()
                except Exception as exc:
                    logging.info(f'Can not open file {sf} for adding new image to Pokemon object {exc}')

        # словарь с постфиксами файлов соответствующих свойств.
        # Первый - постфикс названия файла в предзагруженной папке image_dir.
        # Второй - постфикс названия файла для сохранения в поле объекта (в папке MEDIA_ROOT).

        images_postfixes = {
            'image_big': ('-home-front_default.png', '-image-big.png'),
            'image_small_front': ('-front_default.png', '-image-small-front.png'),
            'image_small_back': ('-back_default.png', '-image-small-back.png')
        }
        # Сначала пытаемся добавить картинки из предзагруженной папки images_dir
        for field_name, postfixes in images_postfixes.items():
            logging.info(f'Добавляем {field_name} для {self.pokeapi_id}')
            add_image(field_name, postfixes[0], postfixes[1])

        # обновляем текущий объект
        self.refresh_from_db(fields=['image_big'])

        # если поле image_big осталось пустым, попробуем загрузить его из сети
        if not self.image_big:
            add_image_big_from_pokeapi(images_postfixes['image_big'][0], images_postfixes['image_big'][1])


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


class Import:
    """
    Класс для импорта покемонов и способностей с pokeapi.
    Использование через shell:

    python pokeverse.manage.py shell
    from pokemon.models import Import
    Import.import_all()

    """
    url_prefix_pokemon = 'https://pokeapi.co/api/v2/pokemon/'
    url_prefix_ability = 'https://pokeapi.co/api/v2/ability/'
    url_prefix_species = 'https://pokeapi.co/api/v2/pokemon-species/'
    sample_dir = 'sample'
    sample_sprites_dir = 'sample/sprites/'
    sample_types_dir = 'sample/types/'

    @classmethod
    def delete_all(cls):
        """
        Удаляет все записи о покемонах и их способностях. Удаляет картинки.
        """
        all_pokemons = Pokemon.objects.all()
        for p in all_pokemons:
            # @todo вставить удаление картинок
            p.delete()
        all_abilities = Ability.objects.all()
        for a in all_abilities:
            a.delete()

    @classmethod
    def _import_pokemons_from_urls(cls, urls: list) -> None:
        """
        Импортируем покемонов из PokeApi по данному списку urls, сохраняем их в БД
        :param urls: список адресов для импорта
        :type urls: list
        :return: None
        """
        for url in urls:
            logging.info(f'Импортируем из {url}')
            # запрашиваем информацию у сервиса
            result = requests.get(url).json()
            # обозначаем поля, которые будем сохранять у себя
            fields = ('name', 'base_experience', 'height', 'weight')
            defaults = {field: result[field] for field in fields}
            # проверяем на существование или создаем заново объект с данным id
            p = Pokemon.objects.get_or_create(
                pokeapi_id=result['id'],
                defaults=defaults
            )
            logging.info(f'Создано: {p[0].id} : {p[0].name}')

    @classmethod
    def _add_images_to_all_pokemons(cls):
        """
        Прикрепляет картинки ко всем покемонам.
        Для экономии времени картинки берутся из папки с заранее скаченными картинками.
        """
        all_pokemons = Pokemon.objects.all()
        for p in all_pokemons:
            p.add_images(cls.sample_sprites_dir, cls.url_prefix_pokemon)

    @classmethod
    def _import_ability_from_pokeapi(cls, name: str) -> None:
        """
        Импортирует способность из PokeApi, находя её по имени.
        :param name: str
        """

        def json_to_dict(json_string: dict) -> dict:
            """
            Преобразует json, присылаемый pokeapi, в словарь с ключами, соответствующими полям модели Ability
            :param json_string:
            :return: словарь с ключами id, name, effect_entry, effect_entry_short (in English)
            """
            new_ability = {
                'id': json_string['id'],
                'name': json_string['name']
            }
            # если есть effect_entries
            if 'effect_entries' in json_string.keys() and not len(json_string['effect_entries']) == 0:
                for lang in json_string['effect_entries']:
                    if lang['language']['name'] == 'en':
                        new_ability['effect_entry'] = lang['effect']
                        new_ability['effect_entry_short'] = lang['short_effect']
            # запасной вариант - flavour_text_entries
            elif 'flavor_text_entries' in json_string.keys() and not len(json_string['flavor_text_entries']) == 0:
                for lang in json_string['flavor_text_entries']:
                    logging.info(lang)
                    if lang['language']['name'] == 'en':
                        new_ability['effect_entry'] = lang['flavor_text']
                        new_ability['effect_entry_short'] = lang['flavor_text']
            # если ничего не найдено
            else:
                new_ability['effect_entry'] = 'No text found'
                new_ability['effect_entry_short'] = 'No text found'
            return new_ability

        url = f'{cls.url_prefix_ability}{name}/'
        try:
            result = requests.get(url).json()
            new_ability = json_to_dict(result)
            a = Ability.objects.get_or_create(
                pokeapi_id=new_ability['id'],
                defaults={
                    'name': new_ability['name'],
                    'effect_entry': new_ability['effect_entry'],
                    'effect_entry_short': new_ability['effect_entry_short']
                }
            )
            return a[0]
        except Exception as exc:
            logging.exception(f'На pokeapi не найдена способность {name}')
            return None

    @classmethod
    def _add_abilities(cls, pokemon: Pokemon) -> None:
        """
        добавляет способности к покемону
        :param pokemon:
        :type pokemon: Pokemon
        """
        url = f'{cls.url_prefix_pokemon}{pokemon.pokeapi_id}/'
        res = requests.get(url).json()
        for a in res['abilities']:
            ability_to_add = None
            try:
                logging.info(f"Обрабатываем способность {a['ability']['name']}")
                ability_to_add = Ability.objects.get(name=a['ability']['name'])
            except ObjectDoesNotExist:
                logging.info('Способность не найдена, импортируем из pokeapi.')
                ability_to_add = cls._import_ability_from_pokeapi(a['ability']['name'])
                logging.info(f"Способность импортирована.")
            if ability_to_add: pokemon.abilities.add(ability_to_add)

    @classmethod
    def _add_abilities_to_all_pokemons(cls):
        """
        Добавляет способности ко всем покемонам
        """
        all_pokemons = Pokemon.objects.all()
        for p in all_pokemons:
            cls._add_abilities(p)

    @classmethod
    def _add_types(cls, pokemon: Pokemon) -> None:
        """
        добавляет типы к покемону
        :param pokemon:
        :type pokemon: Pokemon
        """
        url = f'{cls.url_prefix_pokemon}{pokemon.pokeapi_id}/'
        result = requests.get(url).json()
        types = [i['type']['name'] for i in result['types']]
        types_to_add = []
        for t in types:
            type_to_add = TypePokemon.objects.get_or_create(name=t)[0]
            types_to_add.append(type_to_add)
        pokemon.types.set(types_to_add)
        pokemon.save()
        logging.info(f'Added {type_to_add} to pokemon {pokemon.name}')

    @classmethod
    def _add_types_to_all_pokemons(cls):
        """
        Добавляет типы ко всем покемонам
        """
        all_pokemons = Pokemon.objects.all()
        for p in all_pokemons:
            cls._add_types(p)

    @classmethod
    def _delete_pokemons_without_image(cls):
        """
        Удаляет покемонов без картинок
        """
        Pokemon.objects.filter(image_big='').delete()

    @classmethod
    def _add_images_to_all_types(cls):
        """
        Добавляет картинки ко всем типам покемонов, берет их из предзагруженной папки sample_types_dir
        """
        types = TypePokemon.objects.all()
        for t in types:
            image_file = os.path.join(settings.MEDIA_ROOT, cls.sample_types_dir, t.name.lower() + '.png')
            try:
                f = open(image_file, mode='rb')
                t.image = File(f, name=t.name.lower()+'.png')
                t.save()
                f.close()
                logging.info(f'Added image for {t.name}.')
            except:
                logging.info(f'No image file for {t.name} is found at {image_file}')

    @classmethod
    def _import_all_species(cls):
        """
        Имрортирует все виды покемонов с сайта. Добавляет эти виды в соответствующее поле имеющихся покемонов.
        """
        def _import_species_from_url(url):
            """
            Импортирует вид покемона из заданного адреса.
            :type url: str
            """
            result = requests.get(url).json()
            description = ''
            # ищем описание вида покемонов на английском языке
            for lang in result['form_descriptions']:
                if lang['language']['name'] == 'en':
                    description = lang['description']
            new_species = SpeciesPokemon(name=result['name'], text=description)
            new_species.save()
            # добавляем вид покемонов в соответствующее поле этих покемонов
            for v in result['varieties']:
                try:
                    p = Pokemon.objects.get(name=v['pokemon']['name'])
                    p.species = new_species
                    p.save()
                    logging.info(f'Added species {new_species.name} to Pokemon {p.name}')
                except ObjectDoesNotExist:
                    logging.warning(f'Cant find object of Pokemon {v["pokemon"]["name"]} for species {new_species.name}')

        logging.basicConfig(handlers=(logging.StreamHandler(),), level=logging.INFO)
        res = requests.get(cls.url_prefix_species + '?limit=1000&offset=0').json()
        logging.info(f"Начинаем импорт. В сети найдено видов покемонов: {len(res['results'])}")
        for s in res['results']:
            _import_species_from_url(s['url'])


    @classmethod
    def import_all(cls):
        """
        Импортирует из сети всех покемонов с их способностями, картинками и типами
        """
        logging.basicConfig(handlers=(logging.StreamHandler(),), level=logging.INFO)
        # получаем список всех покемонов
        res = requests.get(cls.url_prefix_pokemon + '?limit=100000&offset=0').json()
        logging.info(f"Начинаем импорт. В сети найдено покемонов: {len(res['results'])}")
        # импортируем всех покемонов из этого списка по сети
        cls._import_pokemons_from_urls([i['url'] for i in res['results']])
        # добавляем картинки к покемонам (для экономии времени берутся из семпловой папки sprites)
        cls._add_images_to_all_pokemons()
        # удаляем покемонов, для которых так и не нашлось картинки
        cls._delete_pokemons_without_image()
        # добавляем способности к покемонам
        cls._add_abilities_to_all_pokemons()
        # добавляем типы ко всем покемонам
        cls._add_types_to_all_pokemons()
        # добавляем картинки ко всем типам покемонов
        cls._add_types_to_all_pokemons()
