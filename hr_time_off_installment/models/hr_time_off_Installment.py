# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, api, fields, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime, timedelta

class EmployeeAdvanceSalary(models.Model):
    _inherit = "hr.advance.salary"
    timeoff_installment = fields.Many2one('timeoff.installment')


class InstallmentCalculationMethod(models.Model):
    _name = "installment.calculation.method"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Installment Calculation Method"
    name=fields.Char(required=True,tracking=1)
    user_id = fields.Many2one('res.users', string='User Created', index=True, tracking=True,
                              default=lambda self: self.env.user)
    company_id = fields.Many2one('res.company', string='Company',readonly=True,default=lambda self: self.env.company)
    time_off_debit_id=fields.Many2one('account.account',required=True,tracking=2)
    time_off_credit_id=fields.Many2one('account.account',required=True,tracking=3)
    ticket_debit_id=fields.Many2one('account.account',required=True,tracking=2)
    ticket_credit_id=fields.Many2one('account.account',required=True,tracking=3)
    other_allowances_debit_id=fields.Many2one('account.account',required=True,tracking=2)
    other_allowances_credit_id=fields.Many2one('account.account',required=True,tracking=3)
    other_deductions_debit_id=fields.Many2one('account.account',required=True,tracking=2)
    other_deductions_credit_id=fields.Many2one('account.account',required=True,tracking=3)
    installment_method_ids=fields.Many2many('method.line')

class MethodLine(models.Model):
    _name = "method.line"
    name=fields.Char()
    type=fields.Selection([
        ('Basic','Basic'),
        ('House_Rent_Allowance','House Rent Allowance'),
        ('Transport_Allowance','Transport Allowance')
    ]
    )

class HrLeave(models.Model):
    _inherit = "hr.leave"
    is_paid=fields.Boolean()
    pay_in_advance=fields.Selection([
        ('yes','YES'),
        ('no','NO'),
    ],default='no')
class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"
    is_annual_leave=fields.Boolean()

class HrLeaveAllocation(models.Model):
    _inherit = "hr.leave.allocation"
    _sql_constraints = [
        ('duration_check', "CHECK ()", "The number of days must be greater than 0."),
           ]

