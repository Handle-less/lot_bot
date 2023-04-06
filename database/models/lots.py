import logging
import pytz
from datetime import timedelta, datetime

from configuration import config
from tortoise import fields, models


class Lot(models.Model):

    post_datetime: fields.DatetimeField = fields.DatetimeField()

    media_type: fields.TextField = fields.TextField(
        null=True
    )

    media: fields.TextField = fields.TextField(
        null=True
    )

    location: fields.TextField = fields.TextField()

    task: fields.TextField = fields.TextField()

    deadline: fields.TextField = fields.TextField()

    first_price: fields.IntField = fields.IntField()

    last_price: fields.IntField = fields.IntField(
        default=0
    )

    is_active = fields.BooleanField = fields.BooleanField(
        default=1
    )

    winner_id: fields.IntField = fields.IntField(
        default=-1
    )

    end_datetime = fields.DatetimeField = fields.DatetimeField(
        null=True
    )

    class Meta:
        table = 'lots'


async def update_lots():
    lots = await Lot.filter(is_active=0)
    for lot in lots:
        tz = pytz.timezone('Europe/Moscow')
        dt = lot.end_datetime + timedelta(hours=config["LOT_SAFE_HOURS"])
        dt_now = tz.localize(datetime.now())
        if dt < dt_now:
            await lot.delete()
    logging.info("UPDATED: lots")
