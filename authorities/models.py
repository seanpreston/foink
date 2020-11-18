from django.core.validators import validate_email
from django.db import models

from notes.models import BaseModel


class FOIRequest(BaseModel):

    text = models.CharField(
        max_length=4096,
        null=False,
    )
    sender = models.CharField(
        max_length=2048,
        null=False,
        validators=[validate_email]
    )
    recipient = models.CharField(
        max_length=2048,
        null=False,
        validators=[validate_email]
    )

    def __str__(self):
        return "FOI Request from {} to {}".format(self.sender, self.recipient)


class Authority(BaseModel):

    name = models.CharField(
        max_length=2048,
        null=False,
    )
    email = models.CharField(
        max_length=2048,
        null=False,
        validators=[validate_email]
    )
    category = models.CharField(
        max_length=2048,
        null=True,
    )

    def __str__(self):
        return self.name

    def get_serialized(self):
        return {
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'uuid': self.uuid,
            'name': self.name,
            'category': self.category,
            'id': self.id,
        }