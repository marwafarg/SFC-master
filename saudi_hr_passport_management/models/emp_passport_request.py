# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
from datetime import datetime
from dateutil.relativedelta import relativedelta
import time


class EmployeePassportRequest(models.Model):
    _name = 'emp.passport.request'
    _inherit = 'mail.thread'
    _description = "Employee Passport Request"

    @api.depends('employee_id')
    def name_get(self):
        """
            to use retrieving the name, combination of `id & name`
        """
        res = []
        if self.employee_id:
            name = self.employee_id.name or ''
            res.append((self.id, name))
        return res

    def unlink(self):
        for obj in self:
            if obj.state in ['second_approve', 'employee_submit', 'receive']:
                raise UserError(_('You can not delete record in this stage!'))
        return super(EmployeePassportRequest, self).unlink()

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=lambda self: self.env['hr.employee'].get_employee())
    job_id = fields.Many2one('hr.job', string='Job Title', readonly=True)
    department_id = fields.Many2one('hr.department', string='Department', readonly=True)
    branch_id = fields.Many2one('res.branch', string='Office', readonly=True)
    note = fields.Text(string='Description')
    passport_no = fields.Char(string='Passport No', size=50, help='Passport number.')
    store_branch_id = fields.Many2one('res.branch', string='Office', help='Passport store branch.', copy=False)
    loker = fields.Char(string='Locker', copy=False)
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    submit_date = fields.Date(string='Submitted Date', readonly=True, copy=False)
    reason = fields.Selection([('passport_renewal', 'Passport Renewal'),
                               ('address_change', 'Address Change'),
                               ('adding_spouse_name', 'Adding Spouse Name'),
                               ('annual_vacation', 'Annual Vacation'),
                               ('business_trip', 'Business Trip'),
                               ('others', 'Others')], string='Reason')
    other_reason = fields.Text(string='Other Reason')
    receive_by = fields.Many2one('res.users', string='Received By', readonly=True, copy=False)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('first_approve', 'First Approval'),
                              ('second_approve', 'Ready To Allocation'),
                              ('employee_submit', 'Employee Submitted'),
                              ('receive', 'Received'),
                              ('cancel', 'Cancel')], default='draft')

    @api.constrains('date_from', 'date_to')
    def _check_date(self):
        """
            to use add constraint on check_date
        """
        for obj in self:
            if obj.date_from > obj.date_to:
                raise UserError(_('Invalid Date! Please enter valid duration from and to date!'))
        return True

    def _track_subtype(self, init_values):
        """
            to use track on state
        """
        if 'state' in init_values and self.state == 'confirm':
            return 'saudi_hr_passport_management.mt_passport_request_confirm'
        elif 'state' in init_values and self.state == 'first_approve':
            return 'saudi_hr_passport_management.mt_passport_request_approve_gr'
        elif 'state' in init_values and self.state == 'second_approve':
            return 'saudi_hr_passport_management.mt_passport_request_approve_gr_manager'
        elif 'state' in init_values and self.state == 'employee_submit':
            return 'saudi_hr_passport_management.mt_passport_request_employee_submit'
        elif 'state' in init_values and self.state == 'receive':
            return 'saudi_hr_passport_management.mt_passport_request_receive'
        elif 'state' in init_values and self.state == 'cancel':
            return 'saudi_hr_passport_management.mt_passport_request_cancel'
