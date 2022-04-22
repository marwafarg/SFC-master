# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, models, fields, _
from dateutil import relativedelta


class HRLeave(models.Model):
    _inherit = 'hr.leave'

    hr_vacation_id = fields.Many2one('hr.vacation', string='Vacation')


class FlightBooking(models.Model):
    _inherit = 'flight.booking'

    hr_vacation_id = fields.Many2one('hr.vacation', string='Vacation')


class HRVisa(models.Model):
    _inherit = 'hr.visa'

    hr_vacation_id = fields.Many2one('hr.vacation', string='Vacation')


class EmployeeAdvanceSalary(models.Model):
    _inherit = "hr.advance.salary"

    hr_vacation_id = fields.Many2one('hr.vacation', string='Vacation')

    @api.model
    def default_get(self, fields):
        data = super(EmployeeAdvanceSalary, self).default_get(fields)
        context = self._context
        if context.get('default_hr_vacation_id'):
            vacation_id = self.env['hr.vacation'].search([('id', '=', context.get('default_hr_vacation_id'))])
            # vacation = vacation_id.date_to - vacation_id.date_start
            # vacation_days = vacation.days
            # if vacation_id.date_to.month != vacation_id.date_start.month:
            #     month_start_date = vacation_id.date_start.replace(day=1) + relativedelta.relativedelta(months=1)
            #     advance_salary_days = (vacation_id.date_to - month_start_date).days
            #     wage = self.env['hr.contract'].sudo().search([('employee_id', '=', vacation_id.employee_id.id),
            #                                               ('state', '=', 'open')], limit=1).wage
            #     advance_salary = (advance_salary_days * wage)/ 30
            #     data['request_amount'] = advance_salary

            previous_day_of_vacation = (vacation_id.date_start - vacation_id.date_start.replace(day=1)).days
            advance_salary_days = previous_day_of_vacation + vacation_id.vacation_days
            wage = self.env['hr.contract'].sudo().search([('employee_id', '=', vacation_id.employee_id.id),
                                                      ('state', '=', 'open')], limit=1).wage
            advance_salary = advance_salary_days * (wage / 30)
            data['request_amount'] = advance_salary
            data['reason'] = 'Vacation : %s' % vacation_id.name
        return data
