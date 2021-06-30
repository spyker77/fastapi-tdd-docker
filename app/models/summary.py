from tortoise.fields import data
from tortoise.models import Model


class TextSummary(Model):
    id = data.IntField(pk=True)
    url = data.TextField()
    summary = data.TextField()
    created_at = data.DatetimeField(auto_now_add=True)

    def __str__(self):
        return self.url
