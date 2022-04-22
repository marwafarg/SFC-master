# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models


class Attendance(models.Model):
    _inherit = "hr.attendance"

    def _get_attendance_overtime(self):
        overtime, total_work_hours, hours_per_day = 0.0, 0.0, 0.0
        is_working_day, is_public_day, is_weekend = False, False, False
        holiday_obj = self.env['hr.leave']
        for rec in self:
            if rec.check_out:
                fiscalyear = self.env['year.year'].find(rec.check_in.date(), True)
                active_contract_ids = rec.employee_id._get_contracts(rec.check_in, rec.check_in, states=['open'])
                if active_contract_ids and active_contract_ids[0].calculate_overtime:
                    resource_calendar_id = active_contract_ids[0].resource_calendar_id
                    is_working_day = holiday_obj.isWorkingDay(rec.check_in.date(), employee_id=rec.employee_id.id, contract_ids=active_contract_ids[0])
                    is_public_day = holiday_obj.isPublicDay(rec.check_in, employee_id=rec.employee_id.id, fiscalyear=fiscalyear)
                    is_weekend = holiday_obj.isweekend(rec.check_in.date(), contract=active_contract_ids[0])
                    if is_weekend and active_contract_ids[0].weekend_overtime:
                        overtime += rec.worked_hours
                    elif is_public_day and active_contract_ids[0].public_holiday_overtime:
                        overtime += rec.worked_hours
                    elif is_working_day:
                        total_work_hours += rec.worked_hours
                        hours_per_day = resource_calendar_id.hours_per_day
        if total_work_hours > 0 and hours_per_day > 0 and (total_work_hours - hours_per_day) > 0:
            overtime = total_work_hours - hours_per_day
        attendance_vals = {
            'is_working_day': is_working_day,
            'is_public_day': is_public_day,
            'is_weekend': is_weekend,
            'overtime': overtime
        }
        return attendance_vals
        # return overtime
