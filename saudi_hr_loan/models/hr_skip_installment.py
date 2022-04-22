# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
from odoo.exceptions import ValidationError, UserError
from dateutil import relativedelta


class HrSkipInstallment(models.Model):
    _name = 'hr.skip.installment'
    _inherit = ['mail.thread']
    _description = "Employee Loan Skip Installment"

    name = fields.Char('Reason to Skip',required=True, track_visibility='onchange')
    loan_id = fields.Many2one('hr.loan','Loan',domain="[('employee_id','=',employee_id), ('state','=', 'approve')]",required=True, track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee','Employee',required=True, default=lambda self: self.env['hr.employee'].get_employee(), track_visibility='onchange')
    date = fields.Date('Date', required=True, default=fields.Date.today, track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('open', 'Waiting Approval'),
                              ('refuse', 'Refused'),
                              ('approve', 'Approved'),
                              ('cancel', 'Cancelled')], string="Status",required=True, default='draft', track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=False, default=lambda self: self.env.user.company_id)
    approved_by = fields.Many2one('res.users', 'Approved by', readonly=True, copy=False)
    refused_by = fields.Many2one('res.users', 'Refused by', readonly=True, copy=False)
    approved_date = fields.Datetime(string='Approved on', readonly=True, copy=False)
    refused_date = fields.Datetime(string='Refused on', readonly=True, copy=False)

    @api.constrains('date', 'employee_id', 'loan_id', 'company_id')
    def _check_date(self):
        employee_ids = self.search([('id', '!=', self.id), ('employee_id', '=', self.employee_id.id), ('loan_id', '=', self.loan_id.id), ('company_id','=',self.company_id.id)])
        current_month = datetime.now().month
        for employee_id in employee_ids:
            skip_date = datetime.strptime(str(employee_id.date), DEFAULT_SERVER_DATE_FORMAT)
            if int(current_month) == int(skip_date.month):
                raise ValidationError(_('Record already exist for this month!'))

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
            onchange the value based on selected employee
            company
        """
        if self.employee_id:
            self.company_id = self.employee_id.company_id.id

    def confirm_request(self):
        """
            sent the status of skip installment request in Confirm state
        """
        self.ensure_one()
        loan_operation_ids = self.env['hr.loan.operation'].search([('loan_id', '=', self.loan_id.id), ('state', 'not in', ['refuse', 'done']), ('loan_operation_type', '=', 'pay_loan_amount')])
        if self.loan_id.is_loan_freeze:
            raise UserError(_('Please Unfreeze Your Loan.'))
        if any(self.date.month == loan_operation.date.month and loan_operation.loan_operation_type == 'pay_loan_amount' for loan_operation in loan_operation_ids):
            raise UserError(_('Please Cancel Your Pay loan Request'))
        self.state = 'confirm'

    def waiting_approval_request(self):
        """
            sent the status of skip installment request in Open state
        """
        self.ensure_one()
        self.state = 'open'

    def approve_request(self):
        """
            sent the status of skip installment request in confirm state
        """
        self.ensure_one()
        if self.loan_id.state == 'approve':
            self.approved_by = self.env.uid
            self.approved_date = datetime.today()
            end_date = self.loan_id.due_date + relativedelta(months=+1)
            self.loan_id.write({'due_date': end_date})
            self.state = 'approve'
        else:
            raise ValidationError(_('You should approve related loan first'))

    def refuse_request(self):
        """
            sent the status of skip installment request in refuse state
        """
        self.ensure_one()
        self.refused_by = self.env.uid
        self.refused_date = fields.Date.today()
        if self.state == 'confirm':
            due_date = datetime.strptime(str(self.loan_id.due_date), DEFAULT_SERVER_DATE_FORMAT)
            end_date = due_date + relativedelta(months=-1)
            self.loan_id.write({'due_date': end_date})
        self.state = 'refuse'

    def set_to_draft(self):
        """
            sent the status of skip installment request in Set to Draft state
        """
        self.ensure_one()
        self.approved_by = False
        self.refused_by = False
        self.approved_date = False
        self.refused_date = False
        self.state = 'draft'

    def set_to_cancel(self):
        """
            sent the status of skip installment request in cancel state
        """
        self.ensure_one()
        self.state = 'cancel'

    def unlink(self):
        """
            To remove the record, which is not in 'draft' and 'cancel' states
        """
        for rec in self:
            if rec.state not in ['draft', 'cancel']:
                raise ValidationError(_('You cannot delete a request to skip installment which is in %s state.')%(rec.state))
        return super(HrSkipInstallment, self).unlink()
