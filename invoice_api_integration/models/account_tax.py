from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.tax'

    is_ecommerce = fields.Boolean(string="")
