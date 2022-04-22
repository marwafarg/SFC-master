# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.exceptions import UserError
#from dateutil import relativedelta
#from datetime import datetime
#from odoo.tools import DEFAULT_SERVER_DATE_FORMAT as DATE_FORMAT


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.model
    def create(self, vals):
        ir_config_obj = self.env['ir.config_parameter'].sudo()
        if ir_config_obj.get_param('saudi_hr_vacations.join_work_after_vacation'):
            vacation_id = self.env['hr.vacation'].search([('employee_id', '=', vals.get('employee_id')),
                                                        ('state', 'not in', ['join_work_after_vacation', 'cancel', 'draft']),
                                                        '|', ('date_start', '<', vals.get('date_to')),
                                                        ('date_to', '<', vals.get('date_to'))])

            if vacation_id:
                emp_id = self.env['hr.employee'].search([('id', '=', vals.get('employee_id'))])
                raise UserError(_("You can't able to create Payslip for this month duration of %s employee." %emp_id.name))
            # vacation_id = self.env['hr.vacation'].search([('employee_id', '=', vals.get('employee_id')),
            #                                             ('state', 'not in', ['join_work_after_vacation', 'cancel', 'draft'])], order='date_start')
            # if vacation_id and vacation_id[-1].date_start.month != vacation_id[-1].date_to.month:
            #     restrict_date = vacation_id[-1].date_start.replace(day=1) + relativedelta.relativedelta(months=1)
            #     if vals.get('date_from') and restrict_date <= datetime.strptime(vals.get('date_from'), DATE_FORMAT).date():
            #         raise UserError(_("You can't able to create Payslip for this month"))
        res = super(HrPayslip, self).create(vals)
        return res

    # @api.onchange('date_from', 'date_to')
    # def onchange_date(self):
    #     ir_config_obj = self.env['ir.config_parameter'].sudo()
    #     if ir_config_obj.get_param('saudi_hr_vacations.join_work_after_vacation'):
    #         vacation_id = self.env['hr.vacation'].search([('employee_id', '=', self.employee_id.id),
    #                                                     ('state', 'not in', ['join_work_after_vacation', 'cancel', 'draft']),
    #                                                     '|', ('date_start', '<', self.date_to),
    #                                                     ('date_to', '<', self.date_to)])
    #         if vacation_id:
    #             raise UserError(_("You can't able to create Payslip for this month"))
