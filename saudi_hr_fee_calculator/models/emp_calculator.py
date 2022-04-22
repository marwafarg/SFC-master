# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError
from datetime import datetime
from odoo.tools import DEFAULT_SERVER_DATE_FORMAT
import calendar


class ExpatsFee(models.Model):
    _name = 'expats.fee'
    _order = 'id desc'
    _inherit = ['mail.thread']
    _description = "Expats Fee"

    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id, required=True)
    up_level_fee = fields.Float('Up Level Fee', required=True)
    down_level_fee = fields.Float('Down Level Fee', required=True)
    year = fields.Many2one('year.year', string='Year', required=True)
    expats_fee_line = fields.One2many('expats.fee.line', 'expats_fee_id')
    state = fields.Selection([('draft', 'Draft'), ('confirm', 'Confirm'), ('done', 'Done'), ('cancelled', 'Cancel')], default='draft')
    done = fields.Boolean()

    _sql_constraints = [
        ('code_month_uniq', 'unique (year)', 'The Year must be unique!')
    ]

    @api.onchange('year')
    def onchange_year(self):
        """
            onchange the value based on selected year,
            up_level_fee, down_level_fee, expats_fee_line
        """
        self.up_level_fee = False
        self.down_level_fee = False
        self.expats_fee_line = False

    def name_get(self):
        """
            Return name of Expats Fee year name
        """
        res = []
        for year in self:
            name = 'Year ' + year.year.name or ''
            res.append((year.id, name))
        return res

    def confirm_expats_fee(self):
        """
            sent the status of generating record Expats Fee in 'Confirm' state
        """
        if not self.expats_fee_line:
            raise UserError(_('Please create some fee details.'))
        self.state = 'confirm'

    def done_expats_fee(self):
        """
            sent the status of generating record Expats Fee in 'Done' state
        """
        self.state = 'done'
        self.done = True

    def cancel_expats_fee(self):
        """
            sent the status of generating record Expats Fee in 'Cancel' state
        """
        self.state = 'cancelled'

    def draft_expats_fee(self):
        """
            sent the status of generating record Expats Fee in 'Draft' state
        """
        self.state = 'draft'
        self.done = False

    def unlink(self):
        """
            Delete/ remove selected record
            :return: Deleted record ID
        """
        for line in self:
            if line.state in ['confirm', 'done']:
                raise UserError(_('You can remove the record which is in Draft or Cancel state'))
            return super(ExpatsFee, line).unlink()


