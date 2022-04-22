# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError, UserError
from odoo.addons.resource.models.resource import datetime_to_string, string_to_datetime, Intervals
from datetime import datetime , date

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_worked_day_lines(self):
        res = super(HrPayslip, self)._get_worked_day_lines()
        lines = {}
        work_entry_type = self.env.ref('hr_time_off_installment.work_entry_type_leave_pay')
        time_request = self.env['hr.leave'].search(
            [('state', '=', 'validate'), ('employee_id', '=', self.employee_id.id),
             ('request_date_from', '<=', self.date_to), ('request_date_to', '>=', self.date_from),
             ('pay_in_advance', '=', 'yes')])
        days = 0
        for time in time_request:
            work_entries=self.contract_id._get_contract_work_entries_values_advance(datetime.combine(self.date_from, time.date_from.time()),datetime.combine(self.date_to, time.date_to.time()))
            for work_entry in work_entries:
                date_start = max(datetime.combine(self.date_from, time.date_from.time()), work_entry['date_start'])
                date_stop = min(datetime.combine(self.date_to, time.date_to.time()), work_entry['date_stop'])
                # if work_entry.work_entry_type_id.is_leave:
                contract = self.env['hr.contract'].browse(work_entry['contract_id'])
                calendar = contract.resource_calendar_id
                employee = contract.employee_id
                contract_data = employee._get_work_days_data_batch(
                    date_start, date_stop, compute_leaves=False, calendar=calendar
                )[employee.id]
                days +=contract_data['days']

        if days > 0:
            for line in work_entry_type:
                if len(res) > 0:
                    if line.id != res[0]['work_entry_type_id']:
                        lines = {
                            'sequence': line.sequence,
                            'work_entry_type_id': line.id,
                            'number_of_days': days,
                            'number_of_hours': 0.0,
                            'amount': 0.0,
                        }
                        res.append(lines)
                else:
                    lines = {
                        'sequence': line.sequence,
                        'work_entry_type_id': line.id,
                        'number_of_days': days,
                        'number_of_hours': 0.0,
                        'amount': 0.0,
                    }
                    res.append(lines)
        return res
