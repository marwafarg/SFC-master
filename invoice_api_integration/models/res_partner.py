from odoo import api, fields, models


class ResPartner(models.Model):
    _inherit = 'res.partner'

    client_id = fields.Char(string="Client ID", required=False, )
    client_nation_id = fields.Char(string="Client NID", required=False, )
    is_ecommerce = fields.Boolean(string="")
