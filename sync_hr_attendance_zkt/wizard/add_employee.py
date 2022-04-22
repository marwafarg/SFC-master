# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import json
import requests

from odoo import fields, models, _
from odoo.exceptions import UserError

def _employee_split_name(employee_name):
    return [' '.join(employee_name.split()[:-1]), ' '.join(employee_name.split()[-1:])]


class AddEmployeeZkt(models.TransientModel):
    _name = 'add.employee.zkt'
    _description = 'Add Employee ZKT'

    attendance_zkt_config_id = fields.Many2one('attendance.zkt.config', 'Machine')

    def action_create_employee_zkt(self):
        self.ensure_one()
        if self._context.get('active_model') == 'hr.employee':
            employee_ids = self.env['hr.employee'].browse(self._context.get('active_ids'))
            for employee in employee_ids.filtered(lambda e: not e.biotime_id):
                if not employee.barcode:
                    raise UserError(_('Please enter Badge ID of %s') % (employee.name))
                emp_params = {
                    'emp_code': employee.barcode,
                    'first_name': _employee_split_name(employee.name)[0],
                    'last_name': _employee_split_name(employee.name)[1],
                    'area': [1],
                    'department': employee.department_id and employee.department_id.biotime_id or 1
                }
                response = self.attendance_zkt_config_id._biometric_request(url='personnel/api/employees/#employees-create', data=emp_params, method='POST')
                if response and response.get('id'):
                    employee.write({
                        'biotime_id': response['id'],
                        'attendance_zkt_config_id': self.attendance_zkt_config_id.id
                    })
        return True
