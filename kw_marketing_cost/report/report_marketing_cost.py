import logging

from odoo import models, _
from odoo.osv.expression import AND, OR

_logger = logging.getLogger(__name__)


# pylint: disable=too-many-locals
# pylint: disable=too-many-branches
# pylint: disable=too-many-statements
class MarketingCostXlsx(models.AbstractModel):
    _name = 'report.kw_marketing_cost.kw_marketing_cost_report_xlsx'
    _inherit = 'report.report_xlsx.abstract'
    _description = 'MarketingCostXlsx'

    def generate_xlsx_report(self, workbook, data, objs=None):
        sheet = workbook.add_worksheet('Worksheet_1')
        sheet.set_row(0, 30)
        sheet.set_row(1, 55)
        sheet.set_column('B:C', 30)
        sheet.set_column('D:D', 45)
        sheet.set_column('E:N', 13)

        wb_style = {
            'head': workbook.add_format({
                'align': 'center', 'bold': True, 'text_wrap': True,
                'border': 1, 'valign': 'vcenter'}),
            'percent': workbook.add_format({
                'num_format': '0%', 'valign': 'vcenter', }),
            'vcenter': workbook.add_format({
                'valign': 'vcenter', }),
        }

        sheet.merge_range(
            0, 0, 0, 13, '{} {} {} {}'.format(
                _('Profitability of marketing tools from'), data['date_from'],
                _('to'), data['date_to']), wb_style['head'])

        sheet.write(1, 0, _('#'), wb_style['head'])
        sheet.write(1, 1, _('Tool (medium)'), wb_style['head'])
        sheet.write(1, 2, _('Source (source)'), wb_style['head'])
        sheet.write(1, 3, _('Campaign'), wb_style['head'])
        sheet.write(1, 4, _('Leads'), wb_style['head'])
        sheet.write(1, 5, _('Deals'), wb_style['head'])
        sheet.write(1, 6, _('Conversion'), wb_style['head'])
        sheet.write(1, 7, _('Sales (number of orders)'), wb_style['head'])
        sheet.write(1, 8, _('Amount of sale (payments)'), wb_style['head'])
        sheet.write(1, 9, _('Sales conversion'), wb_style['head'])
        sheet.write(1, 10, _('Expenses'), wb_style['head'])
        sheet.write(1, 11, _('CPL (price per lead)'), wb_style['head'])
        sheet.write(1, 12, _('CPO (order price)'), wb_style['head'])
        sheet.write(1, 13, _('ROMI'), wb_style['head'])

        crm_lead_ids = self.env['crm.lead'].sudo().search(
            AND([
                [('team_id', 'in', data['sales_team_ids'])],
                [('campaign_id', 'in', data['campaign_ids'] + [False, ])],
                [('source_id', 'in', data['source_ids'] + [False, ])],
                [('medium_id', 'in', data['medium_ids'] + [False, ])],
                [('create_date', '<=', data['date_to'])],
                OR([[('date_closed', '=', False)],
                    [('date_closed', '>=', data['date_from'])]
                    ]),
                OR([
                    [('active', '=', True), ],
                    [('active', '=', False), ],
                ]),
            ]))

        sale_order_ids = self.env['sale.order'].sudo().search([
            ('team_id', 'in', data['sales_team_ids']),
            ('state', 'in', ['sale', 'done']),
            ('create_date', '<=', data['date_to']),
            ('create_date', '<=', data['date_to']),
            ('campaign_id', 'in', data['campaign_ids'] + [False, ]),
            ('source_id', 'in', data['source_ids'] + [False, ]),
            ('medium_id', 'in', data['medium_ids'] + [False, ]),
            ('date_order', '>=', data['date_from'])], )

        account_move_ids = self.env['account.move'].sudo().search([
            ('team_id', 'in', data['sales_team_ids']),
            ('state', '=', 'posted',),
            ('move_type', '=', 'out_invoice'),
            ('campaign_id', 'in', data['campaign_ids'] + [False, ]),
            ('source_id', 'in', data['source_ids'] + [False, ]),
            ('medium_id', 'in', data['medium_ids'] + [False, ]),
            ('create_date', '<=', data['date_to']),
            ('invoice_date', '>=', data['date_from'])], )

        marketing_cost_ids = self.env['kw.marketing.cost'].sudo().search([
            ('campaign_id', 'in', data['campaign_ids'] + [False, ]),
            ('source_id', 'in', data['source_ids'] + [False, ]),
            ('medium_id', 'in', data['medium_ids'] + [False, ]),
            ('date', '<=', data['date_to']),
            ('date', '>=', data['date_from'])], )

        utm_list = crm_lead_ids.mapped('kw_utm_str')
        utm_list += sale_order_ids.mapped('kw_utm_str')
        utm_list += account_move_ids.mapped('kw_utm_str')
        utm_list += marketing_cost_ids.mapped('kw_utm_str')
        utm_list = list(dict.fromkeys(filter(bool, utm_list)))
        utm_list.sort()

        row = 1
        prev_utm = False

        for utm in utm_list:
            row += 1
            sheet.set_row(row=row, height=20, cell_format=wb_style['vcenter'])

            medium_id, source_id, campaign_id = \
                [int(x) for x in utm.split('_')]

            domain = [('medium_id', '=', medium_id or False),
                      ('source_id', '=', source_id or False),
                      ('campaign_id', '=', campaign_id or False), ]
            medium_id = self.env['utm.medium'].sudo().browse(medium_id) \
                if medium_id else False
            if not (prev_utm and medium_id and prev_utm[0] == medium_id.id):
                sheet.write(row, 1, medium_id.name if medium_id else 'Empty')

            source_id = self.env['utm.source'].sudo().browse(source_id) \
                if source_id else False
            if not (prev_utm and source_id and prev_utm[1] == source_id.id):
                sheet.write(row, 2, source_id.name if source_id else 'Empty')

            campaign_id = self.env['utm.campaign'].sudo().browse(campaign_id) \
                if campaign_id else False
            sheet.write(row, 3, campaign_id.name if campaign_id else 'Empty')

            prev_utm = [int(x) for x in utm.split('_')]

            crm_lead_qty = len(crm_lead_ids.filtered_domain(domain))
            if crm_lead_qty:
                sheet.write(row, 4, crm_lead_qty)

            opportunity_qty = len(crm_lead_ids.filtered_domain(
                domain + [('type', '=', 'opportunity')]))
            if opportunity_qty:
                sheet.write(row, 5, opportunity_qty)

            if crm_lead_qty and opportunity_qty:
                sheet.write(row, 6, opportunity_qty / crm_lead_qty,
                            wb_style['percent'])

            order_qty = len(sale_order_ids.filtered_domain(domain))
            if order_qty:
                sheet.write(row, 7, order_qty)

            amount_total = sum(account_move_ids.filtered_domain(domain).mapped(
                'amount_total'))
            if amount_total:
                sheet.write(row, 8, round(amount_total))

            if opportunity_qty and order_qty:
                sheet.write(row, 9, order_qty / opportunity_qty,
                            wb_style['percent'])

            marketing_cost = sum(
                marketing_cost_ids.filtered_domain(domain).mapped('amount'))
            if marketing_cost:
                sheet.write(row, 10, round(marketing_cost))

            if marketing_cost and crm_lead_qty:
                sheet.write(row, 11, round(marketing_cost / crm_lead_qty))

            if marketing_cost and order_qty:
                sheet.write(row, 12, round(marketing_cost / order_qty))

            if amount_total and marketing_cost:
                sheet.write(
                    row, 13, (amount_total - marketing_cost) / marketing_cost,
                    wb_style['percent'])
