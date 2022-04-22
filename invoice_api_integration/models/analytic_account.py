from odoo import api, fields, models


class AccountAnalyticAccount(models.Model):
    _inherit = 'account.analytic.account'

    product_type = fields.Selection(string="", selection=[('1', 'Default Product'), ('2', 'Ammunition'),('4', 'Nafath fees'), ('5', 'Tickets'), ], required=False, )
    is_ecommerce = fields.Boolean(string="")
