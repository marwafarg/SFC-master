# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import date


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def _get_worked_day_lines(self):
        res = super (HrPayslip, self)._get_worked_day_lines()
        contract = self.contract_id
        if contract.resource_calendar_id:
            sheet_line_ids = self.env['attendance.sheet.line'].search(
            [
                ('employee_id', '=', self.employee_id.id),
                ('state', 'in', ['confirm']),
                ('start_date', '>=', self.date_from),
                ('end_date', '<=', self.date_to),
            ])
            working_days_hours = 0
            public_holidays_hours = 0
            weekends_hours = 0

            for sheet_line in sheet_line_ids:
                working_days_hours += sheet_line.total_overtime
                public_holidays_hours += sheet_line.total_public_holiday_overtime
                weekends_hours += sheet_line.total_weekend_holiday_overtime

            if working_days_hours > 0:
                res.append({'work_entry_type_id':  self.env.ref('sync_hr_attendance_sheet.work_entry_type_normal_working_days_overtime').id,
                    'name': 'Working days Overtime',
                    'number_of_days': working_days_hours / contract.resource_calendar_id.hours_per_day,
                    'number_of_hours': working_days_hours,
                    'amount': 0.0,
                    })
            if public_holidays_hours > 0:
                res.append({'work_entry_type_id':  self.env.ref('sync_hr_attendance_sheet.work_entry_type_public_holiday_overtime').id,
                    'name': 'Public Holidays Overtime',
                    'number_of_days': public_holidays_hours / contract.resource_calendar_id.hours_per_day,
                    'number_of_hours': public_holidays_hours,
                    'amount': 0.0,
                    })
            if weekends_hours > 0:
                res.append({'work_entry_type_id':  self.env.ref('sync_hr_attendance_sheet.work_entry_type_weekend_overtime').id,
                    'name': 'Weekend days Overtime',
                    'number_of_days': weekends_hours / contract.resource_calendar_id.hours_per_day,
                    'number_of_hours': weekends_hours,
                    'amount': 0.0,
                    })
        return res