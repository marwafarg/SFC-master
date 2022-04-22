# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class GenerateAirAllowance(models.TransientModel):
    _name = 'generate.air.allowance'
    _description = "Generate Air Allowance"

    allowance_amount = fields.Float('Allowance Amount')

    @api.constrains('allowance_amount')
    def check_allowance_amount(self):
        ctx = self.env.context
        if ctx.get('active_id'):
            ticket_detail_id = self.env['annual.ticket.detail'].browse(ctx.get('active_id'))
            if self.allowance_amount > ticket_detail_id.remaining_amount:
                raise ValidationError(_('Allowance amount should be less then remaining amount!!'))

    def generate_allowance(self):
        if self.allowance_amount > 0:
            ctx = self.env.context
            ticket_detail_id = self.env['annual.ticket.detail'].browse(ctx.get('active_id'))
            payslip_data = {'employee_id': ticket_detail_id.employee_id.id,
                            'description': 'Air Allowance',
                            'calc_type': 'amount',
                            'operation_type': 'allowance',
                            'amount': self.allowance_amount or 0,
                            'state': 'done',
                            'ticket_detail_id': ticket_detail_id.id
                            }
            other_hr_payslip_id = self.env['other.hr.payslip'].create(payslip_data).id
