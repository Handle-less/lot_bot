from tortoise import fields, models


class Report(models.Model):

    tg_id: fields.BigIntField = fields.BigIntField()

    tg_username: fields.TextField = fields.TextField()

    send_datetime: fields.DateField = fields.DateField()

    text: fields.TextField = fields.TextField()

    class Meta:
        table = 'reports'
