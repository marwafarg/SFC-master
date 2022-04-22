from odoo import api, fields, models


class AccountInvoice(models.Model):
    _inherit = 'account.journal'

    is_ecommerce = fields.Boolean(string="")
