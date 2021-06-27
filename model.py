from tortoise import fields
from tortoise.models import Model


class PollData(Model):
    id = fields.TextField(pk=True)
    data = fields.TextField()
