# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
import datetime


class HrTimesheetSheet(models.Model):
    _inherit = 'hr_timesheet.sheet'

    attendances_ids = fields.One2many('hr.attendance', 'sheet_id', string='Attendances', copy=False)
    total_attendance = fields.Float(string='Total Attendance', readonly=True, copy=False)
    total_timesheet = fields.Float(string='Total Timesheet', readonly=True, copy=False)
    total_difference = fields.Float(string='Difference', readonly=True, copy=False)
    total_overtime = fields.Float(string='Total Overtime', readonly=True, copy=False)
    period_ids = fields.One2many('hr_timesheet_sheet_sheet_day', 'sheet_id', string='Period', readonly=True, copy=False)
    attendance_count = fields.Integer(compute='_compute_attendances', string="Attendances")

    def _get_working_hours(self, active_contract, period_id):
        working_hours = active_contract.resource_calendar_id.default_get('attendance_ids')['attendance_ids']
        period_id.total_working_hours = 0
        for hours in working_hours:
            if int(hours[2].get('dayofweek')) == int(period_id.name.weekday()):
                diff = int(hours[2].get('hour_to')) - int(hours[2].get('hour_from'))
                period_id.total_working_hours += diff

    def action_timesheet_confirm(self):
        res = super(HrTimesheetSheet, self).action_timesheet_confirm()
        for rec in self:
            rec.compute_timesheet()
        return res

    def compute_timesheet(self):
        """
            compute attendance sheet
        """
        self.period_ids.unlink()
        date_array = (self.date_start + datetime.timedelta(days=x) for x in range(0, (self.date_end - self.date_start).days + 1))
        for date_object in date_array:
            self.write({'period_ids': [(0, 0, {'name': date_object.strftime("%Y-%m-%d"), 'total_overtime': 0,
                        'total_attendance': 0, 'total_timesheet': 0, })], })
        attendances_ids = self.env['hr.attendance'].search([('employee_id', '=', self.employee_id.id), ('check_in', '>=', self.date_start), ('check_in', '<=', self.date_end), ('check_out', '>=', self.date_start), ('check_out', '<=', self.date_end)])
        attendances_ids._compute_sheet()
        for period_id in self.period_ids:
            period_id.reason = ''
            # active_contract = self.employee_id.get_active_contracts(date=self.date_start)
            active_contract = self.employee_id._get_contracts(self.date_start, self.date_end, states=['open'])
            for timesheet in self.env['account.analytic.line'].search(
                [('employee_id', '=', self.employee_id.id), ('date', '=', period_id.name)]):
                period_id.total_timesheet += timesheet.unit_amount
            overtime_hours = 0
            total_attendance = 0
            self._get_working_hours(active_contract, period_id)
            for attendance in self.attendances_ids:
                attendance.get_attendance_duration()
                if attendance.check_in.date() == period_id.name:
                    total_attendance += attendance.duration
                if total_attendance > 0:
                    overtime_hours = total_attendance - period_id.total_working_hours

            period_id.total_attendance = total_attendance
            if active_contract:
                if active_contract.calculate_overtime and active_contract.overtime_limit and overtime_hours:
                    period_id.total_overtime = active_contract.overtime_limit if overtime_hours > active_contract.overtime_limit else overtime_hours

                elif active_contract.calculate_overtime and not active_contract.overtime_limit:
                    if overtime_hours > 0:
                        period_id.total_overtime = overtime_hours
                    else:
                        period_id.total_overtime = 0
            period_id.total_difference = (period_id.total_attendance - period_id.total_timesheet)
            public_holidays = self.env['hr.holidays.public.line'].search(
                [('start_date', '>=', period_id.name), ('end_date', '<=', period_id.name)])
            if public_holidays:
                period_id.reason += ', '.join([holiday.name for holiday in public_holidays])
                period_id.total_overtime = period_id.total_attendance
            if active_contract:
                working_days = self.env['hr.leave'].isWorkingDay(period_id.name, employee_id=self.employee_id.id, contract_ids=active_contract[0])
                if not working_days:
                    period_id.reason = 'Weekend '
            hr_holidays = self.env['hr.leave'].search(
                [('employee_id', '=', self.employee_id.id), ('state', '=', 'validate'),
                 ('date_from', '<=', period_id.name.strftime("%Y-%m-%d")),
                 ('date_to', '>=', period_id.name.strftime("%Y-%m-%d"))])
            if hr_holidays:
                period_id.reason += ', '.join([holiday.holiday_status_id.name for holiday in hr_holidays])
                period_id.holiday_ids = [(6, 0, hr_holidays.ids)]
        self.total_attendance = sum(line.total_attendance for line in self.period_ids)
        self.total_difference = sum(line.total_difference for line in self.period_ids)
        self.total_timesheet = sum(line.total_timesheet for line in self.period_ids)
        self.total_overtime = sum(line.total_overtime for line in self.period_ids)

