# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from datetime import datetime

import odoo.addons.decimal_precision as dp
from odoo import api, fields, models


class AccountMove(models.Model):
    _inherit= 'account.move'
    installment=fields.Many2one('timeoff.installment')


class CreateJournalEntry(models.TransientModel):
    _name = 'create.journal.entry'
    _description = "Create Journal Entry"
    debit_account_id=fields.Many2one('account.account',readonly=True)
    credit_account_id=fields.Many2one('account.account',readonly=True,related='journal_id.default_account_id')
    journal_id=fields.Many2one('account.journal',required=True,domain=[('type','in',['bank','cash'])])
    partner_id=fields.Many2one('res.partner',readonly=True)
    amount=fields.Float(readonly=True)
    installment=fields.Many2one('timeoff.installment')
    date = fields.Date('Date',readonly=True)






    @api.model
    def default_get(self, default_fields):
        res = super(CreateJournalEntry, self).default_get(default_fields)
        data = self.env['timeoff.installment'].browse(self._context.get('active_ids', []))
        for record in data:
             res.update({'partner_id':record.employee_id.address_home_id.id,'amount':record.total_due,'date':record.date,'debit_account_id':record.installment_calculation_method.time_off_debit_id.id})
        return res

    def action_create_journal_entry(self):
        account_move_obj = self.env['account.move']
        method=self.installment.installment_calculation_method
        entry=account_move_obj.create({'ref': self.installment.name,
                                     'journal_id': self.journal_id.id,
                                     'installment': self.installment.id,
                                     'date': self.date,
                                     'line_ids': [(0, 0, {
                                         'name':'Total Due', 'account_id': self.credit_account_id.id,
                                         'partner_id': self.partner_id.id,
                                         'credit': self.installment.total_due, 'debit':0.0, 'date_maturity': self.date,

                                     }),(0, 0, {
                                         'name':'Deduction Value', 'account_id': method.other_deductions_credit_id.id,
                                         'partner_id': self.partner_id.id,
                                         'credit': self.installment.deduction_value, 'debit':0.0, 'date_maturity': self.date,

                                     }),
                                    (0, 0, {
                                         'name':'Due Amount', 'account_id': self.debit_account_id.id,
                                        'partner_id': self.partner_id.id,
                                         'credit':0.0, 'debit': self.installment.due_amount, 'date_maturity': self.date,
                                     }), (0, 0, {
                                         'name':'Ticket Value', 'account_id': method.ticket_debit_id.id,
                                          'partner_id': self.partner_id.id,
                                         'credit':0.0, 'debit': self.installment.ticket_value, 'date_maturity': self.date,
                                     }), (0, 0, {
                                         'name':'Additional Value', 'account_id': method.other_allowances_debit_id.id,
                                         'partner_id': self.partner_id.id,
                                         'credit':0.0, 'debit': self.installment.additional_value, 'date_maturity': self.date,
                                     })
                                    ]})
        entry.action_post()

        if self.installment.installment_type == 'time_off_request':
            time_request = self.env['hr.leave'].search(
                [('state', '=', 'validate'), ('employee_id', '=', self.installment.employee_id.id),
                 ('holiday_status_id', '=', self.installment.time_off_type.id), ('is_paid', '=', False)])
            for rec in time_request:
                rec.write({'is_paid':True})
        self.installment.write({'state':'validate'})