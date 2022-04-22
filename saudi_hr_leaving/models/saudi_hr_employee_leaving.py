# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

leaving_states = [('draft', 'Draft'),
                  ('confirm', 'Waiting Approval'),
                  ('approve', 'Approved'),
                  ('validate', 'Validated'),
                  ('refuse', 'Refused')]


class HREmployeeLeaving(models.Model):
    _name = "hr.employee.leaving"
    _inherit = ['mail.thread']
    _description = "HR Employee Leaving"

    def unlink(self):
        """
            To remove the record, which is in 'draft' states
        """
        for object in self:
            if object.state in ['confirm', 'validate', 'approve', 'refuse']:
                raise UserError(_('You cannot remove the record which is in %s state!') % object.state)
        return super(HREmployeeLeaving, self).unlink()

    # @api.multi
    # def _employee_get(self):
    #     employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)])
    #     if employee_id:
    #         return employee_id[0]
    #     return False

    @api.constrains('notice_start_date', 'requested_date')
    def _check_start_date(self):
        for rec in self:
            if rec.notice_start_date and rec.requested_date and rec.notice_start_date <= rec.requested_date:
                raise ValidationError(_("Notice Start Date must be greater than Requested Date"))

    @api.constrains('notice_end_date', 'notice_start_date')
    def _check_end_date(self):
        for rec in self:
            if rec.notice_end_date and rec.notice_start_date and rec.notice_end_date < rec.notice_start_date:
                raise ValidationError(_("Notice End Date must be greater than Notice Start Date"))

    @api.constrains('exit_date', 'notice_end_date')
    def _check_exit_date(self):
        for rec in self:
            if rec.notice_end_date and rec.exit_date and rec.exit_date < rec.notice_end_date:
                raise ValidationError(_("Exit Date must be greater than Notice End Date"))

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, default=lambda self: self.env['hr.employee'].get_employee())
    department_id = fields.Many2one('hr.department', 'Department', readonly=True)
    branch_id = fields.Many2one('res.branch', 'Office', readonly=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.user.company_id)
    reason = fields.Char('Reason', size=128, required=True)
    requested_date = fields.Date('Requested Date', default=datetime.strftime(datetime.now(), '%Y-%m-%d'))
    notice_start_date = fields.Date('Notice Start Date')
    notice_end_date = fields.Date('Notice End Date')
    exit_date = fields.Date('Exit Date', compute='compute_exit_date', store=True)
    contact_person = fields.Many2one('res.users', 'Contact Person')
    description = fields.Text('Description', required=True)
    state = fields.Selection(leaving_states, 'Status', track_visibility='onchange', default='draft')
    approved_date = fields.Datetime('Approved Date', readonly=True, track_visibility='onchange', copy=False)
    approved_by = fields.Many2one('res.users', 'Approved By', readonly=True, track_visibility='onchange', copy=False)
    refused_by = fields.Many2one('res.users', 'Refused By', readonly=True, track_visibility='onchange', copy=False)
    refused_date = fields.Datetime('Refused Date', readonly=True, track_visibility='onchange', copy=False)

    def _track_subtype(self, init_values):
        self.ensure_one()
        if 'state' in init_values and self.state == 'draft':
            return self.env.ref('saudi_hr_leaving.mt_employee_leaving_new')
        elif 'state' in init_values and self.state == 'confirm':
            return self.env.ref('saudi_hr_leaving.mt_employee_leaving_confirm')
        elif 'state' in init_values and self.state == 'validate':
            return self.env.ref('saudi_hr_leaving.mt_employee_leaving_validate')
        elif 'state' in init_values and self.state == 'approve':
            return self.env.ref('saudi_hr_leaving.mt_employee_leaving_approve')
        elif 'state' in init_values and self.state == 'refuse':
            return self.env.ref('saudi_hr_leaving.mt_employee_leaving_cancel')
        return super(HREmployeeLeaving, self)._track_subtype(init_values)

    def name_get(self):
        """
            to use retrieving the name
        """
        res = []
        for leave in self:
            name = ''.join([leave.employee_id.name or '', ' Leaving'])
            res.append((leave.id, name))
        return res

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
            onchange the value based on selected employee,
            department and company
        """
        self.department_id = self.employee_id.department_id.id or False
        self.company_id = self.employee_id.company_id.id or False
        self.branch_id = self.employee_id.branch_id or False

    @api.onchange('notice_start_date')
    def onchange_notice_start_date(self):
        """
            onchange the value based on selected notice_end_date,
            exit_date
        """
        if self.notice_start_date:
            self.notice_end_date = self.notice_start_date + timedelta(days=60)

    @api.depends('notice_end_date')
    def compute_exit_date(self):
        """
            onchange the value based on selected notice_end_date,
            exit_date
        """
        for rec in self:
            rec.exit_date = rec.notice_end_date or False

    @api.model
    def create(self, values):
        """
            Create a new record
            :return: Newly created record ID
        """
        if values.get('employee_id', False):
            employee = self.env['hr.employee'].browse(values.get('employee_id'))
            values.update({'department_id': employee.department_id.id or False,
                           'company_id': employee.company_id.id or False,
                           'branch_id': employee.branch_id.id or False
                           })
        return super(HREmployeeLeaving, self).create(values)

    def write(self, values):
        """
            Update an existing record.
            :param values: updated values
            :return: Current update record ID
        """
        if values.get('employee_id', False):
            employee = self.env['hr.employee'].browse(values.get('employee_id', self.employee_id.id))
            values.update({'department_id': employee.department_id.id or False,
                           'company_id': employee.company_id.id or False,
                           'branch_id': employee.branch_id.id or False
                           })
        return super(HREmployeeLeaving, self).write(values)

    def leaving_confirm(self):
        """
            sent the status of generating his/her leaving request in confirm state
        """
        self.ensure_one()
        self.state = 'confirm'

    def leaving_approve(self):
        """
            sent the status of generating his/her leaving request in approve state
        """
        self.ensure_one()
        today = datetime.today()
        if self.employee_id:
            self.employee_id.date_of_leave = self.notice_end_date
            contract_ids = self.employee_id._get_contracts(self.notice_start_date, self.notice_end_date, states=['open'])
            if contract_ids:
                contract_ids.write({'notice_start_date': self.notice_start_date or False, 'notice_end_date': self.notice_end_date or False, 'is_leaving': True})
        self.write({'state': 'approve',
                    'approved_by': self.env.uid,
                    'approved_date': today})
        try:
            template_id = self.env.ref('saudi_hr_leaving.email_template_resigned_emp_aknowledgement')
        except ValueError:
            template_id = False
        if template_id:
            template_id.send_mail(self.id, force_send=True)

    def leaving_validate(self):
        """
            sent the status of generating his/her leaving request in Validate state
        """
        self.ensure_one()
        self.state = 'validate'

    def leaving_refuse(self):
        """
            sent the status of generating his/her leaving request in Refuse state
        """
        self.ensure_one()
        self.write({'state': 'refuse',
                    'refused_by': self.env.uid,
                    'refused_date': datetime.today()})

    def set_draft(self):
        """
            sent the status of generating his/her leaving request in Set to Draft state
        """
        self.ensure_one()
        if self.employee_id:
            self.employee_id.date_of_leave = False
            contract_id = self.employee_id._get_contracts(self.notice_start_date, self.notice_end_date, states=['open'])
            if contract_id:
                contract_id.write({'notice_start_date': False, 'notice_end_date': False, 'is_leaving': False})
        self.state = 'draft'
