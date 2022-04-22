# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models, api, _


class MultiReports(models.Model):
    _name = 'multi.reports'
    _inherit = ['mail.thread']
    _description = "Multi Reports"
    _order = 'id desc'

    @api.model
    def _employee_get(self):
        employee_id = self.env['hr.employee'].search([('user_id', '=', self.env.uid)], limit=1)
        if employee_id:
            return employee_id[0]
        return False

    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, default=_employee_get)
    manager_id = fields.Many2one('hr.employee', 'Authorised by')
    date = fields.Date('Date', required=True, default=fields.Date.today())
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Submitted'), ('inprogress', 'In Progress'), ('refuse', 'Refused'), ('approve', 'Approved')], default='draft')
    report_type = fields.Selection([('bank_loan', 'Bank Loan Transfer (Male) '),
                                    ('bank_loan_female', 'Bank Loan Transfer (Female) '),
                                    ('bankopen_account', 'Bank Open Account (Male)'),
                                    ('bankopen_account_female', 'Bank Open Account (Female)'),
                                    ('certi_approval', 'Ratification Certificate'),
                                    ('family_iqama', 'Family Iqama'),
                                    ('mroor_report', 'Mroor Report'),
                                    ('house_allowance', 'Housing Allowance'),
                                    ('saudi_hr_letters_whomeconcern', ' To Whom Concern (English) '),
                                    ('towhom_concern', ' To Whom Concern (Male)'),
                                    ('towhom_concern_female', 'To Whom Concern (Female)'),
                                    ('stamping_certificate', 'Stamping Certificate  (Male)'),
                                    ('stamping_certificate_female', 'Stamping Certificate (Female)'),
                                    ('wifefrom_home_country', 'Wife From  Home Country'),
                                    ('walid_school', 'Valid School'),
                                    ('saudibritish_bankloan', 'Saudi British Bankloan Transfer'),
                                    ('saudi_hr_letters_transport', 'Transport Report')], required=True, string='Report Type')
    approved_date = fields.Datetime('Approved Date', readonly=True, track_visibility='onchange', copy=False)
    approved_by = fields.Many2one('res.users', 'Approved by', readonly=True, track_visibility='onchange', copy=False)
    refused_date = fields.Datetime('Refused Date', readonly=True, track_visibility='onchange', copy=False)
    refused_by = fields.Many2one('res.users', 'Refused by', readonly=True, track_visibility='onchange', copy=False)
    handled_by_id = fields.Many2one('hr.employee', 'Handled by', default=_employee_get)
    description = fields.Text('Description', required=True)

    @api.model
    def create(self, values):
        res = super(MultiReports, self).create(values)
        partner = [self.env.user.partner_id.id]
        if res.employee_id.sudo().parent_id.user_id:
            partner.append(res.employee_id.sudo().parent_id.user_id.partner_id.id)
        if res.employee_id.user_id:
            partner.append(res.employee_id.user_id.partner_id.id)
        res.message_subscribe(partner_ids=partner)
        return res

    def write(self, values):
        partner = []
        if values.get('employee_id'):
            employee = self.env['hr.employee'].browse(values.get('employee_id'))
            if employee.user_id:
                partner.append(employee.user_id.partner_id.id)
            if employee.sudo().parent_id.user_id:
                partner.append(employee.sudo().parent_id.user_id.partner_id.id)
        self.message_subscribe(partner_ids=partner)
        return super(MultiReports, self).write(values)

    def letter_confirm(self):
        self.ensure_one()
        hr_groups_config_ids = self.env['hr.groups.configuration'].sudo().search([('branch_id', '=', self.employee_id.branch_id.id or False), ('hr_ids', '!=', False)], limit=1)
        if hr_groups_config_ids:
            partner_ids = [item.user_id.partner_id.id for item in hr_groups_config_ids.hr_ids if item.user_id]
            self.message_subscribe(partner_ids=partner_ids)
        self.state = 'confirm'
        self.message_post(message_type="email", subtype='mail.mt_comment', body=_('Request Submitted.'))

    def letter_inprogress(self):
        self.ensure_one()
        self.state = 'inprogress'
        self.message_post(message_type="email", subtype='mail.mt_comment', body=_('Letter request is in progress.'))

    def letter_approve(self):
        self.ensure_one()
        self.write({'state': 'approve',
                    'approved_by': self.env.uid,
                    'approved_date': fields.Datetime.now()})
        self.message_post(message_type="email", subtype='mail.mt_comment', body=_('Letter request is approved.'))

    def letter_refuse(self):
        self.ensure_one()
        self.write({'state': 'refuse',
                    'refused_by':self.env.uid,
                    'refused_date': fields.Datetime.now()})
        self.message_post(message_type="email", subtype='mail.mt_comment', body=_('Letter request is refused.'))

    def set_draft(self):
        self.ensure_one()
        self.state = 'draft'

    def name_get(self):
        res = []
        for letter in self:
            name = ''.join([letter.employee_id.name or '', ' Letter'])
            res.append((letter.id, name))
        return res

    def print_report(self):
        self.ensure_one()
        data = self.read()[0]
        if data['report_type'] == 'bank_loan':
            return self.env.ref('saudi_hr_letters.bankloan_transfer').report_action(self, data=data)
        elif data['report_type'] == 'bank_loan_female':
            return self.env.ref('saudi_hr_letters.bankloan_transfer_female').report_action(self, data=data)
        elif data['report_type'] == 'bankopen_account':
            return self.env.ref('saudi_hr_letters.bankopen_account').report_action(self, data=data)
        elif data['report_type'] == 'bankopen_account_female':
            return self.env.ref('saudi_hr_letters.bankopen_account_female').report_action(self, data=data)
        elif data['report_type'] == 'certi_approval':
            return self.env.ref('saudi_hr_letters.certificate_ofapprove').report_action(self, data=data)
        elif data['report_type'] == 'family_iqama':
            return self.env.ref('saudi_hr_letters.family_iqama').report_action(self, data=data)
        elif data['report_type'] == 'mroor_report':
            return self.env.ref('saudi_hr_letters.mroor_report').report_action(self, data=data)
        elif data['report_type'] == 'house_allowance':
            return self.env.ref('saudi_hr_letters.house_allowence').report_action(self, data=data)
        elif data['report_type'] == 'saudi_hr_letters_whomeconcern':
            return self.env.ref('saudi_hr_letters.saudi_hr_letters_whomeconcern').report_action(self, data=data)
        elif data['report_type'] == 'towhom_concern':
            return self.env.ref('saudi_hr_letters.towhome_concern').report_action(self, data=data)
        elif data['report_type'] == 'towhom_concern_female':
            return self.env.ref('saudi_hr_letters.towhom_concern_female').report_action(self, data=data)
        elif data['report_type'] == 'stamping_certificate':
            return self.env.ref('saudi_hr_letters.stamping_certificate').report_action(self, data=data)
        elif data['report_type'] == 'stamping_certificate_female':
            return self.env.ref('saudi_hr_letters.stamping_certificate_female').report_action(self, data=data)
        elif data['report_type'] == 'wifefrom_home_country':
            return self.env.ref('saudi_hr_letters.wifefrom_home_country').report_action(self, data=data)
        elif data['report_type'] == 'walid_school':
            return self.env.ref('saudi_hr_letters.walid_school').report_action(self, data=data)
        elif data['report_type'] == 'saudibritish_bankloan':
            return self.env.ref('saudi_hr_letters.saudibritish_bankloan').report_action(self, data=data)
        elif data['report_type'] == 'saudi_hr_letters_transport':
            return self.env.ref('saudi_hr_letters.saudi_hr_letters_transport').report_action(self, data=data)
