# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

from collections import defaultdict
from datetime import date, datetime
from odoo import api, fields, models
from odoo.addons.resource.models.resource_mixin import timezone_datetime
from odoo.addons.resource.models.resource import datetime_to_string, string_to_datetime, Intervals

import pytz


class HrContract(models.Model):
    _inherit = 'hr.contract'
    def _get_contract_work_entries_values_advance(self, date_start, date_stop):
        self.ensure_one()
        contract_vals = []
        employee = self.employee_id
        calendar = self.resource_calendar_id
        resource = employee.resource_id
        tz = pytz.timezone(calendar.tz)
        start_dt = pytz.utc.localize(date_start) if not date_start.tzinfo else date_start
        end_dt = pytz.utc.localize(date_stop) if not date_stop.tzinfo else date_stop

        attendances = calendar._attendance_intervals_batch(
            start_dt, end_dt, resources=resource, tz=tz
        )[resource.id]

        # Other calendars: In case the employee has declared time off in another calendar
        # Example: Take a time off, then a credit time.
        # YTI TODO: This mimics the behavior of _leave_intervals_batch, while waiting to be cleaned
        # in master.
        resources_list = [self.env['resource.resource'], resource]
        resource_ids = [False, resource.id]
        leave_domain = [
            ('time_type', '=', 'leave'),
            # ('calendar_id', '=', self.id), --> Get all the time offs
            ('resource_id', 'in', resource_ids),
            ('date_from', '<=', datetime_to_string(end_dt)),
            ('date_to', '>=', datetime_to_string(start_dt)),
        ]
        result = defaultdict(lambda: [])
        tz_dates = {}
        for leave in self.env['resource.calendar.leaves'].search(leave_domain):
            for resource in resources_list:
                if leave.resource_id.id not in [False, resource.id]:
                    continue
                tz = tz if tz else pytz.timezone((resource or self).tz)
                if (tz, start_dt) in tz_dates:
                    start = tz_dates[(tz, start_dt)]
                else:
                    start = start_dt.astimezone(tz)
                    tz_dates[(tz, start_dt)] = start
                if (tz, end_dt) in tz_dates:
                    end = tz_dates[(tz, end_dt)]
                else:
                    end = end_dt.astimezone(tz)
                    tz_dates[(tz, end_dt)] = end
                dt0 = string_to_datetime(leave.date_from).astimezone(tz)
                dt1 = string_to_datetime(leave.date_to).astimezone(tz)
                if leave.holiday_id.pay_in_advance == 'yes':
                    result[resource.id].append((max(start, dt0), min(end, dt1), leave))
        mapped_leaves = {r.id: Intervals(result[r.id]) for r in resources_list}
        leaves = mapped_leaves[resource.id]

        real_attendances = attendances - leaves
        real_leaves = attendances - real_attendances

        # A leave period can be linked to several resource.calendar.leave
        split_leaves = []
        for leave_interval in leaves:
            if leave_interval[2] and len(leave_interval[2]) > 1:
                split_leaves += [(leave_interval[0], leave_interval[1], l) for l in leave_interval[2]]
            else:
                split_leaves += [(leave_interval[0], leave_interval[1], leave_interval[2])]
        leaves = split_leaves

        # Attendances
        default_work_entry_type = self._get_default_work_entry_type()
        # for interval in real_attendances:
        #     work_entry_type_id = interval[2].mapped('work_entry_type_id')[:1] or default_work_entry_type
        #     # All benefits generated here are using datetimes converted from the employee's timezone
        #     contract_vals += [{
        #         'name': "%s: %s" % (work_entry_type_id.name, employee.name),
        #         'date_start': interval[0].astimezone(pytz.utc).replace(tzinfo=None),
        #         'date_stop': interval[1].astimezone(pytz.utc).replace(tzinfo=None),
        #         'work_entry_type_id': work_entry_type_id.id,
        #         'employee_id': employee.id,
        #         'contract_id': self.id,
        #         'company_id': self.company_id.id,
        #         'state': 'draft',
        #     }]

        for interval in real_leaves:
            # Could happen when a leave is configured on the interface on a day for which the
            # employee is not supposed to work, i.e. no attendance_ids on the calendar.
            # In that case, do try to generate an empty work entry, as this would raise a
            # sql constraint error
            if interval[0] == interval[1]:  # if start == stop
                continue
            leave_entry_type = self._get_interval_leave_work_entry_type(interval, leaves)
            interval_start = interval[0].astimezone(pytz.utc).replace(tzinfo=None)
            interval_stop = interval[1].astimezone(pytz.utc).replace(tzinfo=None)
            contract_vals += [dict([
                ('name', "%s%s" % (leave_entry_type.name + ": " if leave_entry_type else "", employee.name)),
                ('date_start', interval_start),
                ('date_stop', interval_stop),
                ('work_entry_type_id', leave_entry_type.id),
                ('employee_id', employee.id),
                ('company_id', self.company_id.id),
                ('state', 'draft'),
                ('contract_id', self.id),
            ] + self._get_more_vals_leave_interval(interval, leaves))]
        return contract_vals

    def _get_contract_work_entries_values(self, date_start, date_stop):
        self.ensure_one()
        contract_vals = []
        employee = self.employee_id
        calendar = self.resource_calendar_id
        resource = employee.resource_id
        tz = pytz.timezone(calendar.tz)
        start_dt = pytz.utc.localize(date_start) if not date_start.tzinfo else date_start
        end_dt = pytz.utc.localize(date_stop) if not date_stop.tzinfo else date_stop

        attendances = calendar._attendance_intervals_batch(
            start_dt, end_dt, resources=resource, tz=tz
        )[resource.id]

        # Other calendars: In case the employee has declared time off in another calendar
        # Example: Take a time off, then a credit time.
        # YTI TODO: This mimics the behavior of _leave_intervals_batch, while waiting to be cleaned
        # in master.
        resources_list = [self.env['resource.resource'], resource]
        resource_ids = [False, resource.id]
        leave_domain = [
            ('time_type', '=', 'leave'),
            # ('calendar_id', '=', self.id), --> Get all the time offs
            ('resource_id', 'in', resource_ids),
            ('date_from', '<=', datetime_to_string(end_dt)),
            ('date_to', '>=', datetime_to_string(start_dt)),
        ]
        result = defaultdict(lambda: [])
        tz_dates = {}
        for leave in self.env['resource.calendar.leaves'].search(leave_domain):
            for resource in resources_list:
                if leave.resource_id.id not in [False, resource.id]:
                    continue
                tz = tz if tz else pytz.timezone((resource or self).tz)
                if (tz, start_dt) in tz_dates:
                    start = tz_dates[(tz, start_dt)]
                else:
                    start = start_dt.astimezone(tz)
                    tz_dates[(tz, start_dt)] = start
                if (tz, end_dt) in tz_dates:
                    end = tz_dates[(tz, end_dt)]
                else:
                    end = end_dt.astimezone(tz)
                    tz_dates[(tz, end_dt)] = end
                dt0 = string_to_datetime(leave.date_from).astimezone(tz)
                dt1 = string_to_datetime(leave.date_to).astimezone(tz)
                if leave.holiday_id.pay_in_advance != 'yes':
                    result[resource.id].append((max(start, dt0), min(end, dt1), leave))
        mapped_leaves = {r.id: Intervals(result[r.id]) for r in resources_list}
        leaves = mapped_leaves[resource.id]

        real_attendances = attendances - leaves
        real_leaves = attendances - real_attendances

        # A leave period can be linked to several resource.calendar.leave
        split_leaves = []
        for leave_interval in leaves:
            if leave_interval[2] and len(leave_interval[2]) > 1:
                split_leaves += [(leave_interval[0], leave_interval[1], l) for l in leave_interval[2]]
            else:
                split_leaves += [(leave_interval[0], leave_interval[1], leave_interval[2])]
        leaves = split_leaves

        # Attendances
        default_work_entry_type = self._get_default_work_entry_type()
        for interval in real_attendances:
            work_entry_type_id = interval[2].mapped('work_entry_type_id')[:1] or default_work_entry_type
            # All benefits generated here are using datetimes converted from the employee's timezone
            contract_vals += [{
                'name': "%s: %s" % (work_entry_type_id.name, employee.name),
                'date_start': interval[0].astimezone(pytz.utc).replace(tzinfo=None),
                'date_stop': interval[1].astimezone(pytz.utc).replace(tzinfo=None),
                'work_entry_type_id': work_entry_type_id.id,
                'employee_id': employee.id,
                'contract_id': self.id,
                'company_id': self.company_id.id,
                'state': 'draft',
            }]

        for interval in real_leaves:
            # Could happen when a leave is configured on the interface on a day for which the
            # employee is not supposed to work, i.e. no attendance_ids on the calendar.
            # In that case, do try to generate an empty work entry, as this would raise a
            # sql constraint error
            if interval[0] == interval[1]:  # if start == stop
                continue
            leave_entry_type = self._get_interval_leave_work_entry_type(interval, leaves)
            interval_start = interval[0].astimezone(pytz.utc).replace(tzinfo=None)
            interval_stop = interval[1].astimezone(pytz.utc).replace(tzinfo=None)
            contract_vals += [dict([
                ('name', "%s%s" % (leave_entry_type.name + ": " if leave_entry_type else "", employee.name)),
                ('date_start', interval_start),
                ('date_stop', interval_stop),
                ('work_entry_type_id', leave_entry_type.id),
                ('employee_id', employee.id),
                ('company_id', self.company_id.id),
                ('state', 'draft'),
                ('contract_id', self.id),
            ] + self._get_more_vals_leave_interval(interval, leaves))]
        return contract_vals


