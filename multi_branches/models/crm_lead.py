# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class Lead(models.Model):
    _inherit = "crm.lead"

    branch_id = fields.Many2one("res.branch", string='Branch', default=lambda self: self.env.user.branch_id)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            if len(branches) > 0:
                self.branch_id = branches[0]
            else:
                self.branch_id = False
        else:
            return {'domain': {'branch_id': []}}
