from django.shortcuts import render
from django.views import generic
from .models import CustomUser
class CustomUserProfileView(generic.TemplateView):
    model = CustomUser

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # current_user = CustomUser.objects.get_by_natural_key(self.request.user)
        context['current_user'] = {'username':self.request.user.username, 'email':self.request.user.email}
        return context