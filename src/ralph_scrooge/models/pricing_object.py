# -*- coding: utf-8 -*-

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from django.db import models as db
from django.utils.translation import ugettext_lazy as _
from lck.django.common.models import (
    EditorTrackable,
    Named,
    TimeTrackable,
)

from lck.django.choices import Choices


PRICE_DIGITS = 16
PRICE_PLACES = 6


class PricingObjectType(Choices):
    _ = Choices.Choice
    asset = _("Asset")
    virtual = _("Virtual")
    tenant = _("OpenStack Tenant")
    ip_address = _("IP Address")


class PricingObject(TimeTrackable, EditorTrackable, Named):
    type = db.PositiveIntegerField(
        verbose_name=_("type"), choices=PricingObjectType(),
    )
    remarks = db.TextField(
        verbose_name=_("Remarks"),
        help_text=_("Additional information."),
        blank=True,
        default="",
    )
    service = db.ForeignKey(
        'Service',
        related_name='pricing_objects'
    )

    class Meta:
        app_label = 'ralph_scrooge'


class DailyPricingObject(db.Model):
    date = db.DateField(null=False, blank=False)
    pricing_object = db.ForeignKey(PricingObject, null=False, blank=False)
    service = db.ForeignKey('Service', related_name='daily_pricing_objects')

    class Meta:
        app_label = 'ralph_scrooge'


class AssetInfo(db.Model):
    pricing_object = db.OneToOneField(
        PricingObject,
        related_name='asset',
    )
    sn = db.CharField(max_length=200, null=True, blank=True, unique=True)
    barcode = db.CharField(max_length=200, null=True, blank=True, unique=True)
    device_id = db.IntegerField(
        verbose_name=_("device id"),
        unique=True,
        null=True,
        blank=True,
        default=None,
    )
    asset_id = db.IntegerField(
        verbose_name=_("asset id"),
        unique=True,
        null=False,
        blank=False,
    )

    class Meta:
        app_label = 'ralph_scrooge'


class DailyAssetInfo(db.Model):
    daily_pricing_object = db.OneToOneField(
        DailyPricingObject,
        related_name='daily_asset'
    )
    asset_info = db.ForeignKey(
        AssetInfo,
    )
    depreciation_rate = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("Depreciation rate"),
        default=0,
    )
    is_depreciated = db.BooleanField(
        default=False,
        verbose_name=_("Is depreciated"),
    )
    daily_cost = db.DecimalField(
        max_digits=PRICE_DIGITS,
        decimal_places=PRICE_PLACES,
        verbose_name=_("daily cost"),
        default=0,
    )

    class Meta:
        verbose_name = _("Daily Asset info")
        verbose_name_plural = _("Daily Assets info")
        app_label = 'ralph_scrooge'


class VirtualInfo(db.Model):
    pricing_object = db.OneToOneField(
        PricingObject,
        related_name='virtual',
    )
    device_id = db.IntegerField(unique=True, verbose_name=_("Ralph device ID"))

    class Meta:
        app_label = 'ralph_scrooge'


class DailyVirtualInfo(db.Model):
    daily_pricing_object = db.OneToOneField(
        DailyPricingObject,
        related_name='daily_virtual'
    )
    hypervisor = db.ForeignKey(DailyAssetInfo, related_name='daily_virtuals')

    class Meta:
        app_label = 'ralph_scrooge'
