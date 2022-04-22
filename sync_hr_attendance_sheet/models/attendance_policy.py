# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models


class AttendancePolicy(models.Model):
    _name = 'attendance.policy'
    _description = 'Attendance Policy'

    name = fields.Char('Name', required=True)
    attendance_rules_ids = fields.One2many('attendance.rules', 'attendance_policy_id', string='Attendance Rules')
    apply_after = fields.Float('Apply after')
    # late_in_policy_id = fields.Many2one('attendance.rules', 'Late in Rule')
