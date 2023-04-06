from tortoise import fields, models


class LotCache(models.Model):

    lot_id: fields.IntField = fields.IntField()

    tg_id: fields.BigIntField = fields.BigIntField()

    price: fields.IntField = fields.IntField()

    class Meta:
        table = 'lots_cache'
