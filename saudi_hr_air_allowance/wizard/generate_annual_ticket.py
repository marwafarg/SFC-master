# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AnnualTicketEmployees(models.TransientModel):
    _name = 'annual.ticket.employees'
    _description = 'Generate Annual Ticket Record for all selected employees'

    employee_ids = fields.Many2many('hr.employee', string='Employees')

    def generate_records(self):
        for rec in self.employee_ids:
            ctx = self.env.context
            ticket_details_obj = self.env['annual.ticket.detail']
            employee = ticket_details_obj.search([('year_id', '=', ctx.get('year_id')), ('employee_id', '=', rec.id)])
            if employee:
                raise ValidationError(_('You already done %s annual ticket for this particular year!!') % rec.name)
            else:
                ticket_details_obj = self.env['annual.ticket.detail']
                ticket_details_ids = ticket_details_obj.search([('employee_id', '=', rec.id), ('annual_ticket_id', '=', ctx.get('active_id'))])
                if ticket_details_ids:
                    raise ValidationError(_('You already generate %s annual ticket details!!') % rec.name)
                else:
                    self.env['annual.ticket.detail'].create({'employee_id': rec.id,
                                                             'annual_ticket_id': ctx.get('active_id'),
                                                             'adult_fare': 0.0,
                                                             'child_fare': 0.0,
                                                             'infant_fare': 0.0,
                                                             'year_id': ctx.get('year_id'),
                                                            })

