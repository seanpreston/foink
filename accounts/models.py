from django.contrib.auth.models import AbstractUser
from notes.models import BaseModel


class User(AbstractUser, BaseModel):

    def get_serialized(self):
        return {
            'uuid': self.uuid,
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'id': self.id,
            'email': self.email,
        }
