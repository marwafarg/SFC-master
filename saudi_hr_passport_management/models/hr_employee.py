# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import _, api, fields, models


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    passport_id = fields.Many2one('emp.passport.register', string="Passport No")


class User(models.Model):
    _inherit = 'res.users'

    passport_id = fields.Many2one('emp.passport.register', string="Passport No")