# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models, api, _
from datetime import datetime, timedelta
from odoo.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = "hr.payslip"

    def _get_working_hours(self, active_contract, period_id):
        working_hours = active_contract.resource_calendar_id.default_get('attendance_ids')['attendance_ids']
        for hours in working_hours:
            if int(hours[2].get('dayofweek')) == int(period_id.weekday()):
                diff = int(hours[2].get('hour_to')) - int(hours[2].get('hour_from'))
                if diff > 0:
                    return True
                return False

    @api.model
    def get_worked_day_lines(self, contract_ids, date_from, date_to):
        """
        @param contract_ids: list of contract id
        @return: returns a list of dict containing the input that should be applied for the given contract between date_from and date_to
        """
        res = super(HrPayslip, self).get_worked_day_lines(contract_ids, date_from, date_to)
        attendance = [attendance for attendance in res if attendance.get('code') == 'WORK100']
        if attendance:
            attendance = attendance[0]
            attendance['overtime_hours'] = 0.0

            def overtime_hours(employee_id, contract_id, datetime_day):
                overtime = 0.0
                day = datetime_day.strftime("%Y-%m-%d")
                sheet_day_obj = self.env['hr_timesheet_sheet_sheet_day']
                contract = self.env['hr.contract'].browse(contract_id)
                sheet_day_ids = sheet_day_obj.search([('name', '=', day), ('sheet_id.employee_id', '=', employee_id), ('sheet_id.state', '=', 'done')])
                if sheet_day_ids and contract.calculate_overtime:
                   overtime = sheet_day_ids[0].total_overtime
                return overtime
            holiday_obj = self.env['hr.leave']
            attendance_obj = self.env['hr.attendance']
            year_obj = self.env['year.year']
            for contract in contract_ids:
                if not contract.resource_calendar_id:
                    continue
                weekend_overtime = {}
                public_overtime = {}
                year_id = year_obj.find(date_from, True)
                to_year_id = year_obj.find(date_to, True)
                if year_id.id != to_year_id.id:
                    raise ValidationError(_('You can not generate 2 different year payslip!'))
                nb_of_days = (date_to - date_from).days + 1
                for day in range(0, nb_of_days):
                    working_day = (date_from + timedelta(days=day)).strftime("%Y-%m-%d 23:59:59")
                    from_datetime = datetime.combine((date_from + timedelta(days=day)), datetime.min.time())
                    working_hours_on_day = self._get_working_hours(active_contract=contract, period_id=from_datetime)
                    overtime_hour = overtime_hours(contract.employee_id.id, contract.id, date_from + timedelta(days=day))
                    public_day = holiday_obj.isPublicDay(from_datetime, employee_id=contract.employee_id.id, fiscalyear=year_id)
                    if contract.overtime_limit and contract.overtime_limit < overtime_hour:
                        overtime_hour = contract.overtime_limit
                    if working_hours_on_day and not public_day:
                        attendance['overtime_hours'] += overtime_hour
                    elif public_day and contract.public_holiday_overtime:
                        if overtime_hour > 0:
                            public_overtime.update({
                                'name': _("Public Holiday Working Days paid at 250%"),
                                'sequence': 3,
                                'code': 'HOLIDAY_OVERTIME',
                                'number_of_days': (public_overtime.get('number_of_days') or 0) + 1,
                                'overtime_hours': (public_overtime.get('overtime_hours') or 0) + overtime_hour,
                                'contract_id': contract.id,
                            })
                    elif not working_hours_on_day and contract.weekend_overtime:
                        if overtime_hour > 0:
                            weekend_overtime.update({
                                'name': _("Weekends Working Days paid at 200%"),
                                'sequence': 2,
                                'code': 'WEEKEND_OVERTIME',
                                'number_of_days': (weekend_overtime.get('number_of_days') or 0) + 1,
                                'overtime_hours': (weekend_overtime.get('overtime_hours') or 0) + overtime_hour,
                                'contract_id': contract.id,
                            })
                # Put this in comment because of apply float_time widget in xml
                # hours, minutes = attendance_obj.float_time_convert(attendance['overtime_hours']).split(":")
                # attendance['overtime_hours'] = float('%02d.%02d' % (int(hours), int(minutes)))
                # if weekend_overtime:
                #     hours, minutes = attendance_obj.float_time_convert(weekend_overtime['overtime_hours']).split(":")
                #     weekend_overtime['overtime_hours'] = float('%02d.%02d' % (int(hours), int(minutes)))
                # if public_overtime:
                #     hours, minutes = attendance_obj.float_time_convert(public_overtime['overtime_hours']).split(":")
                #     public_overtime['overtime_hours'] = float('%02d.%02d' % (int(hours), int(minutes)))
                if weekend_overtime:
                    res += [weekend_overtime]
                if public_overtime:
                    res += [public_overtime]
        return res


class hr_payslip_worked_days(models.Model):
    _inherit = 'hr.payslip.worked_days'

    overtime_hours = fields.Float('Overtime Hours', default=0.0, copy=False)
