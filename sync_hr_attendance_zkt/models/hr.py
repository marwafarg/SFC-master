# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models


class Employee(models.Model):
    _inherit = "hr.employee"

    biotime_id = fields.Integer('BioTime ID')
    attendance_zkt_config_id = fields.Many2one('attendance.zkt.config', 'BioTime Machine ID')


class Empdepartment(models.Model):
    _inherit = "hr.department"

    biotime_id = fields.Integer('BioTime Id')


class Attendance(models.Model):
    _inherit = "hr.attendance"

    biotime_id = fields.Integer('BioTime ID')
    check_out_biotime_id = fields.Integer('Checkout BioTime ID')
