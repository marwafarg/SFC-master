# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError

class ResCompany(models.Model):
    _inherit = "res.company"
    loan_account_id = fields.Many2one('account.account', 'Loan Account', required=True)
    maximum_amount_loan= fields.Float('Maximum Amount Loan %', required=True,default=100.00)

class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'
    loan_account_id = fields.Many2one('account.account', 'Loan Account',related='company_id.loan_account_id', required=True, readonly=False)
    maximum_amount_loan= fields.Float('Maximum Amount Loan',related='company_id.maximum_amount_loan',required=True,readonly=False)

