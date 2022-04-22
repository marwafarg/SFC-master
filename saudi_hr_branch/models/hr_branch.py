# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


# class HrBranch(models.Model):
#     _inherit = 'res.branch'
#     _description = "To Manage Multiple Branch within one Company."
#
#     arabic_name = fields.Char('Arabic Name', size=64)
#     code = fields.Char('Code', size=64, required=True)
#     company_name = fields.Char('Company Name', size=128)
#     company_arabic_name = fields.Char('Company Arabic Name', size=128)
#     po_box_no = fields.Char('P.O.Box', size=128)
#     arabic_street = fields.Char('Street', size=128)
#     arabic_street2 = fields.Char('Street2', size=128)
#     arabic_city = fields.Char('City', size=128)
#     arabic_country = fields.Char('Country', size=128)
#     mobile = fields.Char('Mobile', size=18)
