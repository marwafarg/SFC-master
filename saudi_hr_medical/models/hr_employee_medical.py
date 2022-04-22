# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import models, fields, api, _
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError, UserError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'
    _order = 'id desc'

    insurance_ids = fields.One2many('insurance.details', 'employee_id', string='Medical Insurance')


class EmployeeClass(models.Model):
    _name = 'employee.class'
    _description = 'Employee Class'

    name = fields.Char('Name', required=True)


class InsuranceDetails(models.Model):
    _name = 'insurance.details'
    _inherit = 'mail.thread'
    _order = 'id desc'
    _description = 'Employee Medical Insurance'

    @api.depends('employee_id')
    def _get_employee_vals(self):
        """
            set value dob, gender, company_id, currency_id, member_name depends on employee_id
        """
        for insurance in self:
            if insurance.employee_id:
                insurance.dob = insurance.employee_id.sudo().birthday
                insurance.gender = insurance.employee_id.sudo().gender
                insurance.company_id = (insurance.employee_id.company_id and insurance.employee_id.company_id.id or False) or (insurance.env.user.company_id and insurance.env.user.company_id.id or False)
                insurance.currency_id = insurance.company_id and insurance.company_id.currency_id and insurance.company_id.currency_id.id or False
                insurance.member_name = insurance.employee_id.name

    def _add_followers(self):
        """
            Add employee and Responsible user in followers
        """
        for insurance in self:
            partner_ids = []
            if insurance.employee_id.user_id:
                partner_ids.append(insurance.employee_id.user_id.partner_id.id)
            if insurance.responsible_id:
                partner_ids.append(insurance.responsible_id.partner_id.id)
            insurance.message_subscribe(partner_ids=partner_ids)

    def _count_claim(self):
        """
            count the number of claims
        """
        for insurance in self:
            insurance.claim_count = len(insurance.claims_ids)

    name = fields.Char(string="Insurance Number", readonly=True, track_visibility='onchange')
    card_code = fields.Char('Card Code', required=True, track_visibility='onchange')
    member_name = fields.Char('Member Name', compute=_get_employee_vals, store=True)
    note = fields.Text('Note')
    claim_count = fields.Integer(string='# of claims', compute=_count_claim)
    insurance_amount = fields.Float('Insurance Amount', required=True, track_visibility='onchange')
    premium_amount = fields.Float('Premium Amount', required=True, track_visibility='onchange')
    start_date = fields.Date('Start Date', required=True, default=fields.Date.today(), track_visibility='onchange')
    end_date = fields.Date('End Date', required=True, track_visibility='onchange')
    dob = fields.Date('Date of Birth', compute=_get_employee_vals, store=True)
    premium_type = fields.Selection([('monthly', 'Monthly'),
                                     ('quarterly', 'Quarterly'),
                                     ('half', 'Half Yearly'),
                                     ('yearly', 'Yearly')], string='Payment Mode', required=True, default='monthly', track_visibility='onchange')
    state = fields.Selection([('draft', 'Draft'),
                              ('confirmed', 'Confirm'),
                              ('cancelled', 'Cancel'),
                              ('done', 'Done')], string='Status', default='draft', track_visibility='onchange')

    class_id = fields.Many2one('employee.class', string='Class', track_visibility='onchange')
    gender = fields.Selection([('male', 'Male'),
                               ('female', 'Female')], compute=_get_employee_vals, store=True)
    relation = fields.Selection([('employee', 'Employee'),
                                 ('child', 'Child'),
                                 ('spouse', 'Spouse')], track_visibility='onchange')
    employee_id = fields.Many2one('hr.employee', required=True, string='Employee', track_visibility='onchange')
    department_id = fields.Many2one('hr.department', string="Department", related='employee_id.department_id', store=True)
    job_id = fields.Many2one('hr.job', 'Job Position', readonly=True, related='employee_id.job_id', store=True)
    branch_id = fields.Many2one('res.branch', 'Office', readonly=True, related='employee_id.branch_id', store=True)
    supplier_id = fields.Many2one('res.partner', required=True, string='Supplier',
                                  track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', compute=_get_employee_vals, store=True)
    responsible_id = fields.Many2one('res.users', string='Responsible', required=True, default=lambda self: self.env.uid,
                                     track_visibility='onchange')
    company_id = fields.Many2one('res.company', string='Company', compute=_get_employee_vals, store=True,
                                 track_visibility='onchange')
    claims_ids = fields.One2many('claim.details', 'insurance_id', string='Claims')
    premium_ids = fields.One2many('insurance.premium', 'insurance_id', string='Insurance premium')
    total_paid_premium = fields.Float('Total Paid Premium', compute="_compute_total_paid_premium")

    _sql_constraints = [
        ('card_code_uniq', 'unique(card_code)',
         'The card code of the insurance must be unique!'),
    ]

    @api.constrains('insurance_amount', 'premium_amount')
    def check_premium_amount(self):
        """
            Check premium amount is less than insurance amount or not
        """
        for insurance in self:
            if insurance.insurance_amount < insurance.premium_amount:
                raise ValidationError(_('Insurance amount must be greater then premium amount!'))

    @api.depends('premium_ids')
    def _compute_total_paid_premium(self):
        for rec in self:
            rec.total_paid_premium = sum(rec.premium_ids.search([('is_invoice_created', '=', True), ('id', 'in', rec.premium_ids.ids)]).mapped('amount'))

    @api.model
    def create(self, values):
        """
            Create a new record and employee add in followers
        """
        values['name'] = self.env['ir.sequence'].next_by_code('insurance.details')
        res = super(InsuranceDetails, self).create(values)
        return res

    @api.onchange('company_id')
    def onchange_company_id(self):
        """
            Set currency: Value from Company
        """
        self.currency_id = False
        if self.company_id:
            self.currency_id = self.company_id.currency_id and self.company_id.currency_id.id or False

    def action_generate_premiums(self):
        """
            Generate insurance premiums
        """
        self.premium_ids = []
        if self.start_date and self.end_date and self.premium_type:
            premium_list = []
            next_date = self.start_date
            index = 1
            while next_date <= self.end_date:
                premium_list.append({'sequence': index,
                                     'date': next_date,
                                     'amount': self.premium_amount or 0.0,
                                     'is_invoice_created': False
                                     })
                if self.premium_type == 'monthly':
                    next_date = next_date + relativedelta(months=1)
                elif self.premium_type == 'quarterly':
                    next_date = next_date + relativedelta(months=3)
                elif self.premium_type == 'half':
                    next_date = next_date + relativedelta(months=6)
                else:
                    next_date = next_date + relativedelta(months=12)
                index += 1
            final_list = [(0, 0, line) for line in premium_list]
            self.premium_ids = final_list

    def action_cancelled(self):
        """
            set insurance status as 'cancelled'
        """
        self.ensure_one()
        self.state = 'cancelled'

    def action_confirm(self):
        """
            set insurance status as 'confirmed'
        """
        self.ensure_one()
        self._add_followers()
        if self.insurance_amount <= 0 or self.premium_amount <= 0:
            raise UserError(_('Please enter proper value for Insurance Amount and Premium Amount'))
        self.action_generate_premiums()
        self.state = 'confirmed'

    def action_done(self):
        """
            set insurance status as 'done'
        """
        self.ensure_one()
        self.state = 'done'

    def action_set_to_draft(self):
        """
            set insurance status as 'draft'
        """
        self.ensure_one()
        self.state = 'draft'

    def view_insurance(self):
        """
           Redirect On Employee Insurance Form
        """
        self.ensure_one()
        form_view = self.env.ref('saudi_hr_medical.insurance_details_form_view')
        return {
            'type': 'ir.actions.act_window',
            'name': _('Insurance'),
            'res_model': 'insurance.details',
            'view_mode': 'from',
            'views': [(form_view.id, 'form')],
            'res_id': self.id,
            'context': self.env.context,
            'create': False,
            'editable': False,
        }

    def view_claims(self):
        """
           Redirect On Insurance Claim
        """
        self.ensure_one()
        if self.claims_ids:
            tree_view = self.env.ref('saudi_hr_medical.claims_details_tree_view')
            form_view = self.env.ref('saudi_hr_medical.claim_details_form_view')
            return {
                'type': 'ir.actions.act_window',
                'name': _('Claims'),
                'res_model': 'claim.details',
                'view_mode': 'form',
                'views': [(tree_view.id, 'tree'), (form_view.id, 'form')],
                'domain': [('id', 'in', self.claims_ids.ids)],
                'res_id': self.claims_ids.ids,
                'context': self.env.context,
            }

    @api.model
    def check_insurance_expiry(self):
        """
            Send mail for Insurance Expiry
        """
        try:
            template_id = self.env.ref('saudi_hr_medical.hr_medical_insurance_expiration_email')
        except ValueError:
            template_id = False
        for insurance in self.search([('state', '=', 'confirmed')]):
            reminder_date = insurance.end_date - timedelta(days=10)
            if reminder_date == fields.Date.today() and template_id:
                template_id.send_mail(insurance.id, force_send=True, raise_exception=True)


class InsurancePremium(models.Model):
    _name = 'insurance.premium'
    _description = 'Insurance Premium'

    sequence = fields.Integer('Sequence', required=True)
    date = fields.Date('Premium Date', required=True)
    amount = fields.Float('Premium Amount', required=True)
    is_invoice_created = fields.Boolean('Invoice Created')
    insurance_id = fields.Many2one('insurance.details', string='Insurance')
    employee_id = fields.Many2one('hr.employee', string='Employee', related='insurance_id.employee_id', store=True)
    branch_id = fields.Many2one('res.branch', string='Office', related='employee_id.branch_id', store=True)
    department_id = fields.Many2one('hr.department', string='Department', related='employee_id.department_id', store=True)
    invoice_id = fields.Many2one('account.move', string="Invoice")
    supplier_id = fields.Many2one('res.partner', string='Supplier', related='insurance_id.supplier_id', store=True)

    def create_invoice(self):
        """
            Create Invoice for Premium Amount
        """
        product_id = self.env.ref('saudi_hr_medical.insurance_prodcuct')
        account_move_obj = self.env['account.move']
        account_move_line_obj = self.env['account.move.line']
        if not self.insurance_id.supplier_id.property_account_payable_id:
            raise UserError(
                _('There is no payable account defined for this supplier: "%s".') %
                (self.insurance_id.supplier_id.name,))
        contract = self.env['hr.contract'].search([('employee_id', '=', self.insurance_id.employee_id.id),
                                        ('state', '=', 'open')], limit=1)
        inv_default = {}
        inv_default.update({'partner_id': self.insurance_id.supplier_id.id,
                            'invoice_date': self.date,
                            'type': 'in_invoice',
                            'ref': self.insurance_id.name + '-' +str(self.sequence),
                            'invoice_date_due': self.date,
                            'branch_id': self.insurance_id.branch_id.id
                            })
        invoices_id = account_move_obj.create(inv_default)
        a = account_move_line_obj.with_context({'check_move_validity': False}).create({
                            'name': 'Insurance Premium',
                            'price_unit': self.amount,
                            'quantity': 1.0,
                            'product_id': product_id.id,
                            'account_id': (product_id.property_account_expense_id and product_id.property_account_expense_id.id or False) or (product_id.categ_id.property_account_expense_categ_id and product_id.categ_id.property_account_expense_categ_id.id or False),
                            'move_id': invoices_id.id,
                            'branch_id': self.branch_id.id,
                            'analytic_account_id': contract.analytic_account_id.id or False,
                            'analytic_tag_ids': [(6, 0, contract.analytic_tag_ids.ids)] or False,
                            })
        invoices_id._compute_amount()
        invoices_id.with_context({'check_move_validity': False})._recompute_dynamic_lines()
        invoices_id._onchange_invoice_line_ids()
        invoices_id._compute_invoice_taxes_by_group()
        self.invoice_id = (invoices_id and invoices_id.id or False)
        self.is_invoice_created = True

    def view_invoice_action(self):
        """
            View Invoice
        """
        return {
                'type': 'ir.actions.act_window',
                'view_mode': 'form',
                'res_model': 'account.move',
                'views': [(self.env.ref('account.view_move_form').id, 'form')],
                'res_id': self.invoice_id.id
        }

    def print_invoice(self):
        """
            Print Invoice
        """
        return self.env.ref('account.account_invoices').report_action(self.invoice_id)

    def action_invoice_create(self):
        """
            Create Invoice for Premium Amount
        """
        premiums = self.search([('insurance_id.state', '=', 'confirmed'), ('is_invoice_created', '=', False), ('date', '=', fields.date.today())])
        for premium in premiums:
            premium.create_invoice()


class ClaimDetails(models.Model):
    _name = 'claim.details'
    _description = 'Claim Details'
    _inherit = 'mail.thread'

    @api.depends('insurance_id', 'responsible_id')
    def _set_insurance_vals(self):
        """
            Set claim company id and currency id
        """
        for claim in self:
            claim.company_id = claim.env.user.company_id.id
            claim.currency_id = claim.company_id.currency_id.id
            if claim.insurance_id:
                claim.company_id = claim.insurance_id.company_id.id
                claim.currency_id = claim.company_id.currency_id.id

    name = fields.Char(string="Claim Number", readonly=True)
    date_applied = fields.Date('Date Applied', default=fields.Date.today(), required=True, track_visibility='onchange')
    claim_amount = fields.Float('Claim Amount', required=True, track_visibility='onchange')
    passed_amount = fields.Float('Passed Amount', track_visibility='onchange')
    insurance_id = fields.Many2one('insurance.details', string='Insurance', required=True, domain="[('state', '=', 'confirmed'), ('employee_id', '=', employee_id)]", track_visibility='onchange')
    company_id = fields.Many2one('res.company', string="Company", compute=_set_insurance_vals, store=True, track_visibility='onchange')
    responsible_id = fields.Many2one('res.users', string="Responsible", required=True, default=lambda self: self.env.uid, track_visibility='onchange')
    currency_id = fields.Many2one('res.currency', compute=_set_insurance_vals, store=True)
    state = fields.Selection([('draft', 'Draft'),
                              ('confirm', 'Confirmed'),
                              ('refuse', 'Refused'),
                              ('cancel', 'Cancelled'),
                              ('done', 'Done')], default='draft', track_visibility='onchange')
    note = fields.Text('Note')
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True, default=lambda self: self.env['hr.employee'].get_employee())

    def _add_followers(self):
        """
            Add employee and Responsible user in followers
        """
        for claim in self:
            partner_ids = []
            if claim.employee_id.user_id:
                partner_ids.append(claim.employee_id.user_id.partner_id.id)
            if claim.responsible_id:
                partner_ids.append(claim.responsible_id.partner_id.id)
            claim.message_subscribe(partner_ids=partner_ids)

    @api.model
    def create(self, values):
        """
            Create a new record and employee add in followers
        """
        values['name'] = self.env['ir.sequence'].next_by_code('claim.details')
        res = super(ClaimDetails, self).create(values)
        return res

    @api.onchange('insurance_id')
    def onchange_insurance_id(self):
        """
            Set Responsible: Value from Insurance
        """
        self.responsible_id = False
        if self.insurance_id:
            self.responsible_id = self.insurance_id.responsible_id and self.insurance_id.responsible_id or False

    @api.onchange('company_id')
    def onchange_company_id(self):
        """
            Set Currency: Value from Company
        """
        self.currency_id = False
        if self.company_id:
            self.currency_id = self.company_id.sudo().currency_id and self.company_id.currency_id.id or False

    def action_confirm(self):
        """
            set claim status as 'confirm'
        """
        self.ensure_one()
        if self.claim_amount <= 0:
            raise UserError(_('Please enter proper value for Claim Amount'))
        self._add_followers()
        self.state = 'confirm'

    def action_refuse(self):
        """
            set claim status as 'refuse'
        """
        self.ensure_one()
        self.state = 'refuse'

    def action_cancel(self):
        """
            set claim status as 'cancel'
        """
        self.ensure_one()
        self.state = 'cancel'

    def action_done(self):
        """
            set claim status as 'done'
        """
        self.ensure_one()
        if self.passed_amount <= 0:
            raise UserError(_('Passed Amount should be greater then 0'))
        else:
            self.state = 'done'

    def action_set_to_draft(self):
        """
            set claim status as 'draft'
        """
        self.ensure_one()
        self.state = 'draft'