#     def buttton_timesheet(self):
#         """
#             display employee's timesheet
#         """
#         account_ids = self.env['account.analytic.line'].search([('employee_id', '=', self.employee_id.id)])
#         action = self.env.ref('hr_timesheet.act_hr_timesheet_line')
#         result = action.read()[0]
#         if len(account_ids) > 1:
#             result['domain'] = [('id', 'in', account_ids.ids)]
#         elif len(account_ids) == 1:
#             res = self.env.ref('hr_timesheet.hr_timesheet_line_form', False)
#             result['views'] = [(res.id, 'form')]
#             result['res_id'] = account_ids[0].id
#         else:
#             result['domain'] = [('id', 'in', account_ids.ids)]
#         return result
#
#     def action_sheet_report(self):
#         """
#             display attendance in employee between start date to end date
#         """
#         self.ensure_one()
#         return {'type': 'ir.actions.act_window', 'name': 'HR Timesheet/Attendance Report',
#             'res_model': 'hr.timesheet.attendance.report',
#             'domain': [('date', '>=', self.date_start), ('date', '<=', self.date_end)], 'view_mode': 'pivot',
#             'context': {'search_default_user_id': self.user_id.id, }}

    @api.depends('attendances_ids')
    def _compute_attendances(self):
        """
            count total attendances between start date to end date
        """
        for sheet in self:
            sheet.attendance_count = len(sheet.attendances_ids)


class hr_timesheet_sheet_sheet_day(models.Model):
    _name = "hr_timesheet_sheet_sheet_day"
    _description = "Timesheets by Period"
    _order = 'name'

    name = fields.Date('Date', readonly=True)
    sheet_id = fields.Many2one('hr_timesheet.sheet', string='Sheet', readonly=True, index=True)
    total_timesheet = fields.Float(string='Total Timesheet', readonly=True)
    total_attendance = fields.Float(string='Attendance', readonly=True)
    total_difference = fields.Float(string='Difference', readonly=True)
    total_overtime = fields.Float(string='Overtime', readonly=True)
    total_working_hours = fields.Float(string='Working Hours', readonly=True)
    reason = fields.Char(string='Reason', readonly=True)
    holiday_ids = fields.Many2many('hr.leave', string="Leave Request")


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    sheet_id_computed = fields.Many2one('hr_timesheet.sheet', string='Sheet Computed', compute='_compute_sheet',
                                        index=True, ondelete='cascade', search='_search_sheet', store=True)
    sheet_id = fields.Many2one('hr_timesheet.sheet', compute='_compute_sheet', string='Sheet', store=True)

    @api.depends('employee_id', 'check_in', 'check_out', 'sheet_id_computed.date_end', 'sheet_id_computed.date_start', 'sheet_id_computed.employee_id')
    def _compute_sheet(self):
        """
            Links the attendance to the corresponding sheet
        """
        for attendance in self:
            attendance.sheet_id_computed = False
            attendance.sheet_id = False
            corresponding_sheet = self.env['hr_timesheet.sheet'].search(
                [('date_end', '>=', attendance.check_in), ('date_start', '<=', attendance.check_in),
                 ('employee_id', '=', attendance.employee_id.id),
                 ('state', 'in', ['draft', 'new'])], limit=1)
            if corresponding_sheet:
                attendance.sheet_id_computed = corresponding_sheet[0]
                attendance.sheet_id = corresponding_sheet[0]

    def _search_sheet(self, operator, value):
        assert operator == 'in'
        ids = []
        for ts in self.env['hr_timesheet.sheet'].browse(value):
            self._cr.execute("""
                    SELECT a.id
                        FROM hr_attendance a
                    WHERE %(date_end)s >= a.check_in
                        AND %(date_start)s <= a.check_in
                        AND %(employee_id)s = a.employee_id
                    GROUP BY a.id""", {'date_start': ts.date_start,
                                       'date_end': ts.date_end,
                                       'employee_id': ts.employee_id.id, })
            ids.extend([row[0] for row in self._cr.fetchall()])
        domain = [('id', 'in', ids)]
        return domain