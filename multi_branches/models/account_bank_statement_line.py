# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class AccountBankStatementLine(models.Model):
    _inherit = 'account.bank.statement.line'

    branch_id = fields.Many2one('res.branch', 'Branch', default=lambda self: self.env.user.branch_id, readonly=False)
