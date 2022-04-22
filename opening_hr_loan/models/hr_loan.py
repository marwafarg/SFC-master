# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import time

from lxml import etree
from datetime import timedelta, datetime, date

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError, ValidationError



class HrLoan(models.Model):
    _inherit = 'hr.loan'

    is_opening = fields.Boolean(track_visibility='onchange')
    original_amount = fields.Float('Original Amount', digits='Account', required=True, track_visibility='onchange')
    already_amount = fields.Float('Already Amount', digits='Account', required=True, track_visibility='onchange')

    @api.onchange('is_opening','original_amount','already_amount')
    def onchange_opening_loan(self):
        for rec in self:
            if rec.is_opening == True:
                rec.loan_amount=rec.original_amount - rec.already_amount

    @api.constrains('original_amount','already_amount')
    def onchange_amount_opening(self):
        for rec in self:
            if rec.original_amount < rec.already_amount:
                raise ValidationError(_("Original Amount should n't be less than Already Amount"))

    def confirm_loan(self):
        res=super(HrLoan, self).confirm_loan()
        for rec in self:
            if rec.is_opening == True:
                rec.state = 'approve'
        return res

