# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AttendanceSheet(models.Model):
    _name = 'attendance.sheet'
    _description = 'Attendance Sheet'

    name = fields.Char('Sheet Name', required=True)
    start_date = fields.Date(string='Start Date', default=lambda self: fields.Date.to_string(date.today().replace(day=1)), required=True)
    end_date = fields.Date(string='End Date', default=lambda self: fields.Date.to_string((datetime.now() + relativedelta(months=+1, day=1, days=-1)).date()),
                                required=True)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('refuse', 'Refused')], 'Status', track_visibility='onchange', default='draft')
    attendance_policy_id = fields.Many2one('attendance.policy', 'Attendance Policy')
    attendance_sheet_line_ids = fields.One2many('attendance.sheet.line', 'attendance_sheet_id', string='Attendance Sheet Lines')

    _sql_constraints = [
             ('check_date', 'CHECK(end_date >= start_date AND start_date <= end_date)',
             'The Start Date should be less then End Date and End Date Should be greater then Start Date.')]

    # @api.constrains('start_date', 'end_date')
    # def _check_start_end_date(self):
    #     for record in self:
    #         sheet_ids = self.search_count([('start_date', '<=', record.end_date), ('end_date', '>=', record.start_date), ('id', '!=', record.id)])
    #         if sheet_ids:
    #             raise ValidationError(_('You can not create attendance sheet on same time period!'))

    def unlink(self):
        for rec in self.filtered(lambda s: s.state == 'confirm'):
            raise ValidationError(_('You can not delete record on confirm state.'))
        return super(AttendanceSheet, self).unlink()

    def action_confirm(self):
        self.ensure_one()
        self.state = 'confirm'

    def action_refuse(self):
        self.ensure_one()
        self.state = 'refuse'

    def _create_attendance_sheet_line(self, vals):
        self.ensure_one()
        attendance_line_obj = self.env['attendance.sheet.line']
        values = {
            'employee_id': vals.get('employee_id'),
            'total_attendance': vals.get('total_attendance'),
            'num_total_overtime': vals.get('num_total_overtime'),
            'total_overtime': vals.get('total_overtime'),
            'num_total_absence': vals.get('num_total_absence'),
            'total_absence': vals.get('total_absence'),
            'num_total_diff_time': vals.get('num_total_diff_time'),
            'total_diff_time': vals.get('total_diff_time'),
            'num_total_late_in': vals.get('num_total_late_in'),
            'total_late_in': vals.get('total_late_in'),
            'attendance_sheet_id': self.id,
        }
        if vals.get('line_details'):
            line_details = []
            for line in vals['line_details']:
                line_details.append((0, 0, {
                    'attendance_date': line.get('attendance_date'),
                    'week_list': str(line.get('week_list')),
                    'planning_check_in': line.get('planning_check_in'),
                    'planning_check_out': line.get('planning_check_out'),
                    'actual_check_in': line.get('actual_check_in'),
                    'actual_check_out': line.get('actual_check_out'),
                    'worked_hours': line.get('worked_hours'),
                    'planning_worked_hours': line.get('planning_worked_hours'),
                    'overtime': line.get('overtime'),
                    'diff_time': line.get('diff_time'),
                    'status': line.get('status'),
                }))
            values.update({'attendance_sheet_details_ids': line_details})
        return attendance_line_obj.create(values)


