from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    # @todo вынести в settings
    collectors_group_name = 'Collectors'

    def is_collector(self):
        print('HERE')
        print(self.groups.values_list('name', flat=True))
        if self.groups.filter(name=self.collectors_group_name).exists():
            return True
        else:
            return False