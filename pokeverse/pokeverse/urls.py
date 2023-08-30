"""pokeverse URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from pokemon import views
from django.conf.urls.static import static
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView, PasswordResetCompleteView, PasswordResetDoneView


urlpatterns = [
    path('admin/', admin.site.urls),
    # index page
    path('', views.MainIndex.as_view(), name='main_index'),
    # ex: /search/
    path('search/', views.SearchResultsView.as_view(), name='search_results'),
    # ex: /pokemons/
    path('pokemons/', views.PokemonIndexView.as_view(), name='pokemons_index'),
    # ex: /pokemons/123/
    path('pokemons/<int:pk>/', views.PokemonDetailView.as_view(), name='pokemons_detail'),
    # ex: /types/
    path('types/', views.TypePokemonIndexView.as_view(), name='types_index'),
    # ex: /types/fire/
    path('types/<str:pk>/', views.TypePokemonDetailView.as_view(), name='types_detail'),
    # ex: /abilities/
    path('abilities/', views.AbilityIndexView.as_view(), name='abilities_index'),
    # ex: /abilities/123
    path('abilities/<int:pk>/', views.AbilityDetailView.as_view(), name='abilities_detail'),
    # ex: /species/
    path('species/', views.SpeciesPokemonIndexView.as_view(), name='species_index'),
    # ex: /species/bulbasaur/
    path('species/<str:pk>/', views.SpeciesPokemonDetailView.as_view(), name='species_detail'),
    # authorizing for users
    # path("users/", include("django.contrib.auth.urls")),
    path("users/", include("users.urls")),
    # ex: /collection
    path('collection/', views.CollectionDetailView.as_view(), name='collection_detail'),
    # ex: /collection/edit
    path('collection/edit', views.CollectionEditView.as_view(), name = 'collection_edit'),

    # для использования штатных представлений джанго, импортируем эти пути в корневое пространство имён
    path('password-reset/', PasswordResetView.as_view(template_name='users/reset_password.html'),name='password_reset'),
    path('password-reset/done/', PasswordResetDoneView.as_view(template_name='users/reset_password.html'),name='password_reset_done'),
    path('password-reset-confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(template_name='users/reset_password.html'),name='password_reset_confirm'),
    path('password-reset-complete/',PasswordResetCompleteView.as_view(template_name='users/reset_password.html'),name='password_reset_complete'),

]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
