# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing detials.

from odoo import models, fields, api, _
from datetime import datetime
from odoo.exceptions import ValidationError


class AnnualTicket(models.Model):
    _name = 'annual.ticket'
    _description = "Annual Ticket"
    _rec_name = 'year_id'

    name = fields.Char('Name', required=True)
    year_id = fields.Many2one('year.year', required=True)
    annual_ticket_detail_ids = fields.One2many('annual.ticket.detail', 'annual_ticket_id')
    company_id = fields.Many2one('res.company', string='Company', readonly=True,
                                 default=lambda self: self.env.user.company_id)

    def action_annual_ticket_by_employees(self):
        self.ensure_one()
        form_view = self.env.ref('saudi_hr_air_allowance.view_annual_ticket_by_employees', False)
        return {
            'name': _('Generate Annual Leaving'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'annual.ticket.employees',
            'views': [(form_view.id, 'form')],
            'view_id': form_view.id,
            'target': 'new',
            'context': {'year_id': self.year_id.id},
        }

    @api.constrains('annual_ticket_detail_ids')
    def check_duplicate_emp(self):
        for rec in self:
            emp_list = []
            for line in rec.annual_ticket_detail_ids.search([('year_id', '=', rec.year_id.id)]):
                if line.employee_id.id not in emp_list:
                    emp_list.append(line.employee_id.id)
                else:
                    raise ValidationError(_('You already done %s annual ticket for this particular year!!') % line.employee_id.name)


class AnnualTicketDetails(models.Model):
    _name = 'annual.ticket.detail'
    _description = "Annual Ticket details"
    _rec_name = 'employee_id'

    annual_ticket_id = fields.Many2one('annual.ticket')
    employee_id = fields.Many2one('hr.employee', required=True)
    adult_fare = fields.Float('Adult Fare', required=True, help="This amount shows return fare from the selected city.")
    child_fare = fields.Float('Child Fare', help="80% of Adult Fare", required=True)
    infant_fare = fields.Float('Infant Fare', help="12.5% of Adult Fare", required=True)
    adults = fields.Integer('Adult(s)', compute='_get_total_members', help='Employee and Spouse')
    children = fields.Integer('Children', compute='_get_total_members',
                              help='Maximum two children, if no infants(Age must be between 2 to 18)')
    infant = fields.Integer('Infant(s)', compute='_get_total_members',
                            help='Maximum two infants, if no children(Below 2 Years)')

    ticket_status_ids = fields.One2many('annual.ticket.status', 'ticket_detail_id')
    year_id = fields.Many2one('year.year', required=True)
    allocated_amount = fields.Float('Allocated Amount', required=True, compute='_compute_amount')
    used_amount = fields.Float('Used Amount', compute='_compute_amount')
    remaining_amount = fields.Float('Remaining Amount', compute='_compute_amount')
    other_hr_payslip_ids = fields.One2many('other.hr.payslip', 'ticket_detail_id', readonly=True)

    def generate_air_allowance(self):
        for rec in self:
            return {
               'type': 'ir.actions.act_window',
               'res_model': 'generate.air.allowance',
               'view_mode': 'form',
               'view_type': 'form',
               'view_id': self.env.ref('saudi_hr_air_allowance.generate_air_allowance_from_view').id,
               'target': 'new',
               'context': {'default_allowance_amount': rec.remaining_amount}
            }

    @api.depends('adults', 'infant', 'children', 'adult_fare', 'infant_fare', 'child_fare', 'ticket_status_ids',
                 'other_hr_payslip_ids')
    def _compute_amount(self):
        for rec in self:
            rec.allocated_amount = (rec.adult_fare + rec.infant_fare + rec.child_fare)
            rec.used_amount = sum(rec.ticket_status_ids.mapped('used_amount'))
            rec.remaining_amount = rec.allocated_amount - rec.used_amount
            if rec.other_hr_payslip_ids:
                rec.remaining_amount = rec.remaining_amount - sum(rec.other_hr_payslip_ids.mapped('amount'))

    @api.depends('employee_id')
    def _get_total_members(self):
        """
            calculate the adults, children and infant
        """
        for rec in self:
            rec.adults = 1
            rec.children = 0
            rec.infant = 0
            adults = 1
            children = infant = 0
            if rec.employee_id:
                for dependent in rec.employee_id.dependent_ids:
                    current_year = datetime.today().strftime('%Y')
                    dob_year = dependent.birthdate.year
                    age_year = int(current_year) - int(dob_year)
                    if age_year >= 18 and adults < 2:
                        adults += 1
                    elif age_year >= 2 and age_year < 18 and children < 2:
                        children += 1
                    elif age_year < 2 and infant < 2:
                        infant += 1
                rec.adults = adults
                rec.children = children
                rec.infant = infant
                # Below hack is for contract calculation, if employee will have 2 children then he will not get fare for infant
                if children == 2:
                    rec.infant = 0

    @api.onchange('adult_fare')
    def onchange_adult_fare(self):
        """
            calculate the child and infant fare
        """
        for rec in self:
            rec.child_fare = 0.0
            rec.infant_fare = 0.0
            if rec.adult_fare > 0:
                if rec.children > 0:
                    rec.child_fare = (rec.adult_fare * 80) / 100
                if rec.infant > 0:
                    rec.infant_fare = (rec.adult_fare * 12.5) / 100
                rec.passed_amount = rec.child_fare + rec.infant_fare + rec.adult_fare


class AnnualTicketStatus(models.Model):
    _name = 'annual.ticket.status'
    _description = 'Annual Ticket Status'

    ticket_detail_id = fields.Many2one('annual.ticket.detail')
    member_type = fields.Selection([('adult', 'Adult'), ('child', 'Child'), ('infant', 'Infant')])
    ticket_status = fields.Selection([('not_used', 'Not Used'), ('used', 'Used')], 'Ticket Status', default='not_used')
    allocated_amount = fields.Float('Allocated Amount', compute='_compute_allocated_amount')
    used_amount = fields.Float('Used Amount')
    remaining_amount = fields.Float('Remaining Amount', compute='_compute_remaining_amount')

    def _compute_allocated_amount(self):
        for rec in self:
            if rec.member_type == 'adult' and rec.ticket_detail_id.adult_fare > 0:
                rec.allocated_amount = (rec.ticket_detail_id.adult_fare / rec.ticket_detail_id.adults)
            elif rec.member_type == 'child' and rec.ticket_detail_id.child_fare > 0:
                rec.allocated_amount = (rec.ticket_detail_id.child_fare / rec.ticket_detail_id.children)
            elif rec.member_type == 'infant' and rec.ticket_detail_id.infant_fare > 0:
                rec.allocated_amount = (rec.ticket_detail_id.infant_fare/ rec.ticket_detail_id.infant)

    def _compute_remaining_amount(self):
        for rec in self:
            if rec.used_amount > 0:
                rec.remaining_amount = rec.allocated_amount - rec.used_amount


class OtherHrPayslip(models.Model):
    _inherit = 'other.hr.payslip'

    ticket_detail_id = fields.Many2one('annual.ticket.detail')
