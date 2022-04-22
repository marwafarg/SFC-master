# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta


class HrLeave(models.Model):
    _inherit = "hr.leave"
    returned_date = fields.Date()
    difference = fields.Integer(compute='_get_difference',store=True)
    is_return = fields.Boolean(compute='_get_is_return',store=True)

    @api.depends('holiday_status_id')
    def _get_is_return(self):
        for rec in self:
            if rec.number_of_days > rec.holiday_status_id.minimum_days :
                    # and rec.holiday_status_id.is_annual_leave == True:
                rec.is_return = True
            else:
                rec.is_return = False


    @api.depends('returned_date','request_date_to')
    def _get_difference(self):
        for rec in self:
            fmt = '%Y-%m-%d'
            start_date = rec.returned_date
            end_date = rec.request_date_to
            if start_date and end_date:
                d1 = datetime.strptime(str(start_date), fmt)
                d2 = datetime.strptime(str(end_date), fmt)
                date_difference = d2 - d1
                rec.difference = date_difference.days

class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"
    minimum_days=fields.Integer()






