# -*- coding: utf-8 -*-
from odoo import models, fields, api ,_
from odoo.exceptions import UserError

class HRExpense(models.Model):
    _inherit = 'hr.expense'
    vendor_name=fields.Char()
    vendor_tax_id=fields.Char('Vendor Tax ID')
    supplier_taxes_id=fields.Many2many('account.tax',related='product_id.supplier_taxes_id')


    def _get_account_move_line_values(self):
        res=super(HRExpense, self)._get_account_move_line_values()
        for rec in self:
          for line in res.get(rec.id):
            line.update({
            'vendor_name':rec.vendor_name,
            'vendor_tax_id':rec.vendor_tax_id,
            })
        return res


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    vendor_name=fields.Char()
    vendor_tax_id=fields.Char('Vendor Tax ID')





