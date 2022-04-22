# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import _, api, fields, models
from odoo.exceptions import UserError
import time


class IntPassportProcess(models.Model):
    _name = 'int.passport.process'
    _inherit = 'mail.thread'
    _description = "Internal Passport process"

    @api.depends('employee_id')
    def name_get(self):
        """
            to use retrieving the name, combination of `id & name`
        """
        res = []
        if self.employee_id:
            name = self.employee_id and self.employee_id.name or ''
            res.append((self.id, name))
        return res

    def unlink(self):
        for obj in self:
            if obj.state in ['approve', 'submit']:
                raise UserError(_('You can not delete record in this stage!'))
        return super(IntPassportProcess, self).unlink()

    user_id = fields.Many2one('res.users', string='User', required=True, default=lambda self: self.env.user.id)
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=lambda self: self.env['hr.employee'].get_employee())
    note = fields.Text(string='Description')
    passport_no = fields.Char(string='Passport No', size=50, help='Passport number.')
    store_branch_id = fields.Many2one('res.branch', string='Office', help='Passport store branch.', copy=False)
    loker = fields.Char(string='Locker', copy=False)
    date_from = fields.Date(string='From')
    date_to = fields.Date(string='To')
    submit_date = fields.Date(string='Submitted Date', readonly=True, copy=False)
    approve_by = fields.Many2one('res.users', string='Approve By', copy=False)
    approve_date = fields.Datetime(string='Approve Date', copy=False)
    reason = fields.Selection([('passport_renewal', 'Passport Renewal'),
                               ('address_change', 'Address Change'),
                               ('adding_spouse_name', 'Adding Spouse Name'),
                               ('annual_vacation', 'Annual Vacation'),
                               ('business_trip', 'Business Trip'),
                               ('others', 'Others')], string='Reason')
    other_reason = fields.Text(string="Other Reason")
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('approve', 'Approved'),
                              ('submit', 'Submitted'),
                              ('cancel', 'Cancel')], default='draft')

    @api.constrains('date_from', 'date_to')
    def _check_mobile_number(self):
        """
            to use add constraint on mobile_number
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
            return 'saudi_hr_passport_management.mt_internal_passport_process_confirm'
        elif 'state' in init_values and self.state == 'approve':
            return 'saudi_hr_passport_management.mt_internal_passport_process_approve'
        elif 'state' in init_values and self.state == 'submit':
            return 'saudi_hr_passport_management.mt_passport_submit'
        elif 'state' in init_values and self.state == 'cancel':
            return 'saudi_hr_passport_management.mt_internal_passport_process_cancel'
#         if 'stage_id' in init_values and self.state not in ['confirm', 'approve', 'submit', 'cancel']:
#             return 'saudi_hr_passport_management.mt_internal_passport_process_stage'
        return super(IntPassportProcess, self)._track_subtype(init_values)

    @api.onchange('date_to')
    def onchange_expiration_date(self):
        """
            set the value onchange of expiration_date
        """
        if self.date_from and self.date_to and self.date_from >= self.date_to:
            raise UserError(_('Invalid Date! Please enter valid duration from and to date!'))

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
            set the value onchange of employee_id
        """
        if not self.employee_id:
            self.passport_no = False
        else:
            self.passport_no = False
            doc_type = self.env['res.document.type'].search([('code', '=', 'pno')])
            for doc in self.employee_id.document_ids:
                if doc.type_id == doc_type[0]:
                    self.passport_no = doc.doc_number

    @api.model
    def create(self, values):
        """Overwrite the create method to add the passport process"""
        if values.get('employee_id'):
            employee = self.env['hr.employee'].browse(values.get('employee_id'))
            doc_type = self.env['res.document.type'].search([('code', '=', 'pno')])
            passport_no = False
            for doc in employee.document_ids:
                if doc.type_id == doc_type[0]:
                    passport_no = doc.doc_number
            values.update({'passport_no': passport_no})
        return super(IntPassportProcess, self).create(values)

    def write(self, values):
        """Overwrite the write method to change value of the passport process"""
        if values.get('employee_id'):
            employee = self.env['hr.employee'].browse(values.get('employee_id'))
            doc_type = self.env['res.document.type'].search([('code', '=', 'pno')])
            passport_no = False
            for doc in employee.document_ids:
                if doc.type_id == doc_type[0]:
                    passport_no = doc.doc_number
            values.update({'passport_no': passport_no})
        return super(IntPassportProcess, self).write(values)

    def act_confirm(self):
        """
            set the confirm state
        """
        self.ensure_one()
        document_id = self.env['res.documents'].search([('employee_id', '=', self.employee_id.id),
                                                        ('doc_number', '=', self.passport_no),
                                                        ('status', '=', 'office')])
        if not document_id:
            raise UserError(_('Passport is not registered by this employee , please contact his HR manger!'))
        if self.employee_id.user_id:
            self.message_subscribe(partner_ids=[self.employee_id.user_id.partner_id.id])
        self.state = 'confirm'

    def act_approve(self):
        """
            set the approve state
        """
        self.ensure_one()
        document_ids = self.env['res.documents'].search([('employee_id', '=', self.employee_id.id),
                                                         ('doc_number', '=', self.passport_no)])
        for document_id in document_ids:
            document_id.status = 'gr_user'
        self.write({'state': 'approve',
                    'approve_by': self.env.user.id,
                    'approve_date': time.strftime('%Y-%m-%d %H:%M:%S')})
        self.message_subscribe(partner_ids=[self.env.user.partner_id.id])

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

    def act_submit(self):
        """
            set the submit state
        """
        self.ensure_one()
        register_ids = self.env['emp.passport.register'].search([('employee_id', '=', self.employee_id.id),
                                                                 ('passport_no', '=', self.passport_no)])
        document_ids = self.env['res.documents'].search([('employee_id', '=', self.employee_id.id),
                                                         ('doc_number', '=', self.passport_no)])
        for register_id in register_ids:
            body = "Passport Is Relocate from office %s Locker Number %s to Locker Number %s" % (register_id.store_branch_id.name, register_id.loker, self.loker)
            register_id.message_post(message_type="email", subtype='mail.mt_comment', body=_(body))
            register_id.loker = self.loker
        for document_id in document_ids:
            document_id.write({'position': self.loker,
                               'status': 'office'})
        try:
            template_id = self.env.ref('saudi_hr_passport_management.passport_submission_email')
        except ValueError:
            template_id = False
        if template_id:
            mail_mail_record = template_id.send_mail(self.id, force_send=True, raise_exception=False)
            mail_mail_record = self.env['mail.mail'].browse(mail_mail_record)
            mail_msg_record = self.env['mail.message'].browse(mail_mail_record.mail_message_id.id)
            mail_msg_record.write({'partner_ids': [(6, 0, [self.approve_by.partner_id.id])]})  # 'notification_ids': [(0, 0, [self.approve_by.partner_id.id])]})
        self.write({'state': 'submit',
                    'submit_date': time.strftime('%Y-%m-%d')})
