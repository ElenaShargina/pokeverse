from django.shortcuts import redirect
from django.views import generic
from .models import CustomUser, Collection
from .forms import CustomUserCreationForm, CustomUserChangePasswordForm, CustomUserResetPasswordForm
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth import login, update_session_auth_hash
from django.views.generic.edit import UpdateView
from django.shortcuts import get_object_or_404


class CustomUserProfileView(LoginRequiredMixin, generic.TemplateView):
    model = CustomUser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # current_user = CustomUser.objects.get_by_natural_key(self.request.user)
        context['current_user'] = {'username': self.request.user.username, 'email': self.request.user.email}
        return context


class CustomUserRegisterView(generic.FormView):
    form_class = CustomUserCreationForm
    success_url = reverse_lazy('users:profile')
    template_name = 'users/register.html'

    # форма показывается только НЕ авторизованным пользователям, остальные отправляются на главную страницу
    def dispatch(self, request, *args, **kwargs):
        if self.request.user.is_authenticated:
            return redirect('main_index')
        else:
            return super(CustomUserRegisterView, self).dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        user = form.save()
        login(self.request, user)
        return redirect(self.success_url)


class CustomUserChangePasswordView(generic.FormView):
    form_class = CustomUserChangePasswordForm
    template_name = 'users/change_password.html'
    model = CustomUser
    success_url = reverse_lazy('users:profile')

    def get_form_kwargs(self):
        kwargs = super(CustomUserChangePasswordView, self).get_form_kwargs()
        self.form_class.base_fields['old_password'].label = 'Старый пароль'
        self.form_class.base_fields['new_password1'].label = 'Новый пароль'
        self.form_class.base_fields['new_password2'].label = 'Повтор нового пароля'

        kwargs['user'] = self.request.user
        if self.request.method == 'POST':
            kwargs['data'] = self.request.POST
        return kwargs

    def form_valid(self, form):
        form.save()
        update_session_auth_hash(self.request, form.user)
        return super(CustomUserChangePasswordView, self).form_valid(form)

# https://docs.djangoproject.com/en/4.1/topics/forms/#using-a-form-in-a-view
# https://docs.djangoproject.com/en/4.1/topics/class-based-views/generic-editing/

class CollectionDetailView(LoginRequiredMixin, generic.DetailView):
    model = Collection

    def get_object(self, queryset=None):
        return None


# https://docs.djangoproject.com/en/4.1/topics/forms/modelforms/#django.forms.ModelForm
# https://docs.djangoproject.com/en/4.1/topics/forms/
# https://docs.djangoproject.com/en/4.1/topics/class-based-views/generic-editing/
class CollectionEditView(UpdateView):
    model = Collection
    fields = ['name', 'pokemons']

    # https://stackoverflow.com/questions/7778143/whats-easiest-way-to-use-filter-horizontal-outside-of-the-admin-in-django

    def get_object(self, queryset=None):
        return get_object_or_404(Collection, user_id=self.request.user.id)