class TimeoffInstallment(models.Model):
    _name = "timeoff.installment"
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']
    _description = "Installment Transaction"
    name = fields.Char(string='Reference', required=True, copy=False, readonly=True,index=True, default=lambda self: _('New'),tracking=1)
    date = fields.Date('Date',required=True,readonly=True,states={'draft': [('readonly', False)]})
    employee_id = fields.Many2one('hr.employee', 'Employee', required=True,domain="[('active','=',True)]",readonly=True,states={'draft': [('readonly', False)]})
    department_id = fields.Many2one('hr.department', 'Department',related="employee_id.department_id",store=True)
    job_id = fields.Many2one('hr.job', 'Job Position',related="employee_id.job_id",store=True)
    company_id = fields.Many2one('res.company', string='Company', readonly=True, default=lambda self: self.env.company)
    user_id = fields.Many2one('res.users', string='User Created', index=True, tracking=True,
                              default=lambda self: self.env.user)

    contract_id=fields.Many2one('hr.contract',related='employee_id.contract_id',store=True)
    time_off_type=fields.Many2one('hr.leave.type',domain="[('is_annual_leave','=',True)]",required=True,readonly=True,states={'draft': [('readonly', False)]})
    installment_type=fields.Selection([
        ('time_off_request','Time Off Request'),
        ('balance','Balance'),
    ],required=True,readonly=True,states={'draft': [('readonly', False)]})
    time_off_days=fields.Float(compute='_get_time_off_days',store=True)
    balance=fields.Float(compute='_get_current_balance',store=True)
    number_of_days=fields.Float(readonly=True,states={'draft': [('readonly', False)]})

    installment_calculation_method=fields.Many2one('installment.calculation.method',required=True,readonly=True,states={'draft': [('readonly', False)]})

    due_amount=fields.Float(compute='_get_due_amount',store=True)
    ticket_value=fields.Float(readonly=True,states={'draft': [('readonly', False)]})
    additional_value=fields.Float(readonly=True,states={'draft': [('readonly', False)]})
    deduction_value=fields.Float(readonly=True,states={'draft': [('readonly', False)]})
    total_due=fields.Float(compute='_get_total_due',store=True)
    state=fields.Selection([
        ('draft','Draft'),
        ('confirm','Confirm'),
        ('validate','Validate'),
        ('create_advance','Advance Salary Created'),
        ('cancel','Cancel'),
    ],default='draft')

    journal_entry_ids=fields.One2many('account.move','installment')
    journal_entry_count=fields.Integer(compute='_journal_entry_count')

    @api.depends('journal_entry_ids')
    def _journal_entry_count(self):
        for rec in self:
            rec.journal_entry_count=len(rec.journal_entry_ids)


    def action_view_journal_entry(self):
        journal_entry=self.journal_entry_ids.ids
        return {
            'name': _("Journal Entry"),
            'view_mode': 'tree,form',
            'views': False,
            'res_model': 'account.move',
            'type': 'ir.actions.act_window',
            'domain':[('id','in',journal_entry)],
            'nodestroy': True,
            'context': {'create':False}
        }

    advance_salary_ids=fields.One2many('hr.advance.salary','timeoff_installment')
    advance_salary_count=fields.Integer(compute='_advance_salary_count')

    @api.depends('advance_salary_ids')
    def _advance_salary_count(self):
        for rec in self:
            rec.advance_salary_count=len(rec.advance_salary_ids)


    def action_view_advance_salary(self):
        advance_salary=self.advance_salary_ids.ids
        return {
            'name': _("Advance Salary"),
            'view_mode': 'tree,form',
            'views': False,
            'res_model': 'hr.advance.salary',
            'type': 'ir.actions.act_window',
            'domain':[('id','in',advance_salary)],
            'nodestroy': True,
            'context': {'create':False}
        }

    def create_advance_salary(self):
        for rec in self:
            self.env['hr.advance.salary'].create({'timeoff_installment':rec.id,'employee_id':rec.employee_id.id,'reason':'Advance Salary Request From Installment'})
            rec.write({'state':'create_advance'})



    @api.depends('time_off_type','employee_id','installment_type')
    def _get_time_off_days(self):
        for rec in self:
            time_request=self.env['hr.leave'].search([('state','=','validate'),('employee_id','=',self.employee_id.id),('holiday_status_id','=',self.time_off_type.id),('is_paid','=',False),('pay_in_advance','=','yes')])
            rec.time_off_days=sum(request.number_of_days for request in time_request)

    @api.depends('time_off_type','employee_id')
    def _get_current_balance(self):
        for rec in self:
            time_request=self.env['hr.leave'].search([('state','=','validate'),('employee_id','=',self.employee_id.id),('holiday_status_id','=',self.time_off_type.id)])
            time_off_days=sum(request.number_of_days for request in time_request)
            allocation=self.env['hr.leave.allocation'].search([('state','=','validate'),('employee_id','=',self.employee_id.id),('holiday_status_id','=',self.time_off_type.id)])
            number_of_days_allocation=sum(all.number_of_days for all in allocation)
            rec.balance=number_of_days_allocation-time_off_days

    @api.depends('additional_value','deduction_value','due_amount','ticket_value')
    def _get_total_due(self):
        for rec in self:
            rec.total_due=rec.due_amount + rec.additional_value + rec.ticket_value - rec.deduction_value


    @api.depends('installment_calculation_method','number_of_days','contract_id','time_off_days')
    def _get_due_amount(self):
        for rec in self:

            if rec.contract_id:
                installment=0.0
                for method in rec.installment_calculation_method.installment_method_ids:
                    if method.type =='Basic':
                        installment +=rec.contract_id.basic
                    elif method.type =='House_Rent_Allowance':
                        installment +=rec.contract_id.HRA

                    elif method.type =='Transport_Allowance':
                        installment +=rec.contract_id.TA
                if rec.installment_type == 'balance':
                  rec.due_amount=installment/30 *rec.number_of_days
                elif rec.installment_type == 'time_off_request':
                  rec.due_amount=installment/30 *rec.time_off_days
            else:
                rec.due_amount=0.0







    @api.model
    def create(self, values):
        if values.get('name','New') == 'New':
           values['name'] = self.env['ir.sequence'].next_by_code('timeoff.installment')
        return super(TimeoffInstallment, self).create(values)

    def confirm(self):
        for rec in self:
          if rec.installment_type == 'balance':
              if rec.number_of_days == 0.0 :
                  raise UserError(_("Please Add Number of Days For Transaction greater than Zero."))
              if rec.number_of_days > 0.0 :
                  allocation=self.env['hr.leave.allocation'].create({'employee_id':self.employee_id.id,'holiday_status_id':self.time_off_type.id,
                                                      'number_of_days':- self.number_of_days,'holiday_type':'employee'})
                  allocation.action_approve()

                  if allocation.state in ['confirm', 'validate1']:
                      allocation.action_validate()

          elif rec.installment_type == 'time_off_request':
              if rec.time_off_days == 0.0 :
                  raise UserError(_("You can't confirm Transaction that time off days is zero."))

              time_request = self.env['hr.leave'].search(
                  [('state', '=', 'validate'), ('employee_id', '=', self.employee_id.id),
                   ('holiday_status_id', '=', self.time_off_type.id), ('is_paid', '=', False),('pay_in_advance','=','yes')])

              for time in time_request:
                  time.write({'is_paid':True})

          rec.write({'state': 'confirm'})

    def validate(self):
        for rec in self:
            return {
                'name': _("Create Journal Entry"),
                'view_mode':'form',
                'views':False,
                'res_model': 'create.journal.entry',
                'type': 'ir.actions.act_window',
                'nodestroy': True,
                'context': "{'default_installment':active_id}",
                'target':'new',
            }
          # rec.write({'state': 'validate'})

    def set_to_draft(self):
        for rec in self:
          rec.write({'state': 'draft'})

    def cancel(self):
        for rec in self:
          rec.write({'state': 'cancel'})


    def unlink(self):
        for rec in self:
            if rec.state in ['confirm','validate']:
                raise UserError(_("You cannot delete a Transaction which is confirm or validate."))
        return super(TimeoffInstallment, self).unlink()


    @api.constrains('number_of_days','additional_value','deduction_value')
    def _check(self):
        if self.number_of_days > self.balance:
            raise UserError(_("number of days must be less than or equal current balance ."))
        elif self.number_of_days < 0:
            raise UserError(_("number of days must n't be less than zero."))

        elif self.deduction_value < 0:
            raise UserError(_("Deduction Value must n't be less than zero."))

        elif self.additional_value < 0:
            raise UserError(_("Additional Value must n't be less than zero."))






