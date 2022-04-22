# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class AttendanceRules(models.Model):
    _name = 'attendance.rules'
    _description = 'Attendance Rules'

    name = fields.Char('Name', required=True)
    rule_type = fields.Selection([
        ('late_in', 'Late In')
    ], required=True, default='late_in')
    # ('working_days', 'Working Days'),
    # ('weekend_days', 'Weekend Days'),
    # ('public_holidays', 'Public Holidays'),
    rate = fields.Float('Rate')
    apply_after = fields.Float('Apply after')
    attendance_policy_id = fields.Many2one('attendance.policy', 'Attendance Policy')