class AttendanceSheetLine(models.Model):
    _name = 'attendance.sheet.line'
    _description = 'Attendance Sheet Line'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    attendance_sheet_id = fields.Many2one('attendance.sheet', 'Attendance Sheet', required=True)
    start_date = fields.Date(string="Start Date", related='attendance_sheet_id.start_date', store=True)
    end_date = fields.Date(string="End Date", related='attendance_sheet_id.end_date', store=True)
    state = fields.Selection(string="State", related="attendance_sheet_id.state", store=True)

    total_attendance = fields.Integer('Total Attendance', required=False)
    num_total_overtime = fields.Integer('No. of Total Overtimes', compute='_compute_sheet_data', store=True)
    total_overtime = fields.Float('Total OverTime', compute='_compute_sheet_data', store=True)
    total_normal_overtime = fields.Float('Total Normal OverTime', compute='_compute_sheet_data', store=True)
    total_public_holiday_overtime = fields.Float('Total Public Holiday Overtime', compute='_compute_sheet_data', store=True)
    total_weekend_holiday_overtime = fields.Float('Total Weekends Holiday Overtime', compute='_compute_sheet_data', store=True)
    num_total_absence = fields.Integer('No. of Total Absence', compute='_compute_sheet_data', store=True)
    total_absence = fields.Float('Total Absence(H)', compute='_compute_sheet_data', store=True)
    num_total_diff_time = fields.Integer('No. of Diff Times', compute='_compute_sheet_data', store=True)
    total_diff_time = fields.Float('Total Diff Times(H)', compute='_compute_sheet_data', store=True)
    num_total_late_in = fields.Integer('No. of Late In', compute='_compute_sheet_data', store=True)
    total_late_in = fields.Float('Total Late In', compute='_compute_sheet_data', store=True)
    total_no_policy_late_in = fields.Integer('No. Policy Based Late In', compute='_compute_sheet_data', store=True)
    total_no_approve_late_in = fields.Integer('No. Approved Late In', compute='_compute_sheet_data', store=True)
    total_no_refuse_late_in = fields.Integer('No. Refuse Late In', compute='_compute_sheet_data', store=True)
    attendance_sheet_details_ids = fields.One2many('attendance.sheet.details', 'attendance_sheet_line_id', 'Attendance Details')

    @api.depends('attendance_sheet_details_ids', 'attendance_sheet_details_ids.is_approved', 'attendance_sheet_details_ids.is_refused')
    def _compute_sheet_data(self):
        def _get_data(sheet_line, sheet_field):
            return sum(sheet_line.mapped(sheet_field))

        for line in self:
            line.total_overtime = _get_data(line.attendance_sheet_details_ids, 'overtime')
            line.total_public_holiday_overtime = _get_data(line.attendance_sheet_details_ids.filtered(lambda a: a.status == 'public_holiday'), 'overtime')
            line.total_weekend_holiday_overtime = _get_data(line.attendance_sheet_details_ids.filtered(lambda a: a.status == 'weekend'), 'overtime')
            line.total_normal_overtime = line.total_overtime - (line.total_public_holiday_overtime + line.total_weekend_holiday_overtime)
            line.total_diff_time = _get_data(line.attendance_sheet_details_ids, 'diff_time')
            line.total_late_in = _get_data(line.attendance_sheet_details_ids, 'total_late_in')
            absence_line = line.attendance_sheet_details_ids.filtered(lambda a: a.status == 'absence').mapped('planning_worked_hours')
            line.total_absence = sum(absence_line)
            line.num_total_absence = len(absence_line)
            line.num_total_overtime = len(line.attendance_sheet_details_ids.filtered(lambda a: a.overtime > 0))
            line.num_total_diff_time = len(line.attendance_sheet_details_ids.filtered(lambda a: a.diff_time != 0))
            line.num_total_late_in = len(line.attendance_sheet_details_ids.filtered(lambda a: a.late_in > 0))
            line.total_no_policy_late_in = len(line.attendance_sheet_details_ids.filtered(lambda l: l.late_in != 0).mapped('late_in'))
            line.total_no_approve_late_in = len(line.attendance_sheet_details_ids.filtered(lambda l: l.is_approved).mapped('late_in'))
            line.total_no_refuse_late_in = len(line.attendance_sheet_details_ids.filtered(lambda l: l.is_refused).mapped('late_in'))

    def deduct_late_entry_days(self):
        self.ensure_one()
        if any(self.attendance_sheet_details_ids.filtered(lambda l: l.late_in > 0 and not l.is_approved and not l.is_refused)):
            raise ValidationError(_("Please approve or refuse late entry."))
        context = dict(self.env.context or {})
        context.update({
            'default_employee_id': self.employee_id.id,
            'default_description': 'Late Entry Deduction',
            'default_calc_type': 'days',
            'default_date': fields.Date.today(),
            'default_no_of_days': self.total_no_refuse_late_in,
            'default_operation_type': 'deduction',
        })
        action = {
                'name': _('Other Allowances/Deduction'),
                'view_mode': 'form',
                'res_model': 'other.hr.payslip',
                'view_id': self.env.ref('saudi_hr_payroll.other_hr_payslip_form1').id,
                'type': 'ir.actions.act_window',
                'context': context,
                'target': 'new'
            }
        return action

    def approve_all_late_in(self):
        self.ensure_one()
        for line in self.attendance_sheet_details_ids.filtered(lambda a: a.late_in > 0 and not a.is_refused and not a.is_approved):
            line.approve_late_in()
        return True

    def refuse_all_late_in(self):
        self.ensure_one()
        for line in self.attendance_sheet_details_ids.filtered(lambda a: a.late_in > 0 and not a.is_refused and not a.is_approved):
            line.refuse_late_in()
        return True


