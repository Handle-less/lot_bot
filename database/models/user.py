from tortoise import fields, models


class User(models.Model):

    tg_id: fields.BigIntField = fields.BigIntField(
        null=False,
        unique=True
    )

    tg_username: fields.TextField = fields.TextField()

    balance: fields.IntField = fields.IntField(
        default=0
    )

    full_name: fields.TextField = fields.TextField()

    phone: fields.TextField = fields.TextField()

    verification: fields.SmallIntField = fields.SmallIntField(
        default=0
    )

    reg_date: fields.DateField = fields.DateField()

    is_banned: fields.BooleanField = fields.BigIntField(
        default=False
    )

    class Meta:
        table = 'users'
