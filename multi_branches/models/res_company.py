# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class Company(models.Model):
    _inherit = 'res.company'

    @api.model
    def create(self, values):
        return super(Company, self.with_context({'is_branch': True})).create(values)
