import logging
from datetime import date

from odoo import models, fields, exceptions, _

_logger = logging.getLogger(__name__)


class MarketingCostWizard(models.TransientModel):
    _name = 'kw.marketing.cost.report'
    _description = 'Marketing Cost Report'

    date_from = fields.Date(
        string='Start Date', default=date.today(), required=True, )
    date_to = fields.Date(
        string='End Date', default=date.today(), required=True, )
    sales_team_ids = fields.Many2many(
        comodel_name='crm.team', string='Sales team',
        default=lambda self: self._get_default_marketing('team'))
    campaign_ids = fields.Many2many(
        comodel_name='utm.campaign', string='Campaign',
        default=lambda self: self._get_default_marketing('campaign'))
    source_ids = fields.Many2many(
        comodel_name='utm.source', string='Source',
        default=lambda self: self._get_default_marketing('source'))
    medium_ids = fields.Many2many(
        comodel_name='utm.medium', string='Medium',
        default=lambda self: self._get_default_marketing('medium'))

    def _get_default_marketing(self, param=None):
        if param not in ['medium', 'source', 'campaign', 'team']:
            raise exceptions.ValidationError(_('Invalid param for default!!!'))
        crm_ids = self.env['crm.lead'].sudo().search([
            ('company_id.id', 'in', self.env.companies.ids), ]).mapped(
                f'{param}_id')
        objs = []
        for crm in crm_ids:
            if crm.company_id.id in self.env.companies.ids:
                objs.append(crm.id)
        return objs

    def _get_default_sales_team_ids(self):
        return self.env['crm.team'].search([])

    def get_self_action(self):
        return {
            'context': self.env.context,
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'kw.marketing.cost.report',
            'res_id': self.id,
            'view_id': False,
            'type': 'ir.actions.act_window',
            'target': 'new', }

    def remove_sales(self):
        self.sales_team_ids = [(5, 0, 0)]
        return self.get_self_action()

    def remove_campaign(self):
        self.campaign_ids = [(5, 0, 0)]
        return self.get_self_action()

    def remove_source(self):
        self.source_ids = [(5, 0, 0)]
        return self.get_self_action()

    def remove_medium(self):
        self.medium_ids = [(5, 0, 0)]
        return self.get_self_action()

    def get_report(self):
        data = {
            'id': self.id,
            'date_from': self.date_from,
            'date_to': self.date_to,
            'sales_team_ids': self.sales_team_ids.ids,
            'campaign_ids': self.campaign_ids.ids,
            'source_ids': self.source_ids.ids,
            'medium_ids': self.medium_ids.ids, }
        report = self.env.ref(
            'kw_marketing_cost.kw_marketing_cost_report_xlsx').sudo()
        return report.report_action(self, data=data)
