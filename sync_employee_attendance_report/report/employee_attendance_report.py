# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from odoo import api, models, fields, _
from odoo.exceptions import Warning
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class EmployeeReportAttendance(models.AbstractModel):
    _name = 'report.sync_employee_attendance_report.attendance_report_view'
    _description = 'Employee Attendance Report'

    @api.model
    def _get_report_values(self, docids, data=None):
        date_start_obj = datetime.strptime(data['form']['date_start'], DATE_FORMAT)
        date_end_obj = datetime.strptime(data['form']['date_end'], DATE_FORMAT)
        docs = []
        attendance_info = {}

        for employee in data['form']['employee_ids']:
            total_hours = []
            for attendance in self.env['hr.attendance'].search([]).filtered(lambda l: l.employee_id.id == employee and l.check_in >= date_start_obj and l.check_out <=  date_end_obj and l.check_in <= l.check_out and l.check_out >= l.check_in):
                delta = attendance.check_out - attendance.check_in
                result = 0
                (h, m, s) = str(delta).split(':')
                result = int(h) * 3600 + int(m) * 60 + int(s)
                total_hours.append(result)
                docs.append({
                    'employee': attendance.employee_id.name,
                    'check_in': attendance.check_in,
                    'check_out': attendance.check_out,
                    'delta': delta,
                    })
                total = sum(total_hours)
                hours, remainder = divmod(total, 3600)
                minutes, seconds = divmod(remainder, 60)
                total_time_hours = ''
                total_time_hours = '{:02}:{:02}:{:02}'.format(int(hours), int(minutes), int(seconds))
                attendance_info[employee] = {
                    'emp_name': attendance.employee_id.name,
                    'department': attendance.department_id.name,
                    'docs': docs,
                    'time1': total_time_hours,
                    }
        if not attendance_info:
            raise Warning(_('No records Found !'))
        return {
            'doc_ids': attendance,
            'doc_model': 'hr_attendance.hr.attendance',
            'attendance_info': attendance_info,
            }