#         if 'stage_id' in init_values and self.state not in ['confirm', 'first_approve', 'second_approve', 'employee_submit', 'receive', 'cancel']:
#             return 'saudi_hr_passport_management.mt_passport_request_stage'
        return super(EmployeePassportRequest, self)._track_subtype(init_values)

    @api.onchange('date_to')
    def onchange_date_to(self):
        """
            set the value onchange of date_to
        """
        if self.date_from and self.date_to and self.date_from >= self.date_to:
            raise UserError(_('Invalid Date! Please enter valid duration from and to date!'))

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
            set the value onchange of employee_id
        """
        self.job_id = self.employee_id.job_id.id or False
        self.department_id = self.employee_id.department_id.id or False
        self.branch_id = self.employee_id.branch_id.id or False
        self.passport_no = False
        doc_type = self.env['res.document.type'].search([('code', '=', 'pno')])
        for doc in self.employee_id.document_ids:
            if doc.type_id == doc_type[0]:
                self.passport_no = doc.doc_number

    @api.model
    def create(self, values):
        """
            Overwrite the create method to add the passport request
        """
        if values.get('employee_id'):
            employee = self.env['hr.employee'].browse(values.get('employee_id'))
            doc_type = self.env['res.document.type'].search([('code', '=', 'pno')])
            passport_no = False
            for doc in employee.document_ids:
                if doc.type_id == doc_type[0]:
                    passport_no = doc.doc_number
            values.update({'job_id': employee.job_id.id or False,
                           'department_id': employee.department_id.id or False,
                           'branch_id': employee.branch_id.id or False,
                           'passport_no': passport_no})
        return super(EmployeePassportRequest, self).create(values)

    def write(self, values):
        """
            Overwrite the write method to change value of the passport request
        """
        if values.get('employee_id'):
            employee = self.env['hr.employee'].browse(values.get('employee_id'))
            doc_type = self.env['res.document.type'].search([('code', '=', 'pno')])
            passport_no = False
            for doc in employee.document_ids:
                if doc.type_id == doc_type[0]:
                    passport_no = doc.doc_number
            values.update({'job_id': employee.job_id.id or False,
                           'department_id': employee.department_id.id or False,
                           'branch_id': employee.branch_id.id or False,
                           'passport_no': passport_no})
        return super(EmployeePassportRequest, self).write(values)

    def act_confirm(self):
        """
            set the confirm state
        """
        self.ensure_one()
        document_id = self.env['res.documents'].search([('employee_id', '=', self.employee_id.id),
                                                        ('doc_number', '=', self.passport_no),
                                                        ('status', '=', 'office')])
        if not document_id:
            raise UserError(_('Your passport is not registered,please contact your HR manger!'))
        if self.employee_id.user_id:
            self.message_subscribe(partner_ids=[self.employee_id.user_id.partner_id.id])
        self.state = 'confirm'

    def act_first_approve(self):
        """
            set the first approval
        """
        self.ensure_one()
        self.state = 'first_approve'
        self.message_subscribe(partner_ids=[self.env.user.partner_id.id])

    def act_second_approve(self):
        """
            set the second approval
        """
        self.ensure_one()
        document_ids = self.env['res.documents'].search([('employee_id', '=', self.employee_id.id),
                                                         ('doc_number', '=', self.passport_no)])
        for document_id in document_ids:
            document_id.write({'status': 'employee'})
        self.state = 'second_approve'
        self.message_subscribe(partner_ids=[self.env.user.partner_id.id])

    def act_employee_submit(self):
        """
            set the employee submit state
        """
        self.ensure_one()
        document_ids = self.env['res.documents'].search([('employee_id', '=', self.employee_id.id),
                                                         ('doc_number', '=', self.passport_no)])
        for document_id in document_ids:
            document_id.sudo().write({'status': 'gr_user'})
        self.write({'state': 'employee_submit',
                    'submit_date': time.strftime('%Y-%m-%d')})

    def act_receive(self):
        """
            set the receive state
        """
        register_ids = self.env['emp.passport.register'].search([('employee_id', '=', self.employee_id.id), ('passport_no', '=', self.passport_no)])
        document_ids = self.env['res.documents'].search([('employee_id', '=', self.employee_id.id), ('doc_number', '=', self.passport_no)])
        for register_id in register_ids:
            body = "Passport Is Relocate from office %s Locker Number %s to office %s Locker Number %s" % (register_id.store_branch_id.name, register_id.loker, self.store_branch_id.name, self.loker)
            register_id.message_post(type="email", subtype='mail.mt_comment', body=_(body))
            register_id.write({'store_branch_id': self.store_branch_id.id, 'loker': self.loker})
        for document_id in document_ids:
            document_id.write({'position': '/'.join([self.store_branch_id.name, self.loker]),
                               'status': 'office'})
        self.write({'state': 'receive', 'receive_by': self.env.user.id})

    def act_cancel(self):
        """
            set the cancel state
        """
        self.ensure_one()
        self.state = 'cancel'

    def act_set_to_draft(self):
        """
            set the draft state
        """
        self.ensure_one()
        self.state = 'draft'

    @api.model
    def send_notification(self):
        """
            send notification of passport request
        """
        try:
            template_id = self.env.ref('saudi_hr_passport_management.passport_resubmission_email')
        except ValueError:
            template_id = False
        request_ids = self.env['emp.passport.request'].search([('state', '=', 'second_approve')])
        for obj in request_ids:
            if obj.date_to:
                notify_date = obj.date_to + relativedelta(days=2)
                if datetime.today().date().strftime('%Y-%m-%d') == notify_date.strftime('%Y-%m-%d') and template_id:
                    template_id.send_mail(obj.id, force_send=True, raise_exception=False)
