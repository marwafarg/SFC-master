# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    branch_id = fields.Many2one('res.branch', related='order_id.branch_id', default=lambda self: self.env.user.branch_id)

    def _prepare_stock_moves(self, picking):
        stock_moves = super(PurchaseOrderLine, self)._prepare_stock_moves(picking)
        for rec in self:
            for move in stock_moves:
                move.update({'branch_id':rec.branch_id.id})
        return stock_moves


class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    branch_id = fields.Many2one("res.branch", string='Branch', default=lambda self: self.env.user.branch_id)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
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
            warehouse = self.env['stock.warehouse'].search([('branch_id', '=', self.branch_id.id)])
            picking = self.env['stock.picking.type'].search([('warehouse_id', 'in', warehouse.ids), ('code', '=', 'incoming')])
            if self.branch_id and picking:
                self.picking_type_id = picking.ids[0]
            else:
                self.picking_type_id = False
            return {'domain': {'picking_type_id': [('id', 'in', picking.ids)]}}
        else:
            return {'domain': {'picking_type_id': []}}

    @api.model
    def _prepare_picking(self):
        res = super(PurchaseOrder, self)._prepare_picking()
        if self.branch_id:
            res.update({'branch_id': self.branch_id.id})
        return res

    # def action_view_invoice(self,moves=False):
    #     result = super(PurchaseOrder, self).action_view_invoice(moves)
    #     if result.get('context'):
    #         result.get('context')['branch_id'] = self.branch_id.id
    #     return result

    @api.model
    def create(self, vals):
        if vals.get('branch_id'):
            branch_id = self.env['res.branch'].browse(vals['branch_id'])
            seq_date = None
            if 'date_order' in vals:
                seq_date = fields.Datetime.context_timestamp(self, fields.Datetime.to_datetime(vals['date_order']))
            if branch_id.purchase_sequence_id:
                vals['name'] = branch_id.purchase_sequence_id.next_by_id(sequence_date=seq_date) or '/'
        return super(PurchaseOrder, self).create(vals)
