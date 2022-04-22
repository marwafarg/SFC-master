# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

import pytz
from datetime import datetime, timedelta
from datetime import time as datetime_time
from odoo import api, models, fields, _
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT
from itertools import groupby
from pytz import utc, timezone


def to_naive_utc(datetime, record):
    tz_name = record._context.get('tz') or record.env.user.tz
    tz = tz_name and pytz.timezone(tz_name) or pytz.UTC
    return tz.localize(datetime.replace(tzinfo=None), is_dst=False).astimezone(pytz.UTC).replace(tzinfo=None)


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    is_verify = fields.Boolean('Skip Confirmation', help='While tick payslips will confirmed and paid.', default=True)

    _sql_constraints = [
        ('date_check', "CHECK(date_end >= date_start)", "The start date must be anterior to the end date."),
    ]


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    bank_account_id = fields.Many2one('res.partner.bank', 'Bank Account Number', help="Employee bank salary account",
                                      states={'draft': [('readonly', False)]})

#     @api.onchange('employee_id', 'date_from', 'date_to')
#     def onchange_employee(self):
#         super(HrPayslip, self).onchange_employee()
#         res = {}
#         self.bank_account_id = False
#         if self.employee_id:
#             self.bank_account_id = self.employee_id.bank_account_id.id,
#             res.update({'domain': {'bank_account_id': [('id', '=', self.employee_id.bank_account_id.id)]}})
#         return res
#
#     def onchange_employee_id(self, date_from, date_to, employee_id=False, contract_id=False):
#         res = super(HrPayslip, self).onchange_employee_id(date_from, date_to, employee_id, contract_id)
#         res['value'].update({'bank_account_id': False})
#         contract_obj = self.env['hr.contract']
#         if employee_id:
#             employee = self.env['hr.employee'].search([('id','=',employee_id)])
#             res['value'].update({
#                                  'bank_account_id': employee.bank_account_id and employee.bank_account_id.id or False,
#                                  'employee_id':employee.id
#                                  })
#             res.update({'domain':{'bank_account_id':[('id','=',employee.bank_account_id and employee.bank_account_id.id or False)]}})
#         if res['value']['contract_id']:
#             result = self.get_worked_day_lines(contract_obj.browse(res['value']['contract_id']) , date_from, date_to)
#             # Note : We have apped result on base method
#             worked_days_line_ids = result
#             # leave_summary = leave_result[1]
#             input_line_ids = self.get_inputs(contract_obj.browse(res['value']['contract_id']), date_from, date_to)
#             res['value'].update({
#                         'worked_days_line_ids': worked_days_line_ids,
#                         'input_line_ids': input_line_ids,
#                         'date_from': date_from,
#                         'date_to': date_to,
#             })
#         return res
#
#     def compute_sheet(self):
#         res = super(HrPayslip, self).compute_sheet()
#         worked_line_obj = self.env['hr.payslip.worked_days']
#         input_line_obj = self.env['hr.payslip.input']
#         sequence_obj = self.env['ir.sequence']
#         for payslip in self:
#             number = payslip.number or sequence_obj.next_by_code('salary.slip')
#             # JIMIT delete old worked data and input data
#             old_worked_lines_ids = worked_line_obj.search([('payslip_id', '=', payslip.id)])
#             if old_worked_lines_ids:
#                 old_worked_lines_ids.unlink()
#             old_input_line_ids = input_line_obj.search([('payslip_id', '=', payslip.id)])
#             if old_input_line_ids:
#                 old_input_line_ids.unlink()
#             if payslip.contract_id:
#                 # set the list of contract for which the rules have to be applied
#                 contract_ids = payslip.contract_id
#             else:
#                 # if we don't give the contract, then the rules to apply should be for all current contracts of the employee
#                 contract_ids = self.get_contract(payslip.employee_id, payslip.date_from, payslip.date_to)
#             # jimit onchange changed
#             if contract_ids:
#                 result = self.get_worked_day_lines(contract_ids, payslip.date_from, payslip.date_to)
#                 # Note : We have apped result on base method
#                 worked_days_line_ids = result
#                 input_line_ids = self.get_inputs(contract_ids, payslip.date_from, payslip.date_to)
#                 if worked_days_line_ids:
#                     payslip.write({'worked_days_line_ids': [(0, 0, worked_days_line_id) for worked_days_line_id in worked_days_line_ids]})
#                 if input_line_ids:
#                     payslip.write({'input_line_ids': [(0, 0, input_id) for input_id in input_line_ids]})
#                 payslip.write({'number': number})# 'line_ids': lines
#         return res
#
#     @api.model
#     def get_worked_day_lines(self, contracts, date_from, date_to):
#         """
#         @param contract: Browse record of contracts
#         @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
#         """
#         res = []
#         for contract in contracts.filtered(lambda contract: contract.resource_calendar_id):
#             day_from = datetime.combine(fields.Date.from_string(date_from), datetime_time.min)
#             day_to = datetime.combine(fields.Date.from_string(date_to), datetime_time.max)
#
#             if not day_from.tzinfo:
#                 day_from = day_from.replace(tzinfo=utc)
#             if not day_to.tzinfo:
#                 day_to = day_to.replace(tzinfo=utc)
#             # total hours per day: retrieve attendances with one extra day margin,
#             # in order to compute the total hours on the first and last days
#                 user_tz = self.env.user.tz or 'UTC'
#                 day_from = day_from.astimezone(timezone(user_tz))
#                 day_to = day_to.astimezone(timezone(user_tz))
#
#             # compute leave days
#             leaves = {}
#             holiday_list = []
#             leave_detail_list = []
#             nb_of_days = (day_to - day_from).days + 1
#             for day in range(0, nb_of_days):
#                 day_from_start = datetime.strptime(((day_from + timedelta(days=day)).strftime("%Y-%m-%d 00:00:00")), DEFAULT_SERVER_DATETIME_FORMAT)
#                 day_from_end = datetime.strptime(((day_from + timedelta(days=day)).strftime("%Y-%m-%d 23:59:59")), DEFAULT_SERVER_DATETIME_FORMAT)
#                 holiday_ids = self.env['hr.leave'].search([('employee_id', '=', contract.employee_id.id),
#                                                            ('state', '=', 'validate'),
#                                                            '|', '&',
#                                                            ('date_from', '>=', str(day_from_start)),
#                                                            ('date_from', '<=', str(day_from_end)),
#                                                            '&',
#                                                            ('date_to', '>=', str(day_from_start)),
#                                                            ('date_to', '<=', str(day_from_end))])
#                 leave_details = self.env['leave.detail'].search([
#                     ('leave_id', 'in', holiday_ids.ids),
#                     ('period_id.date_start', '<=', str(day_from_start.date())),
#                     ('period_id.date_stop', '>=', str(day_from_start.date())),
#                 ])
#                 leave_detail_list.extend(leave_details.ids)
#                 holiday_list.extend(holiday_ids.ids)
#
#             leave_detail_list = self.env['leave.detail'].browse(list(set(leave_detail_list)))
#             leave_detail_object = self.env['leave.detail']
#             for leave_detail in sorted(leave_detail_list, key=lambda l: l.leave_id.holiday_status_id.id):
#                 leave_detail_object += leave_detail
#             paid_leave_days_list = []
#             paid_leave_hours_list = []
#             total_leave_day_list = []
#             total_leave_hours_list = []
#             for holiday_status_id, lines in groupby(leave_detail_object, lambda l: l.leave_id.holiday_status_id.id):
#                 values = list(lines)
#                 holiday_status_id = self.env['hr.leave.type'].browse(holiday_status_id)
#                 paid_leave_days_list.append(sum([detail.paid_leave for detail in values]))
#                 paid_leave_hours_list.append(sum([detail.leave_hours for detail in values]))
#                 total_leave_day_list.append(sum([detail.total_leave for detail in values]))
#                 total_leave_hours_list.append(sum([detail.total_leave_hours for detail in values]))
#                 leave_detail_obj = self.env['leave.detail']
#                 for detail in values:
#                     leave_detail_obj += detail
#                 if leave_detail_obj.filtered(lambda l: l.unpaid_leave):
#                     current_leave_struct = leaves.setdefault(holiday_status_id, {
#                                 'name': holiday_status_id.name + ' Working Days unpaid at 100%',
#                                 'sequence': 5,
#                                 'code': holiday_status_id.code or holiday_status_id.name,
#                                 'number_of_days': sum([detail.unpaid_leave for detail in values]),
#                                 'number_of_hours': sum([detail.unpaid_leave_hours for detail in values]),
#                                 'contract_id': contract.id,
#                             })
#
#             # compute unpaid leaves
#             paid_leave_dict = {}
#             if paid_leave_days_list:
#                 paid_leave_dict = {
#                     'name': _("Leave Working Days paid at 100%"),
#                     'sequence': 2,
#                     'code': 'LEAVES100',
#                     'number_of_days': sum(paid_leave_days_list),
#                     'number_of_hours': sum(paid_leave_hours_list),
#                     'contract_id': contract.id,
#                 }
#
#             # compute worked days
#             work_data = contract.employee_id._get_work_days_data(day_from, day_to, calendar=contract.resource_calendar_id)
#             leave_days = contract.employee_id._get_leave_days_data(day_from, day_to, calendar=contract.resource_calendar_id)
#             leave_hours = self.get_leaves_hours_count(day_from, day_to, employee_id=contract.employee_id, calendar=contract.resource_calendar_id)
#             attendances = {
#                 'name': _("Normal Working Days paid at 100%"),
#                 'sequence': 1,
#                 'code': 'WORK100',
#                 'number_of_days': float((work_data['days']) + leave_days['days']) - sum(total_leave_day_list),
#                 'number_of_hours': float((work_data['hours']) + leave_hours) - sum(total_leave_hours_list),
#                 'contract_id': contract.id,
#             }
#             res.append(attendances)
#             if paid_leave_dict:
#                 res.append(paid_leave_dict)
#             res.extend(leaves.values())
#         return res
#
#     def get_leaves_hours_count(self, from_datetime, to_datetime, employee_id, calendar=None):
#         hours_count = 0.0
#         calendar = calendar or self.resource_calendar_id
#         for day_intervals in calendar._leave_intervals(from_datetime, to_datetime, employee_id.resource_id):
#             # theoric_hours = employee_id.get_day_work_hours_count(day_intervals[0][0].date(), calendar=calendar)
#             leave_time = (day_intervals[1] - day_intervals[0])
#             leave_time = float(float(leave_time.seconds / 60.0) / 60.0)
#             hours_count += leave_time
#         return hours_count
#
#
# class HrPayslipWorkedDays(models.Model):
#     _inherit = 'hr.payslip.worked_days'
#
#     working_hours = fields.Float('Working Hour(s)')
#     absence_hours = fields.Float('Absence Hour(s)', default=0.0)
