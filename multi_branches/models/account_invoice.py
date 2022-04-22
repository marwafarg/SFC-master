# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError


class AccountInvoice(models.Model):
    _inherit = 'account.move'

    def _default_branch_id(self):
        branch_id = self.env.user.branch_id.id
        if self._context.get('branch_id'):
            branch_id = self._context.get('branch_id')
        return branch_id

    branch_id = fields.Many2one("res.branch", string='Branch', default=_default_branch_id)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and not self._context.get('branch_id'):
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            if len(branches) > 0:
                self.branch_id = branches[0]
            else:
                self.branch_id = False
            return {'domain': {'branch_id': [('id', 'in', branches)]}}
        else:
            return {'domain': {'branch_id': []}}

    def action_invoice_register_payment(self):
        return self.env['account.payment']\
            .with_context(active_ids=self.ids, active_model='account.move', active_id=self.id, branch_id=self.branch_id.id)\
            .action_register_payment()

    def _reverse_moves(self, default_values_list=None, cancel=False):
        # OVERRIDE
        if not default_values_list:
            default_values_list = [{} for move in self]
        for move, default_values in zip(self, default_values_list):
            default_values.update({
                'branch_id': move.branch_id.id,
            })
        return super(AccountInvoice, self)._reverse_moves(default_values_list=default_values_list, cancel=cancel)

    def _get_sequence(self):
        ''' Return the sequence to be used during the post of the current move.
        :return: An ir.sequence record or False.
        '''
        self.ensure_one()
        if self.branch_id:
            sale_id = False
            if self.invoice_line_ids:
                sale_id = self.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
            if self.branch_id.invoice_hertz_sequence_id and self.type in ('out_invoice', 'out_receipt') and sale_id and sale_id[0].sales_category and sale_id[0].sales_category == 'hertz':
                return self.branch_id.invoice_hertz_sequence_id
            if self.branch_id.invoice_emper_sequence_id and self.type in ('out_invoice', 'out_receipt') and sale_id and sale_id[0].sales_category and sale_id[0].sales_category == 'emper':
                return self.branch_id.invoice_emper_sequence_id
            if self.branch_id.invoice_sequence_id and self.type in ('out_invoice', 'out_receipt') and not sale_id:
                return self.branch_id.invoice_sequence_id
            if self.branch_id.bill_sequence_id and self.type in ('in_invoice', 'in_receipt'):
                return self.branch_id.bill_sequence_id
            if self.branch_id.invoice_hertz_refund_sequence_id and self.type in ('out_refund') and sale_id and sale_id[0].sales_category and sale_id[0].sales_category == 'hertz':
                return self.branch_id.invoice_hertz_refund_sequence_id
            if self.branch_id.invoice_emper_refund_sequence_id and self.type in ('out_refund') and sale_id and sale_id[0].sales_category and sale_id[0].sales_category == 'emper':
                return self.branch_id.invoice_emper_refund_sequence_id
            if self.branch_id.invoice_refund_sequence_id and self.type in ('out_refund'):
                return self.branch_id.invoice_refund_sequence_id
            if self.branch_id.bill_refund_sequence_id and self.type in ('in_refund'):
                return self.branch_id.bill_refund_sequence_id
        return super(AccountInvoice, self)._get_sequence()


class AccountMoveLine(models.Model):
    _inherit = "account.move.line"

    branch_id = fields.Many2one("res.branch", string='Branch')

    @api.model_create_multi
    def create(self, vals_list):
        res = super(AccountMoveLine, self).create(vals_list=vals_list if vals_list else [])
        for rec in res:
            if not rec.branch_id and rec.move_id and rec.move_id.branch_id:
                rec.branch_id = rec.move_id.branch_id.id
        return res

    def write(self, vals):
        res = super(AccountMoveLine, self).write(vals)
        for rec in self:
            if not rec.branch_id and rec.move_id and rec.move_id.branch_id:
                rec.branch_id = rec.move_id.branch_id.id
        return res


class AccountPayments(models.Model):
    _inherit = 'account.payment'

    def post(self):
        for rec in self:
            if not rec.name and rec.branch_id.payment_sequence_id and rec.partner_type == 'customer':
                rec.name = rec.branch_id.payment_sequence_id.next_by_id(sequence_date=rec.payment_date) or _('New')
        return super(AccountPayments, self).post()

    @api.model
    def default_get(self, fields):
        rec = super(AccountPayments, self).default_get(fields)
        invoice_defaults = self.resolve_2many_commands('invoice_ids', rec.get('invoice_ids'))
        if invoice_defaults and len(invoice_defaults) == 1:
            invoice = invoice_defaults[0]
            rec['branch_id'] = invoice.get('branch_id') and invoice.get('branch_id')[0]
        return rec

    branch_id = fields.Many2one("res.branch", string='Branch', default=lambda self: self.env.user.branch_id)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and not self._context.get('branch_id'):
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            if len(branches) > 0:
                self.branch_id = branches[0]
            else:
                self.branch_id = False
            return {'domain': {'branch_id': [('id', 'in', branches)]}}
        else:
            return {'domain': {'branch_id': []}}

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            self.journal_id = False

    def _prepare_payment_moves(self):
        all_move_vals = super(AccountPayments, self)._prepare_payment_moves()
        for move in all_move_vals:
            move.update({'branch_id': self.branch_id.id})
            for line in move.get('line_ids'):
                line[2].update({'branch_id': self.branch_id.id})
        return all_move_vals


class account_journal(models.Model):
    _inherit = 'account.journal'

    branch_id = fields.Many2one("res.branch", string='Branch', default=lambda self: self.env.user.branch_id.id)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id and not self._context.get('branch_id'):
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            if len(branches) > 0:
                self.branch_id = branches[0]
            else:
                self.branch_id = False
            return {'domain': {'branch_id': [('id', 'in', branches)]}}
        else:
            return {'domain': {'branch_id': []}}

    @api.model
    def name_search(self, name, args, operator='ilike', limit=100):
        if self._context.get('branch_id', False):
            branch_id = self._context.get('branch_id', False)
            if branch_id:
                args.append(('branch_id', '=', branch_id))
            else:
                args.append(('id', '=', []))
        return super(account_journal, self).name_search(name, args=args, operator=operator, limit=limit)
