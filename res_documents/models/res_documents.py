# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from datetime import datetime
from dateutil.relativedelta import relativedelta
from odoo import models, fields, api, _


class ResDocumentType(models.Model):
    _name = 'res.document.type'
    _description = 'Document Type'

    code = fields.Char('Code', required=True)
    name = fields.Char('Name', required=True)

    _sql_constraints = [
        ('code', 'unique(code)', 'Code must be unique per Document!'),
    ]


class ResDocuments(models.Model):
    _name = 'res.documents'
    _inherit = ['mail.thread']
    _description = 'Res Documents'

#     applicant_id =  fields.Many2one('hr.applicant', 'Applicant')
    type_id = fields.Many2one('res.document.type', 'Type')
    doc_number = fields.Char('Number', size=128)
    issue_place = fields.Char('Place of Issue', size=128)
    issue_date = fields.Date('Date of Issue', track_visibility='onchange')
    expiry_date = fields.Date('Date of Expiry', track_visibility='onchange')
    notes = fields.Text('Notes')
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, default=lambda self: self.env['hr.employee'].get_employee())
    manager_id = fields.Many2one('hr.employee', string='Manager', readonly=True, track_visibility='onchange')
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.user.company_id)
    is_visible_on_report = fields.Boolean('Visible on Report')
    profession = fields.Char('Profession', size=32)
    hijri_expiry_date = fields.Char('Date of Expiry(Hijri)')
    position = fields.Char('Position')
    attachment_ids = fields.Many2many('ir.attachment', string='Attachments')
    state = fields.Selection([
            ('draft', 'Draft'),
            ('confirm', 'Confirmed'),
            ('issue', 'Issued'),
            ('refuse', 'Refused'),
            ('renew', 'Renew'),
            ('expiry', 'Expiry')], string='Status', readonly=True, copy=False, default='draft', track_visibility='onchange')

    # create or write method add for channel_id but notification not send
    @api.model
    def create(self, values):
        """
            Create a new record
            :return: Newly created record ID
        """
        res = super(ResDocuments, self).create(values)
        partner = [self.env.user.partner_id.id]
        if res.manager_id.user_id:
            partner.append(res.manager_id.user_id.partner_id.id)
        if res.employee_id.user_id:
            partner.append(res.employee_id.user_id.partner_id.id)
        # channel_id = self.env.ref('saudi_hr.manager_channel').id
        # res.message_subscribe(partner_ids=partner, channel_ids=[channel_id])
        res.message_subscribe(partner_ids=partner)
        return res

    def write(self, values):
        """
            Update an existing record.
            :param values:
            :return: Current update record ID
        """
        partner = []
        if values.get('manager_id'):
            employee = self.env['hr.employee'].browse(values.get('manager_id'))
            if employee.user_id:
                partner.append(employee.user_id.partner_id.id)
        if values.get('employee_id'):
            employee = self.env['hr.employee'].browse(values.get('employee_id'))
            if employee.user_id:
                partner.append(employee.user_id.partner_id.id)
        # channel_id=self.env.ref('saudi_hr.manager_channel').id
        self.message_subscribe(partner_ids=partner)
        return super(ResDocuments, self).write(values)

    @api.onchange('employee_id')
    def onchange_employee(self):
        for rec in self:
            if rec.employee_id:
                rec.position = rec.employee_id.job_title
                rec.profession = rec.employee_id.department_id.name

    @api.depends('employee_id', 'type_id', 'doc_number')
    def name_get(self):
        """
            Return name of document with employee name, document type & document number.
        """
        result = []
        for doc in self:
            name = doc.employee_id.name + ' ' + doc.type_id.name + ' ' + doc.doc_number
            result.append((doc.id, name))
        return result

    @api.model
    def run_scheduler(self):
        """
            cron job for automatically sent an email,
            sent notification, your document expired after 1 month.
        """
        today = datetime.now().date()
        for document in self.search([('state', '=', 'issue')]):
            if document.expiry_date and document.employee_id.user_id:
                notification_date = (document.expiry_date - relativedelta(months=+1))
                if today == notification_date:
                    try:
                        template_id = self.env.ref('res_documents.email_template_res_documents_notify')
                    except ValueError:
                        template_id = False
                    email_to = ''
                    user = document.employee_id.user_id
                    if user.email:
                        email_to = email_to and email_to + ',' + user.email or email_to + user.email
                    template_id.write({'email_to': email_to, 'reply_to': email_to, 'auto_delete': False})
                    template_id.send_mail(document.id, force_send=True)
            if document.expiry_date and document.expiry_date == today:
                document.state = 'expiry'
                try:
                    template_id = self.env.ref('res_documents.email_template_res_document_expire')
                except ValueError:
                    template_id = False
                if template_id:
                    template_id.send_mail(document.id, force_send=True, raise_exception=False, email_values=None)
        return True

    def action_send_mail(self):
        """
            send mail using mail template
        """
        try:
            template_id = self.env.ref('res_documents.email_template_res_document')
        except ValueError:
            template_id = False
        if template_id:
            template_id.send_mail(self.id, force_send=True, raise_exception=False, email_values=None)
        return True

    def set_draft(self):
        """
            sent the status of generating Document record in draft state
        """
        self.state = 'draft'

    def _add_followers(self):
        """
            Add employee and manager in followers
        """
        partner_ids = []
        if self.employee_id.user_id:
            partner_ids.append(self.employee_id.user_id.partner_id.id)
        if self.manager_id.user_id:
            partner_ids.append(self.manager_id.user_id.partner_id.id)
        self.message_subscribe(partner_ids=partner_ids)

    def document_submit(self):
        """
            sent the status of generating Document record in confirm state
        """
        self._add_followers()
        self.state = 'confirm'

    @api.model
    def get_employee(self):
        """
            Get Employee record depends on current user.
            return: employee_ids
        """
        employee_ids = self.env['hr.employee'].search([('user_id', '=', self.env.uid)]).ids
        return employee_ids[0] if employee_ids else False

    def document_issue(self):
        """
            sent the status of generating Document record in issue state and get issue date
        """
        self.write({'manager_id': self.get_employee(),
                    'state': 'issue',
                    'issue_date': datetime.today()})
        self._add_followers()
        self.action_send_mail()

    def document_refuse(self):
        """
            sent the status of generating Document record in refuse state
        """
        self.state = 'refuse'

    def document_renew(self):
        """
            sent the status of generating Document record is renew
        """
        self.write({'state': 'renew',
                    'expiry_date': False,
                    'issue_date': False})


class HrEmployee(models.Model):

    _inherit = 'hr.employee'

    document_ids = fields.One2many('res.documents', 'employee_id', 'Document')
    documents_count = fields.Integer(string='Documents', compute='_compute_documents')

    def _compute_documents(self):
        """
            count total document related employee
        """
        for employee in self:
            documents = self.env['res.documents'].search([('employee_id', '=', employee.id)])
            employee.documents_count = len(documents) if documents else 0

    def action_documents(self):
        """
            Show employee Documents
        """
        self.ensure_one()
        tree_view = self.env.ref('res_documents.res_documents_view_tree')
        form_view = self.env.ref('res_documents.res_documents_view_form')
        return {'type': 'ir.actions.act_window',
                'name': _('Documents'),
                'res_model': 'res.documents',
                'view_mode': 'tree',
                'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
                'domain': [('employee_id', '=', self.id)],
                'res_id': self.document_ids.ids and self.document_ids.ids[0] or False,
                'context': self.env.context,
                }
