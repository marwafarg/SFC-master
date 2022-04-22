from odoo import api, fields, models


class CrmTeam(models.Model):
    _inherit = 'crm.team'

    is_ecommerce = fields.Boolean(string="")
