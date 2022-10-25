import logging

from odoo import models, fields
from odoo.addons.generic_mixin import pre_create, pre_write

_logger = logging.getLogger(__name__)


class MarketingCostMixin(models.AbstractModel):
    _name = 'kw.marketing.cost.mixin'
    _inherit = ['generic.mixin.track.changes', ]
    _description = 'Marketing Cost mixin'

    kw_utm_str = fields.Char(
        index=True, )

    @pre_create()
    @pre_write('campaign_id', 'source_id', 'medium_id', )
    def pre_write_utm(self, changes):
        f_list = ['medium_id', 'source_id', 'campaign_id', ]
        utms = []
        for f in f_list:
            x = changes.get(f, [False, False])
            x = x[0] or x[1] or getattr(self, f)
            utms.append(str(x.id if x else 0))
        return {'kw_utm_str': '_'.join(utms)}


class MarketingCost(models.Model):
    _name = 'kw.marketing.cost'
    _inherit = ['kw.marketing.cost.mixin',  'utm.mixin', ]
    _description = 'Marketing Cost'

    name = fields.Char()

    active = fields.Boolean(
        default=True, )
    company_id = fields.Many2one(
        comodel_name='res.company', )
    date = fields.Date(
        default=fields.Date.today, )
    amount = fields.Float()

    currency_id = fields.Many2one(
        comodel_name='res.currency', string='Currency', required=True,
        default=lambda self: self._get_default_currency_id(), )

    def _get_default_currency_id(self):
        return self.env.company.currency_id.id


class Lead(models.Model):
    _name = 'crm.lead'
    _inherit = ['kw.marketing.cost.mixin', 'crm.lead', ]


class Order(models.Model):
    _name = 'sale.order'
    _inherit = ['kw.marketing.cost.mixin', 'sale.order', ]


class Move(models.Model):
    _name = 'account.move'
    _inherit = ['kw.marketing.cost.mixin', 'account.move', ]