class ExpatsFeeLine(models.Model):
    _name = 'expats.fee.line'
    _order = 'id desc'
    _inherit = ['mail.thread']
    _description = "Expats Fee Line"

    @api.depends('month', 'expats_fee_id', 'fee')
    def compute_fee(self):
        """
            set total_expats_employee, total_employee, total_saudi_employee Value
            based on month, expats fee and fee
        """
        for rec in self:
            rec.total_employee = False
            rec.total_expats_employee = False
            rec.ratio = False
            rec.total_fee = False
            employee_obj = self.env['hr.employee']
            if rec.expats_fee_id.year and rec.month:
                count = 0
                expats_year = rec.expats_fee_id.year.date_start
                expats_employee = employee_obj.search(['|', ('active', '=', False), ('active', '=', True), '|', ('country_id.code', '!=', 'SA'), ('country_id', '=', False), ('date_of_join', '!=', False)])
                for line in expats_employee:
                    if int(line.date_of_join.year) < int(expats_year.year):
                        count += 1
                    elif int(line.date_of_join.year) == int(expats_year.year) and int(line.date_of_join.month) <= int(rec.month):
                        count += 1
                    if line.date_of_leave:
                        if int(line.date_of_leave.year) < int(expats_year.year):
                            count -= 1
                        elif int(line.date_of_leave.year) == int(expats_year.year) and int(line.date_of_leave.month) < int(rec.month):
                            count -= 1
                        elif int(line.date_of_leave.year) == int(expats_year.year) and int(line.date_of_leave.month) <= int(rec.month) and int(line.date_of_leave.day) < 15:
                            count -= 1
                rec.total_expats_employee = count

                total_employee = employee_obj.search(['|', ('active', '=', False), ('active', '=', True), ('date_of_join', '!=', False)])
                count = 0
                for line in total_employee:
                    expats_year = rec.expats_fee_id.year.date_start
                    if int(line.date_of_join.year) < int(expats_year.year):
                        count += 1
                    elif int(line.date_of_join.year) == int(expats_year.year) and int(line.date_of_join.month) <= int(rec.month):
                        count += 1
                    if line.date_of_leave:
                        if int(line.date_of_leave.year) < int(expats_year.year):
                            count -= 1
                        elif int(line.date_of_leave.year) == int(expats_year.year) and int(line.date_of_leave.month) < int(rec.month):
                            count -= 1
                        elif int(line.date_of_leave.year) == int(expats_year.year) and int(line.date_of_leave.month) <= int(rec.month) and int(line.date_of_leave.day) < 15:
                            count -= 1
                rec.total_employee = count

                saudi_employee = employee_obj.search(['|', ('active', '=', False), ('active', '=', True), ('country_id.code', '=', 'SA'), ('date_of_join', '!=', False)])
                count = 0

                for line in saudi_employee:
                    if int(line.date_of_join.year) < int(expats_year.year):
                        count += 1
                    elif int(line.date_of_join.year) == int(expats_year.year) and int(line.date_of_join.month) <= int(rec.month):
                        count += 1
                    if line.date_of_leave:
                        if int(line.date_of_leave.year) < int(expats_year.year):
                            count -= 1
                        elif int(line.date_of_leave.year) == int(expats_year.year) and int(line.date_of_leave.month) < int(rec.month):
                            count -= 1
                        elif int(line.date_of_leave.year) == int(expats_year.year) and int(line.date_of_leave.month) <= int(rec.month) and int(line.date_of_leave.day) < 15:
                            count -= 1
                rec.total_saudi_employee = count

                if rec.total_employee and rec.total_expats_employee > 0:
                    rec.ratio = float((float(rec.total_expats_employee) / float(rec.total_employee)) * 100)
                    rec.total_fee = rec.total_expats_employee * rec.fee

    expats_fee_id = fields.Many2one('expats.fee', string='Expats Fee', domain=[('state', 'not in', ['done', 'cancelled'])])
    total_saudi_employee = fields.Float('Saudi Employees', compute=compute_fee, store=True)
    month = fields.Selection([('1', 'January'), ('2', 'February'), ('3', 'March'), ('4', 'April'), ('5', 'May'), ('6', 'June'), ('7', 'July'), ('8', 'August'), ('9', 'September'), ('10', 'October'), ('11', 'November'), ('12', 'December')], required=True)
    total_employee = fields.Float(string='Total Employees', compute=compute_fee, store=True)
    total_expats_employee = fields.Float(string='Expats Employees', compute=compute_fee, store=True)
    ratio = fields.Float(string='Ratio(%)', compute=compute_fee, store=True)
    fee = fields.Float(string='Fee', readonly=False)
    total_fee = fields.Float(string='Total Fee', compute=compute_fee, store=True)
    done = fields.Boolean(related='expats_fee_id.done', readonly=True)

    _sql_constraints = [
        ('expats_fee_id', 'unique (expats_fee_id,month)', 'The Month must be unique!')
    ]

    def name_get(self):
        """
            Return name of Expats Fee Line based on months
        """
        res = []
        for month in self:
            month_name = calendar.month_name[int(month.month)]
            name = ' '.join([month.expats_fee_id.year.name or '', ' - ', month_name])
            res.append((month.id, name))
        return res

    @api.onchange('expats_fee_id', 'month')
    def onchange_expats_year_month(self):
        """
            onchange the value based on selected expats_fee_id and month,
            Fee
        """
        for line in self:
            line.fee = False
            if line.total_expats_employee > line.total_saudi_employee:
                line.fee = line.fee or line.expats_fee_id.up_level_fee
            else:
                line.fee = line.fee or line.expats_fee_id.down_level_fee

    @api.model
    def schedular_calculate_fee(self):
        """
            Create Expats Fee Line based on Running month
        """
        todaydate = datetime.today().date()
        for line in self.env['expats.fee'].search([]):
            date_start = line.year.date_start
            date_stop = line.year.date_stop
            if date_start <= todaydate and date_stop >= todaydate:
                expats_fee_line_ids = self.env['expats.fee.line'].search([('month', '=', todaydate.month)])
                if expats_fee_line_ids:
                    for rec in expats_fee_line_ids:
                        rec.write({
                            'expats_fee_id': line.id,
                            'month': str(todaydate.month)
                            })
                        rec.onchange_expats_year_month()
                else:
                    line_id = self.create({
                        'expats_fee_id': line.id,
                        'month': str(todaydate.month)
                        })
                    line_id.onchange_expats_year_month()
