# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    branch_id = fields.Many2one("res.branch", string='Branch', default=lambda self: self.env.user.branch_id)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            self.branch_id = False
            if len(branches) > 0:
                self.branch_id = branches[0]
            warehouse = self.env['stock.warehouse'].search([('branch_id', 'in', self.user_id.branch_ids.ids)])
            default_warehouse = self.env['stock.warehouse'].search([('branch_id', '=', self.env.user.branch_id.id)], limit=1)
            self.warehouse_id = False
            if default_warehouse:
                self.warehouse_id = default_warehouse.id
            return {'domain': {'branch_id': [('id', 'in', branches)], 'warehouse_id': [('id', 'in', warehouse.ids)]}}
        else:
            return {'domain': {'branch_id': [], 'warehouse_id': []}}

    # @api.onchange('branch_id')
    # def _onchange_branch_id(self):
    #     if self.branch_id:
    #         warehouse = self.env['stock.warehouse'].search([('branch_id', '=', self.branch_id.id)])
    #         self.warehouse_id = False
    #         if self.branch_id and warehouse:
    #             self.warehouse_id = warehouse[0].id
    #         return {'domain': {'warehouse_id': [('id', 'in', warehouse.ids)]}}
    #     else:
    #         return {'domain': {'warehouse_id': []}}

    def _prepare_invoice(self):
        invoice_vals = super(SaleOrder, self)._prepare_invoice()
        invoice_vals.update({'branch_id': self.branch_id.id})
        return invoice_vals

    @api.onchange('partner_id')
    def onchange_partner_id(self):
        super(SaleOrder, self).onchange_partner_id()
        if self.partner_id:
            branch_id = self.env.user.branch_ids.filtered(lambda m: m.id == self.partner_id.branch_id.id)
            if branch_id:
                self.branch_id = branch_id.id
            else:
                self.branch_id = self.user_id.branch_id.id or self.env.user.branch_id.id

    @api.model
    def create(self, vals):
        if vals.get('branch_id'):
            branch_id = self.env['res.branch'].browse(vals['branch_id'])
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            if branch_id.sale_sequence_id:
                vals['name'] = branch_id.sale_sequence_id.next_by_id(sequence_date=seq_date) or _('New')
        return super(SaleOrder, self).create(vals)
