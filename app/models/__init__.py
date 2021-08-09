from tortoise.fields import data, relational
from tortoise.models import Model


class TimestampMixin:
    created_at = data.DatetimeField(auto_now_add=True)
    modified_at = data.DatetimeField(auto_now=True)


class AbstractBaseModel(Model):
    id = data.UUIDField(pk=True, index=True)

    class Meta:
        abstract = True


class Summary(TimestampMixin, AbstractBaseModel):
    url = data.TextField()
    summary = data.TextField()
    user: relational.ForeignKeyRelation["User"] = relational.ForeignKeyField("models.User", related_name="summaries")

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return self.url


class User(TimestampMixin, AbstractBaseModel):
    username = data.CharField(max_length=255, unique=True, index=True)
    email = data.CharField(max_length=255, unique=True, index=True)
    full_name = data.TextField()
    is_active = data.BooleanField(default=True)
    is_superuser = data.BooleanField(default=False)
    hashed_password = data.TextField()

    summaries: relational.ReverseRelation[Summary]

    class Meta:
        ordering = ["username"]

    def __str__(self):
        return self.username