class AttendanceSheetDetails(models.Model):
    _name = 'attendance.sheet.details'
    _description = 'Attendance Sheet Details'

    attendance_date = fields.Date('Date', required=True)
    week_list = fields.Selection([
                        ('0', 'Monday'),
                        ('1', 'Tuesday'),
                        ('2', 'Wednesday'),
                        ('3', 'Thursday'),
                        ('4', 'Friday'),
                        ('5', 'Saturday'),
                        ('6', 'Sunday')
                    ], string='Day', required=True)
    planning_check_in = fields.Float('Planned Check-in')
    planning_check_out = fields.Float('Planned Check-out')
    actual_check_in = fields.Float('Actual Check-in')
    actual_check_out = fields.Float('Actual Check-out')
    planning_worked_hours = fields.Float('Planned Worked Hours')
    worked_hours = fields.Float('Worked Hours')
    late_in = fields.Float('Late In Entry', compute='_compute_sheet_late_in', store=True)
    total_late_in = fields.Float('Total Late In', compute='_compute_sheet_late_in', store=True)
    overtime = fields.Float('Overtime')
    diff_time = fields.Float('Diff Time', compute='_compute_sheet_diff_time', store=True)
    status = fields.Selection([
            ('weekend', 'Week End'),
            ('absence', 'Absence'),
            ('public_holiday', 'Public Holiday')
        ], string="Status")
    attendance_sheet_line_id = fields.Many2one('attendance.sheet.line', 'Attendance Sheet Line')
    is_approved = fields.Boolean('Approved Late Entry', default=False)
    is_refused = fields.Boolean('Refuse Late Entry', default=False)

    def approve_late_in(self):
        self.ensure_one()
        self.is_approved = True

    def refuse_late_in(self):
        self.ensure_one()
        self.is_refused = True

    @api.depends('planning_check_in', 'actual_check_in')
    def _compute_sheet_late_in(self):
        for record in self.filtered(lambda s: s.planning_check_in and s.actual_check_in and s.actual_check_in > s.planning_check_in):
            total_late_in = record.actual_check_in - record.planning_check_in
            record.late_in = record.actual_check_in - record.planning_check_in
            record.total_late_in = total_late_in if total_late_in > 0 else 0.0
            if record.attendance_sheet_line_id and record.attendance_sheet_line_id.attendance_sheet_id \
                and record.attendance_sheet_line_id.attendance_sheet_id.attendance_policy_id and \
                record.attendance_sheet_line_id.attendance_sheet_id.attendance_policy_id.apply_after:
                late_in = record.actual_check_in - (record.planning_check_in + record.attendance_sheet_line_id.attendance_sheet_id.attendance_policy_id.apply_after)
                record.late_in = late_in if late_in > 0 else 0.0

    @api.depends('worked_hours', 'planning_worked_hours')
    def _compute_sheet_diff_time(self):
        for record in self.filtered(lambda s: s.worked_hours > 0):
            if record.planning_check_in == 0 and record.planning_check_out == 0:
                record.diff_time = record.worked_hours
            else:
                record.diff_time = record.worked_hours - record.planning_worked_hours
