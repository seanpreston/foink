from django.core.exceptions import ValidationError
from django.conf import settings
from django.db import models
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _

from accounts.utils import generate_uuid


class BaseModel(models.Model):
    created_at = models.DateTimeField(default=now, null=True)
    modified_at = models.DateTimeField(auto_now=True, null=True)
    uuid = models.CharField(
        max_length=255,
        blank=False,
        null=False,
        default=generate_uuid,
        unique=True,
    )

    class Meta:
        abstract = True


def validate_rating(value):
    if value < 0 or value > 5:
        raise ValidationError(
            _('%(value)s must be between 1 and 5'),
            params={'value': value},
        )


class Note(BaseModel):

    text = models.CharField(max_length=2048)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        related_name='notes',
        on_delete=models.CASCADE,
    )
    # The rating of the note between 0 and 5
    # 0 == no rating
    # 1 == worst rating
    # 5 == best rating
    rating = models.IntegerField(
        default=0,
        null=True,
        blank=True,
        validators=[validate_rating]
    )

    def get_serialized(self):
        return {
            'created_at': self.created_at,
            'modified_at': self.modified_at,
            'uuid': self.uuid,
            'text': self.text,
            'rating': self.rating,
        }
