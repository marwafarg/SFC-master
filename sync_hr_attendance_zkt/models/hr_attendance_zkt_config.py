# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import json
import requests
import logging
import pytz

from werkzeug import urls
from datetime import timedelta, datetime

from odoo import api, fields, models, _
from odoo.exceptions import UserError
from odoo.tools import DEFAULT_SERVER_DATETIME_FORMAT as DS

_logger = logging.getLogger(__name__)


class HrAttendanceZktConfig(models.Model):
    _name = 'attendance.zkt.config'
    _description = 'HR Attendance ZKT Config'

    @api.model
    def _tz_get(self):
        return [(x, x) for x in pytz.all_timezones]

    name = fields.Char('Name', required=True)
    device_ip = fields.Char('Device URL', help="Need to add url with port. EX: 192.168.218.8:8090 or domain")
    #port = fields.Char('Port', size=4)
    device_password = fields.Char('Device Password')
    device_user = fields.Char('Device User Name')
    device_token = fields.Char('Token')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company)
    date_tz = fields.Selection('_tz_get', string='Timezone', required=True, default=lambda self: self.env.user.tz or 'UTC')
    active = fields.Boolean('Active', default=True, help="If the active field is set to False, it will allow you to hide the Biometric machine without removing it.")
    last_synchronized_date = fields.Datetime('Last Synchronized Date')

    _sql_constraints = [('ip_uniq', 'unique(device_ip)', 'Machine IP address must be unique!')]

    def _get_biometric_url(self, url):
        return urls.url_join('http://%s' % self.device_ip, url)

    def _biometric_request(self, url, data=False, method='POST', is_token=False):
        """ Biometric request method for get and post data to biometric machine. """
        self.ensure_one()
        response = False
        request_url = self._get_biometric_url(url)
        headers = {'Content-Type': 'application/json'}
        if not is_token:
            headers = {'Content-Type': 'application/json', 'Authorization': 'JWT %s' % (self.device_token)}
        try:
            if method == 'POST':
                resp = requests.post(request_url, 
                                    data=json.dumps(data),
                                    headers=headers)
                response = json.loads(resp.content)
            elif method == 'GET':
                resp = requests.get(request_url, headers=headers)
                response = json.loads(resp.content)
        except Exception as e:
            raise UserError(_('Biotime Error: %s !' % e))
        return response

    def connect_biometric_zkt(self):
        self.ensure_one()
        connect_params = {"username": self.device_user, "password": self.device_password}
        response = self._biometric_request(url='jwt-api-token-auth/', data=connect_params, method='POST', is_token=True)
        if response and response.get('token'):
            self.device_token = response['token']
        else:
            raise UserError(_('Please enter correct configuration parameters.'))

    def create_department_biometric_zkt(self):
        self.ensure_one()
        if not self.device_token:
            self.connect_biometric_zkt()
        department_ids = self.env['hr.department'].search([('biotime_id', '=', False)], order="id ASC")
        for department in department_ids:
            dept_params = {
                'dept_code': 'Dept_%s' % (department.id),
                'dept_name': department.name,
            }
            if department.parent_id and department.parent_id.biotime_id:
                dept_params.update({'parent_dept': department.parent_id.biotime_id})
            response = self._biometric_request(url='personnel/api/departments/#departments-create', data=dept_params, method='POST')
            if response and response.get('id'):
                department.biotime_id = int(response['id'])
            elif response and not response.get('id') and response.get('dept_code'):
                raise UserError(_(response['dept_code']))
            elif response and not response.get('id') and response.get('parent_dept'):
                raise UserError(_(response['parent_dept']))

    def create_area_biometric_zkt(self):
        self.ensure_one()
        if not self.device_token:
            self.connect_biometric_zkt()
        if self.company_id:
            area_params = {
                'area_code': 'Area_%s' % (self.company_id.id),
                'area_name': self.company_id.name,
            }
            if self.company_id.parent_id and self.company_id.parent_id.biotime_id:
                area_params.update({'parent_area': self.company_id.parent_id.biotime_id})
            response = self._biometric_request(url='personnel/api/areas/#areas-create', data=area_params, method='POST')
            if response and response.get('id'):
                self.company_id.biotime_id = int(response['id'])
            elif response and not response.get('id') and response.get('area_code'):
                raise UserError(_(response['area_code']))
            elif response and not response.get('id') and response.get('parent_area'):
                raise UserError(_(response['parent_area']))

    def convert_date_tz(self, date=False, tz=False, is_in=False):
        date = datetime.strptime(date.strftime(DS), DS)
        local_tz = pytz.timezone(tz or 'GMT')
        local_dt = local_tz.localize(date, is_dst=None).utcoffset()
        utc_dt = date + local_dt
        if is_in:
            utc_dt = date - local_dt
        return utc_dt

    def get_attendance(self):
        def get_attendance_details(url):
            return record._biometric_request(url=url, method='GET')

        def get_attendance_data(attendees_data, employee_url):
            response = get_attendance_details(employee_url)
            if response.get('data'):
                attendees_data += response['data']
            if response.get('next'):
                get_attendance_data(attendees_data, '/'.join(response['next'].split("/")[3:]))

        attendance_obj = self.env['hr.attendance']
        for record in self.search([('active', '=', True)]):
            if not record.device_token:
                record.connect_biometric_zkt()
            headers = {'Content-Type': 'application/json', 'Authorization': 'JWT %s' % (record.device_token)}
            employee_ids = self.env['hr.employee'].search([('attendance_zkt_config_id', '=', record.id),
                                                           ('company_id', '=', record.company_id.id)])
            date_time_tz = self.convert_date_tz(date=fields.Datetime.now(), tz=record.date_tz)
            start_time = self.convert_date_tz(date=record.last_synchronized_date, tz=record.date_tz) if record.last_synchronized_date else False
            for employee in employee_ids:
                attendees_data = []
                if start_time:
                    employee_url = 'iclock/api/transactions/?emp_code=%s&start_time=%s&end_time=%s' % (employee.barcode, start_time, date_time_tz)
                else:
                    employee_url = 'iclock/api/transactions/?emp_code=%s' % (employee.barcode)
                get_attendance_data(attendees_data, employee_url)
                for atte_data in attendees_data:
                    is_attendance = False
                    if atte_data.get('punch_time'):
                        punch_time = datetime.strptime(atte_data['punch_time'], DS)
                        punch_time_tz = self.convert_date_tz(date=punch_time, tz=record.date_tz, is_in=True)
                        attendance_id = attendance_obj.search([('employee_id', '=', employee.id),
                                                               ('check_in', '!=', None),
                                                               ('check_out', '=', None)], limit=1)
                        if attendance_id and attendance_id.check_in < punch_time_tz:
                            attendance_id.write({'check_out': punch_time_tz, 'check_out_biotime_id': atte_data.get('id') or False})
                        else:
                            # we take the latest attendance before our check_in time and check it doesn't overlap with ours
                            last_attendance_before_check_in = attendance_obj.search([
                                ('employee_id', '=', employee.id),
                                ('check_in', '<=', punch_time_tz)], order='check_in desc', limit=1)
                            if last_attendance_before_check_in and last_attendance_before_check_in.check_out and last_attendance_before_check_in.check_out > punch_time_tz:
                                is_attendance = True
                                _logger.warn(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                                    'empl_name': employee.name,
                                    'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(punch_time_tz))),
                                })

                            # if our attendance is "open" (no check_out), we verify there is no other "open" attendance
                            no_check_out_attendances = attendance_obj.search([
                                ('employee_id', '=', employee.id),
                                ('check_out', '=', False)], order='check_in desc', limit=1)
                            if no_check_out_attendances:
                                is_attendance = True
                                _logger.warn(_("Cannot create new attendance record for %(empl_name)s, the employee hasn't checked out since %(datetime)s") % {
                                    'empl_name': employee.name,
                                    'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(punch_time_tz))),
                                })

                            # we verify that the latest attendance with check_in time before our check_out time
                            # is the same as the one before our check_in time computed before, otherwise it overlaps
                            last_attendance_before_check_out = attendance_obj.search([
                                ('employee_id', '=', employee.id),
                                ('check_in', '<', punch_time_tz)], order='check_in desc', limit=1)
                            if last_attendance_before_check_out and last_attendance_before_check_in != last_attendance_before_check_out:
                                is_attendance = True
                                _logger.warn(_("Cannot create new attendance record for %(empl_name)s, the employee was already checked in on %(datetime)s") % {
                                    'empl_name': employee.name,
                                    'datetime': fields.Datetime.to_string(fields.Datetime.context_timestamp(self, fields.Datetime.from_string(punch_time_tz))),
                                })

                            if atte_data.get('id') and any(attendance_obj.search(['|',('biotime_id', '=', atte_data['id']), \
                                                                ('check_out_biotime_id', '=', atte_data['id'])])):
                                is_attendance = True

                            # Create new attendance with check-in
                            if not is_attendance:
                                attendance_id = attendance_obj.create({
                                    'employee_id': employee.id,
                                    'check_in': punch_time_tz,
                                    'biotime_id': atte_data.get('id') or False
                                })
                record.last_synchronized_date = fields.Datetime.now()
        return True
