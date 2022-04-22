# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from datetime import datetime, timedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class GenerateAttendanceSheet(models.TransientModel):
    _name = 'generate.attendance.sheet'
    _description = 'Generate Attendance Sheet'

    @api.model
    def default_get(self, fields):
        vals = super(GenerateAttendanceSheet, self).default_get(fields)
        if self._context.get('active_model') == 'attendance.sheet' and self._context.get('active_id'):
            attendance_sheet_id = self.env['attendance.sheet'].browse(self._context['active_id'])
            vals.update({
                'start_date': attendance_sheet_id.start_date,
                'end_date': attendance_sheet_id.end_date
            })
        return vals

    employee_ids = fields.Many2many('hr.employee', string="Employee")
    start_date = fields.Date(string='Start Date')
    end_date = fields.Date(string='End Date')

    def generate_attendance_sheet(self):
        self.ensure_one()
        attendance_obj = self.env['hr.attendance']

        def get_daily_attendance(date, employee):
            datetime_start = datetime.combine(date, datetime.min.time())
            datetime_end = datetime_start + timedelta(hours=23, minutes=59, seconds=59)
            attendance_ids = attendance_obj.search([('employee_id', '=', employee.id),
                                                    ('check_in', '>=', datetime_start),
                                                    ('check_out', '<=', datetime_end)])
            attendance_check_in = min(attendance_ids.mapped('check_in')) if attendance_ids.mapped('check_in') else False
            attendance_check_out = max(attendance_ids.mapped('check_out')) if attendance_ids.mapped('check_out') else False
            attendance_vals = attendance_ids._get_attendance_overtime()
            total_overtime = attendance_vals['overtime']
            return {
                'attendance_vals': attendance_vals,
                'total_overtime': total_overtime,
                'check_in_tz': fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance_check_in)) if attendance_check_in else False,
                'check_out_tz': fields.Datetime.context_timestamp(self, fields.Datetime.from_string(attendance_check_out)) if attendance_check_out else False,
                'worked_hours': sum(attendance_ids.mapped('worked_hours'))
            }

        def get_planned_attendance(work_hours, weekday):
            planned_check_in, planned_check_out = [], []
            for wo in work_hours:
                if str(weekday) == wo[2].get('dayofweek'):
                    planned_check_in.append(wo[2].get('hour_from')) if wo[2].get('hour_from') else False
                    planned_check_out.append(wo[2].get('hour_to')) if wo[2].get('hour_to') else False
            return {
                'planned_check_in': min(planned_check_in) if planned_check_in != [] else False,
                'planned_check_out': max(planned_check_out) if planned_check_out != [] else False
            }

        if not self.employee_ids:
            raise ValidationError(_('Please select employee for generate attendance sheet.'))

        sheet_line_vals, working_hours = {}, []
        resource_calendar_id = False

        if self._context.get('active_model') == 'attendance.sheet' and self._context.get('active_id'):
            attendance_sheet_id = self.env['attendance.sheet'].browse(self._context['active_id'])

            for emp in self.employee_ids:
                sheet_line_ids = self.env['attendance.sheet.line'].search([
                        ('employee_id', '=', emp.id),
                        ('start_date', '>=', self.start_date),
                        ('end_date', '<=', self.end_date),
                    ])
                if sheet_line_ids:
                    raise ValidationError(_('You can not create attendance sheet on same time period for %s!' % (emp.name)))

            start_datetime = datetime.combine(self.start_date if self.start_date else attendance_sheet_id.start_date, datetime.min.time())
            end_datetime = datetime.combine(self.end_date if self.end_date else attendance_sheet_id.end_date, datetime.min.time())
            employee_ids = self.employee_ids - attendance_sheet_id.attendance_sheet_line_ids.mapped('employee_id')

            for employee in employee_ids:
                active_contract_ids = employee._get_contracts(start_datetime, end_datetime, states=['open'])
                if active_contract_ids:
                    resource_calendar_id = active_contract_ids[0].resource_calendar_id
                    working_hours = resource_calendar_id.default_get('attendance_ids')['attendance_ids']
                sheet_line_vals.update({'employee_id': employee.id})
                attendance_details = []

                for day in range(int ((self.end_date - self.start_date).days + 1)):
                    attendance_day = self.start_date + timedelta(day)
                    planning_attendance_vals = get_planned_attendance(working_hours, attendance_day.weekday())
                    daily_attendance_vals = get_daily_attendance(attendance_day, employee)
                    attendance_details_data = {
                        'attendance_date': attendance_day,
                        'week_list': attendance_day.weekday(),
                        'planning_check_in': planning_attendance_vals['planned_check_in'],
                        'planning_check_out': planning_attendance_vals['planned_check_out'],
                        'actual_check_in': daily_attendance_vals['check_in_tz'].hour + daily_attendance_vals['check_in_tz'].minute/60.0 if daily_attendance_vals.get('check_in_tz') else False,
                        'actual_check_out': daily_attendance_vals['check_out_tz'].hour + daily_attendance_vals['check_out_tz'].minute/60.0 if daily_attendance_vals.get('check_in_tz') else False,
                        'worked_hours': daily_attendance_vals['worked_hours'],
                        'overtime': daily_attendance_vals['total_overtime'],
                        'planning_worked_hours': resource_calendar_id and resource_calendar_id.hours_per_day
                    }
                    attendance_values = daily_attendance_vals.get('attendance_vals')
                    if daily_attendance_vals.get('worked_hours') == 0.0 and planning_attendance_vals.get('planned_check_in') \
                        and planning_attendance_vals.get('planned_check_out'):
                        attendance_details_data.update({'status': 'absence'})
                    elif daily_attendance_vals.get('worked_hours') > 0.0 and not planning_attendance_vals.get('planned_check_in') \
                        and not planning_attendance_vals.get('planned_check_out') and attendance_values.get('is_weekend'):
                        attendance_details_data.update({'status': 'weekend'})
                    elif attendance_values.get('is_public_day'):
                        attendance_details_data.update({'status': 'public_holiday'})
                    attendance_details.append(attendance_details_data)
                sheet_line_vals.update({
                    'total_attendance': len(attendance_details),
                    'line_details': attendance_details
                })
                attendance_sheet_id._create_attendance_sheet_line(sheet_line_vals)
        return True
