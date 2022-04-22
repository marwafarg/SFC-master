# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

import time

from lxml import etree
from datetime import timedelta, datetime, date

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from dateutil.relativedelta import relativedelta



class HrLoan(models.Model):
    _name = 'hr.loan'
    _description = "Employee Loan"
    _inherit = ['mail.thread']

    @api.depends('loan_amount', 'installment_lines', 'installment_lines.amount')
    def _calculate_amounts(self):
        for rec in self:
            paid_amount = 0.0
            for installment in rec.installment_lines:
                paid_amount += installment.amount
            rec.amount_paid = paid_amount
            rec.amount_to_pay = rec.loan_amount - paid_amount

    @api.depends('start_date', 'duration')
    def _calculate_due_date(self):
        for rec in self:
            rec.due_date = False
            if rec.start_date:
                rec.due_date = rec.start_date + timedelta(rec.duration * 365 / 12)

    name = fields.Char('Reference', size=64, required=True, default=_('New'))
    request_date = fields.Date('Loan Request Date', required=True, default=fields.Date.today)
    start_date = fields.Date('Loan Payment Start Date', track_visibility='onchange')
    due_date = fields.Date('Loan Payment End Date', track_visibility='onchange', compute='_calculate_due_date', store=True)
    loan_amount = fields.Float('Loan Amount', digits='Account', required=True, track_visibility='onchange')
    duration = fields.Integer('Payment Duration(Months)', track_visibility='onchange', copy=False)
    deduction_amount = fields.Float('Deduction Amount', digits='Account', copy=False)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True, default=lambda self: self.env['hr.employee'].get_employee())
    # branch_id = fields.Many2one('res.branch', 'Office', readonly=True, related='employee_id.branch_id', store=True)
    loan_type = fields.Selection([('salary', 'Loan Against Salary'), ('service', 'Loan Against Service')], string="Loan Type", required=True, default='salary')
    description = fields.Text('Purpose For Loan', required=True)
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id', store=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirm'),
                              ('open', 'Waiting Approval'),
                              ('refuse', 'Refused'),
                              ('approve', 'Approved'),
                              ('done', 'Done'),
                              ('cancel', 'Cancelled')], string="Status", required=True, default='draft', track_visibility='onchange')
    loan_state = fields.Selection([('freeze', 'Freeze'), ('unfreeze', 'Unfreeze')], string="Loan Status", default='unfreeze')
    emi_based_on = fields.Selection([('duration', 'By Duration'), ('amount', 'By Amount')], string='EMI based on',
                                    required=True, default='duration', track_visibility='onchange')
    percentage_of_gross = fields.Float('Percentage of Gross', digits='Account')
    installment_lines = fields.One2many('installment.line', 'loan_id', 'Installments')
    amount_paid = fields.Float('Amount Paid', compute='_calculate_amounts', digits='Account',
                               track_visibility='onchange')
    amount_to_pay = fields.Float('Amount to Pay', compute='_calculate_amounts', digits='Account',
                                 track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', required=True, readonly=False,
                                 default=lambda self: self.env.company)
    partner_id = fields.Many2one('res.partner', string='partner')
    approved_by = fields.Many2one('res.users', 'Approved by', readonly=True, copy=False)
    refused_by = fields.Many2one('res.users', 'Refused by', readonly=True, copy=False)
    approved_date = fields.Datetime(string='Approved on', readonly=True, copy=False)
    refused_date = fields.Datetime(string='Refused on', readonly=True, copy=False)
    is_loan_freeze = fields.Boolean()
    loan_operation_ids = fields.Many2many('hr.loan.operation', compute='_get_loan_operations')
    skip_installment_count = fields.Integer(compute='_compute_skip_installments')
    increase_amount_count = fields.Integer(compute='_compute_increase_loan_amount')
    pay_loan_count = fields.Integer(compute='_compute_pay_loan_amount')
    treasury_account_id = fields.Many2one('account.account', string="Treasury Account")
    emp_account_id = fields.Many2one('account.account', string="Employee Loan Account")
    journal_id = fields.Many2one('account.journal', 'Journal',
                                 default=lambda self: self.env['account.journal'].search([('type', '=', 'general')],
                                                                                         limit=1))
    analytic_account_id = fields.Many2one('account.analytic.account', string='Analytic Account', index=True, track_visibility='onchange')
    analytic_tag_ids = fields.Many2many('account.analytic.tag', string='Analytic Tags', track_visibility='onchange')
    move_id = fields.Many2one('account.move', 'Accounting Entry', readonly=True, copy=False)

    journal_entry_count=fields.Integer(compute='_journal_entry_count')


    @api.model
    def default_get(self, fields):
        rec = super(HrLoan, self).default_get(fields)
        if 'company_id' in rec:
            rec['emp_account_id'] = self.env['res.company'].browse(rec['company_id']).loan_account_id.id
        return rec


    @api.depends('move_id')
    def _journal_entry_count(self):
        for rec in self:
            rec.journal_entry_count=len(rec.move_id)


    def action_view_journal_entry(self):
        journal_entry=self.move_id.id
        return {
            'name': _("Journal Entry"),
            'view_mode': 'tree,form',
            'views': False,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain':[('id','=',journal_entry)],
            'nodestroy': True,
            'context': {'create':False}
        }


    @api.model
    def fields_view_get(self, view_id=None, view_type='form',
                        toolbar=False, submenu=False):
        """
            Override method for hide create button
        """
        res = super(HrLoan, self).fields_view_get(
            view_id=view_id, view_type=view_type,
            toolbar=toolbar, submenu=submenu)
        if self.env.user.employee_id and not self.user_has_groups('saudi_hr_loan.group_employee_can_request_loan')\
            and not self.user_has_groups('hr.group_hr_user') and not self.user_has_groups('saudi_hr.group_line_manager'):
            root = etree.fromstring(res['arch'])
            root.set('create', 'false')
            root.set('edit', 'false')
            res['arch'] = etree.tostring(root)
        return res

    def _get_loan_operations(self):
        self.loan_operation_ids = self.env['hr.loan.operation'].search([('employee_id', '=', self.employee_id.id)])

    @api.depends('loan_operation_ids')
    def _compute_skip_installments(self):
        if self.loan_operation_ids:
            loan_operation_ids = self.mapped('loan_operation_ids').filtered(lambda operation: operation.loan_operation_type == 'skip_installment')
            self.skip_installment_count = len(loan_operation_ids)

    @api.depends('loan_operation_ids')
    def _compute_increase_loan_amount(self):
        if self.loan_operation_ids:
            loan_operation_ids = self.mapped('loan_operation_ids').filtered(lambda operation: operation.loan_operation_type == 'amount')
            self.increase_amount_count = len(loan_operation_ids)

    @api.depends('loan_operation_ids')
    def _compute_pay_loan_amount(self):
        if self.loan_operation_ids:
            loan_operation_ids = self.mapped('loan_operation_ids').filtered(lambda operation: operation.loan_operation_type == 'pay_loan_amount')
            self.pay_loan_count = len(loan_operation_ids)

    @api.onchange('employee_id')
    def onchange_employee(self):
        """
            onchange the value based on selected employee
            department, job and company
        """
        self.department_id = False
        if self.employee_id:
            self.department_id = self.employee_id.department_id.id
            self.company_id = self.employee_id.company_id.id
            contract = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'open')], limit=1)
            self.analytic_account_id = contract and contract.analytic_account_id.id or False
            self.analytic_tag_ids = contract and [(6, 0, contract.analytic_tag_ids.ids)] or False
            self.partner_id=self.employee_id.address_home_id

    @api.model
    def create(self, values):
        if values.get('employee_id'):
            loan_ids = self.env['hr.loan'].search([('state', 'not in', ['done', 'cancel']),
                                                   ('employee_id', '=', values['employee_id'])])
            if loan_ids:
                raise UserError(_('This employee loan is already in Process.'))
        if values.get('company_id'):
            values['name'] = self.env['ir.sequence'].with_context(force_company=values['company_id']).next_by_code(
                'hr_loan') or _('New')
        else:
            values['name'] = self.env['ir.sequence'].next_by_code('hr_loan') or _('New')
        return super(HrLoan, self).create(values)

    def write(self, values):
        if values.get('employee_id'):
            loan_ids = self.env['hr.loan'].search([('state', 'not in', ['done', 'cancel']),
                                                   ('employee_id', '=', values['employee_id'])])
            if loan_ids:
                raise UserError(_('This employee loan is already in Process.'))
        return super(HrLoan, self).write(values)

    def make_calculation(self):
        """
            check the loan amount, loan interest, payment duration and based on it calculate deduction amount
        """
        if not self.loan_amount or self.loan_amount < 0:
            raise UserError(_("Please enter proper value for Loan Amount & Loan Interest"))
        loan_limit=self.employee_id.contract_id.total_salary * self.company_id.maximum_amount_loan/100
        if self.loan_amount > loan_limit :
            raise UserError(_("Please enter proper value for Loan Amount in limit %s")%(('{:.2f}').format(loan_limit)))
        if self.emi_based_on == 'duration':
            if not self.duration or self.duration < 0:
                raise UserError(_("Please enter proper value for Payment Duration"))
            self.deduction_amount = self.loan_amount / self.duration
        elif self.emi_based_on == 'amount':
            if not self.deduction_amount or self.deduction_amount < 0:
                raise UserError(_("Please enter proper value for Deduction Amount"))
            self.duration = self.loan_amount / self.deduction_amount
        # self.compute_installment()

    def compute_installment(self):
        """This automatically create the installment the employee need to pay to
        company based on payment start date and the no of installments.
            """
        for loan in self:
            loan.installment_lines.unlink()
            date_start = datetime.strptime(str(loan.start_date), '%Y-%m-%d')
            amount = loan.deduction_amount
            for i in range(1, loan.duration + 1):
                self.env['installment.line'].create({
                    'date': date_start,
                    'amount': amount,
                    'employee_id': loan.employee_id.id,
                    'loan_id': loan.id})
                date_start = date_start + relativedelta(months=1)
        return True



    def confirm_loan(self):
        """
            sent the status of generating his/her loan in Confirm state
        """
        self.ensure_one()
        self.make_calculation()
        self.state = 'confirm'

    def waiting_approval_loan(self):
        """
            sent the status of generating his/her loan in Open state
        """
        self.ensure_one()
        self.state = 'open'

    def approve_loan(self):
        """
            sent the status of generating his/her loan in Approve state
        """
        self.ensure_one()
        #self.start_date = date.today()
        #self.due_date = self.start_date + timedelta(self.duration * 365 / 12)
        self.approved_by = self.env.uid
        self.approved_date = datetime.today()
        timenow = time.strftime('%Y-%m-%d')
        for loan in self:
            amount = loan.loan_amount
            loan_name = loan.employee_id.name
            reference = loan.name
            journal_id = loan.journal_id.id
            debit_account_id = loan.emp_account_id.id
            credit_account_id = loan.treasury_account_id.id
            analytic_account_id = loan.analytic_account_id.id
            debit_vals = {
                'name': reference,
                'account_id': debit_account_id,
                'analytic_account_id': analytic_account_id or False,
                'analytic_tag_ids': [(6, 0, loan.analytic_tag_ids.ids)] or False,
                'partner_id': loan.partner_id.id or False,
                'journal_id': journal_id,
                'date': timenow,
                'debit': amount > 0.0 and amount or 0.0,
                'credit': amount < 0.0 and -amount or 0.0,
            }
            credit_vals = {
                'name': reference,
                'account_id': credit_account_id,
                'analytic_account_id': analytic_account_id or False,
                'analytic_tag_ids': [(6, 0, loan.analytic_tag_ids.ids)] or False,
                'journal_id': journal_id,
                'partner_id': loan.partner_id.id or False,
                'date': timenow,
                'debit': amount < 0.0 and -amount or 0.0,
                'credit': amount > 0.0 and amount or 0.0,
            }
            vals = {
                # 'branch_id': loan.branch_id.id or False,
                'ref': reference,
                'journal_id': journal_id,
                'date': timenow,
                'line_ids': [(0, 0, debit_vals), (0, 0, credit_vals)]
            }
            move = self.env['account.move'].create(vals)
            move.post()
            loan.move_id = move
        self.state = 'approve'

    def done_loan(self):
        """
            sent the status of generating his/her loan in Done state
        """
        self.ensure_one()
        self.state = 'done'

    def refuse_loan(self):
        """
            sent the status of generating his/her loan in Refuse state
        """
        self.ensure_one()
        if self.installment_lines:
            raise UserError(_('You can not refuse a loan having any installment!'))
        self.refused_by = self.env.uid
        self.refused_date = datetime.today()
        self.state = 'refuse'

    def set_to_draft(self):
        """
            sent the status of generating his/her loan in Set to Draft state
        """
        self.ensure_one()
        self.approved_by = False
        self.approved_date = False
        self.refused_by = False
        self.refused_date = False
        self.state = 'draft'

    def set_to_cancel(self):
        """
            sent the status of generating his/her loan in Cancel state
        """
        self.ensure_one()
        self.state = 'cancel'

    def is_loan_freeze_button_action(self):
        for rec in self:
            if rec.is_loan_freeze:
                rec['is_loan_freeze'] = False
                rec['loan_state'] = 'unfreeze'
                if date.today() != rec['start_date']:
                    rec['start_date'] = date.today()
            else:
                rec['is_loan_freeze'] = True
                rec['loan_state'] = 'freeze'

    def is_employee_loan_unfreeze(self):
        loan_ids = self.env['hr.loan'].search([('is_loan_freeze', '=', True)])
        for loan in loan_ids:
            if loan.start_date == date.today():
                loan.is_loan_freeze = False
                loan.loan_state = 'unfreeze'

    def action_view_operation_req(self):
        self.ensure_one()
        loan_operation_ids = self.loan_operation_ids.search([('employee_id', '=', self.employee_id.id),
                                                             ('loan_id', '=', self.id)])
        tree_view = self.env.ref('saudi_hr_loan.view_hr_loan_operation_tree')
        form_view = self.env.ref('saudi_hr_loan.view_hr_loan_operation_form')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Loan Operation Request'),
            'res_model': 'hr.loan.operation',
            'view_mode': 'from',
            'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
            'domain': [('id', 'in', loan_operation_ids.ids)],
            #'res_id': loan_operation_ids.ids,
            'context': {'group_by': 'loan_operation_type', 'default_employee_id': self.employee_id.id,
                        'default_loan_id': self.id, 'default_analytic_account_id': self.analytic_account_id.id,
                        'default_analytic_tag_ids': [(6, 0, self.analytic_tag_ids.ids)]},
        }

    def unlink(self):
        """
            To remove the record, which is not in 'draft' and 'cancel' states
        """
        for rec in self:
            if rec.state not in ['draft', 'cancel']:
                raise UserError(_('You cannot delete a loan which is in %s state.') % rec.state)
            return super(HrLoan, self).unlink()


class InstallmentLine(models.Model):
    _name = 'installment.line'
    _description = 'Installment Line'

    loan_id = fields.Many2one('hr.loan', 'Loan', required=True)
    payslip_id = fields.Many2one('hr.payslip', 'Payslip', required=False)
    operation_id = fields.Many2one('hr.loan.operation', 'Operation', required=False)
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True)
    date = fields.Date('Date', required=True)
    amount = fields.Float('Installment Amount', digits='Account', required=True)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    loan_ids = fields.One2many('hr.loan', 'employee_id', 'Loans')
