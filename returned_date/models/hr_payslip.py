# -*- coding: utf-8 -*-

from odoo import models, fields, api,_
from odoo.exceptions import ValidationError,UserError



class HrPayslip(models.Model):
    _inherit ='hr.payslip'

    @api.model
    def create(self,vals):
        res=super(HrPayslip, self).create(vals)
        for r in res:
            time_request = self.env['hr.leave'].search(
                [('state', '=', 'validate'), ('employee_id', '=', r.employee_id.id),
                 ('request_date_from','<=',r.date_from),('request_date_to','<=',r.date_to)])
            for rec in time_request:
                if rec.number_of_days > rec.holiday_status_id.minimum_days and rec.returned_date == False:
                    raise ValidationError(_('Please Add Returned Date'))

        return res

    def write(self,vals):
        res=super(HrPayslip, self).write(vals)
        for r in self:
            time_request = self.env['hr.leave'].search(
                [('state', '=', 'validate'), ('employee_id', '=', r.employee_id.id),
                 ('request_date_from','<=',r.date_from),('request_date_to','<=',r.date_to)])
            for rec in time_request:
                if rec.number_of_days > rec.holiday_status_id.minimum_days and rec.returned_date == False:
                    raise ValidationError(_('Please Add Returned Date'))

        return res


