# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import api, fields, models, _
from datetime import datetime
from odoo.exceptions import UserError


class HrSponsorshipTransfer(models.Model):
    _name = 'hr.sponsorship.transfer'
    _inherit = ['mail.thread']
    _description = "Employee Sponsorship Transfer"

    # Fields Hr Sponsorship Transfer
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=lambda self: self.env['hr.employee'].get_employee())
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Waiting for Approval'),
                              ('approved', 'Approved'),
                              ('refused', 'Refused'),
                              ('cancel', 'Cancel')], string='Status', default='draft', track_visibility='onchange')
    recruiter_id = fields.Many2one('res.users', string='Recruiter', default=lambda self: self.env.uid)
    approved_date = fields.Datetime(string='Approved on', readonly=True)
    approved_by = fields.Many2one('res.users', string='Approved by', readonly=True)
    refused_by = fields.Many2one('res.users', string='Refused by', readonly=True)
    refused_date = fields.Datetime(string='Refused on', readonly=True)
    description = fields.Text(string='Description')
    handled_by = fields.Many2one('hr.employee', string='Handled By')
    company_id = fields.Many2one('res.company', string="Company", required=True, default=lambda self: self.env.user.company_id)

    def unlink(self):
        """
            To remove the record, which is not in 'confirm', 'approved' and 'refused' states
        """
        for objects in self:
            if objects.state in ['confirm', 'approved', 'refused']:
                raise UserError(_('You cannot remove the record which is in %s state!') % objects.state)
        return super(HrSponsorshipTransfer, self).unlink()

    def name_get(self):
        """
            to use retrieving the name
        """
        result = []
        for employee in self:
            name = employee.employee_id.name or ''
            result.append((employee.id, name))
        return result

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        """
            onchange the value based on selected employee,
            company
        """
        self.company_id = self.employee_id.company_id.id

    def _add_followers(self):
        """
            Add employee, recruiter and handled_by in followers
        """
        gr_groups_config_ids = self.env['hr.groups.configuration'].search([('branch_id', '=', self.employee_id.branch_id.id), ('gr_ids', '!=', False)])
        partner_ids = gr_groups_config_ids and [employee.user_id.partner_id.id for employee in gr_groups_config_ids.gr_ids if employee.user_id] or []
        partner_ids.append(self.recruiter_id.partner_id.id)
        if self.employee_id.user_id:
            partner_ids.append(self.employee_id.user_id.partner_id.id)
        if self.handled_by:
            partner_ids.append(self.handled_by.user_id.partner_id.id)
        self.message_subscribe(partner_ids=partner_ids)

    def sponsorship_confirm(self):
        """
            sent the status of generating his/her sponsorship in 'confirm' state
        """
        self.ensure_one()
        self._add_followers()
        self.state = 'confirm'

    def sponsorship_approved(self):
        """
            sent the status of generating his/her sponsorship in 'approved' state
        """
        self.ensure_one()
        self._add_followers()
        self.write({'state': 'approved',
                    'approved_by': self.env.uid,
                    'approved_date': datetime.today()})

    def sponsorship_refused(self):
        """
            sent the status of generating his/her sponsorship in 'refused' state
        """
        self.ensure_one()
        self.write({'state': 'refused',
                    'refused_by': self.env.uid,
                    'refused_date': datetime.today()})

    def sponsorship_cancel(self):
        """
            sent the status of generating his/her sponsorship in 'cancel' state
        """
        self.ensure_one()
        self.state = 'cancel'

    def set_to_draft(self):
        """
            sent the status of generating his/her sponsorship in 'draft' state
        """
        self.ensure_one()
        self.write({'state': 'draft',
                    'refused_by': False,
                    'refused_date': False,
                    'approved_by': False,
                    'approved_date': False})

    def send_required_document_mail(self):
        """
            This function send mail to employee for his/her required documents for sponsorship transfer
        """
        self.ensure_one()
        try:
            template_id = self.env.ref('saudi_hr_sponsorship_transfer.email_template_required_document')
        except ValueError:
            template_id = False
        if template_id:
            template_id.send_mail(self.id, force_send=True)
