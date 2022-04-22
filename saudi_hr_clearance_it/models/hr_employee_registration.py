# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class EquipmentRegistration(models.Model):
    _inherit = "equipment.registration"

    it_dept_id = fields.Many2one('hr.employee.clearance')
