# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class Warehouse(models.Model):
    _inherit = 'stock.warehouse'

    branch_id = fields.Many2one("res.branch", string='Branch', default=lambda self: self.env.user.branch_id)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            self.branch_id = False
            if len(branches) > 0:
                self.branch_id = branches[0]
        else:
            return {'domain': {'branch_id': []}}

    def _create_or_update_sequences_and_picking_types(self):
        self.ensure_one
        res = super(Warehouse, self)._create_or_update_sequences_and_picking_types()
        PickingType = self.env['stock.picking.type']
        for picking_type in res:
            PickingType.browse(res[picking_type]).write({'branch_id': self.branch_id.id})
        return res

    @api.model
    def create(self, vals):
        if self._context.get('is_branch'):
            return False
        warehouse = super(Warehouse, self).create(vals)
        if warehouse:
            warehouse.lot_stock_id.write({'branch_id': vals.get('branch_id')})
            warehouse.view_location_id.write({'branch_id': vals.get('branch_id')})
            warehouse.wh_input_stock_loc_id.write({'branch_id': vals.get('branch_id')})
            warehouse.wh_qc_stock_loc_id.write({'branch_id': vals.get('branch_id')})
            warehouse.wh_output_stock_loc_id.write({'branch_id': vals.get('branch_id')})
            warehouse.wh_pack_stock_loc_id.write({'branch_id': vals.get('branch_id')})
            # v13 base problem company not change in buy rule
            # warehouse.buy_pull_id.write({'company_id': vals.get('company_id')})
        return warehouse

    @api.model
    def name_search(self, name, args, operator='ilike', limit=100):
        context = dict(self.env.context)
        if context.get('branch_id'):
            warehouses = self.env['stock.warehouse'].search([('branch_id', '=', context['branch_id'])])
            if len(warehouses) > 0:
                args.append(('id', 'in', warehouses.ids))
            else:
                args.append(('id', '=', []))
        if context.get('user_id'):
            # user_id = self.env['res.users'].browse(context['user_id'])
            warehouses = self.env['stock.warehouse'].search([('branch_id', 'in', self.env.user.branch_ids.ids)])
            if len(warehouses) > 0:
                args.append(('id', 'in', warehouses.ids))
            else:
                args.append(('id', '=', []))
        return super(Warehouse, self).name_search(name, args=args, operator=operator, limit=limit)


class StockLocation(models.Model):
    _inherit = 'stock.location'

    branch_id = fields.Many2one("res.branch", string='Branch', default=lambda self: self.env.user.branch_id)

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            self.branch_id = False
            if len(branches) > 0:
                self.branch_id = branches[0]
        else:
            return {'domain': {'branch_id': []}}

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id.id != self.location_id.branch_id.id:
            raise ValidationError(_("Configuration Error \n You must select same branch on a location as a warehouse configuration"))


class StockPicking(models.Model):
    _inherit = 'stock.picking'

    branch_id = fields.Many2one("res.branch", string='Branch',
                                default=lambda self: self.env.user.branch_id, index=True,
                                states={'done': [('readonly', True)], 'cancel': [('readonly', True)]})

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            self.branch_id = False
            if len(branches) > 0:
                self.branch_id = branches[0]
        else:
            return {'domain': {'branch_id': []}}



class StockPickingType(models.Model):
    _inherit = 'stock.picking.type'

    branch_id = fields.Many2one("res.branch", string='Branch',
                                default=lambda self: self.env.user.branch_id, index=True)

    @api.onchange('warehouse_id')
    def _onchange_warehouse_id(self):
        if self.warehouse_id:
            self.branch_id = self.warehouse_id.branch_id.id

    @api.model
    def name_search(self, name, args, operator='ilike', limit=100):
        if self._context.get('branch_id', False):
            branch_id = self._context.get('branch_id', False)
            warehouse = self.env['stock.warehouse'].search([('branch_id', '=', branch_id)])
            if warehouse:
                pickings = self.env['stock.picking.type'].search([('warehouse_id', 'in', warehouse.ids), ('code', '=', 'incoming')])
                if pickings:
                    args.append(('id', 'in', pickings.ids))
                else:
                    args.append(('id', '=', []))
        if self._context.get('pos_branch_id', False):
            branch_id = self._context.get('pos_branch_id', False)
            if branch_id:
                args.append(('branch_id', '=', branch_id))
            else:
                args.append(('id', '=', []))
        return super(StockPickingType, self).name_search(name, args=args, operator=operator, limit=limit)


class StockMove(models.Model):
    _inherit = 'stock.move'

    branch_id = fields.Many2one("res.branch", string='Branch', default=lambda self: self.env.user.branch_id)

    def _assign_picking(self):
        """ Try to assign the moves to an existing picking that has not been
        reserved yet and has the same procurement group, locations and picking
        type (moves should already have them identical). Otherwise, create a new
        picking to assign them to. """
        Picking = self.env['stock.picking']
        for move in self:
            move.branch_id = self.group_id.sale_id.warehouse_id.branch_id.id
            recompute = False
            picking = move._search_picking_for_assignation()
            if picking:
                if picking.partner_id.id != move.partner_id.id or picking.origin != move.origin:
                    # If a picking is found, we'll append `move` to its move list and thus its
                    # `partner_id` and `ref` field will refer to multiple records. In this
                    # case, we chose to  wipe them.
                    picking.write({
                        'partner_id': False,
                        'origin': False,
                    })
            else:
                recompute = True
                picking = Picking.create(move._get_new_picking_values())
            move.write({'picking_id': picking.id})
            move._assign_picking_post_process(new=recompute)
            # If this method is called in batch by a write on a one2many and
            # at some point had to create a picking, some next iterations could
            # try to find back the created picking. As we look for it by searching
            # on some computed fields, we have to force a recompute, else the
            # record won't be found.
            if recompute:
                move.recompute()
        return True

    def _get_new_picking_values(self):
        vals = super(StockMove, self)._get_new_picking_values()
        vals['branch_id'] = self.group_id.sale_id.warehouse_id.branch_id.id
        return vals

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            self.branch_id = False
            if len(branches) > 0:
                self.branch_id = branches[0]
        else:
            return {'domain': {'branch_id': []}}

    def _create_account_move_line(self, credit_account_id, debit_account_id, journal_id, qty, description, svl_id, cost):
        self.ensure_one()
        AccountMove = self.env['account.move'].with_context(default_journal_id=journal_id)

        move_lines = self._prepare_account_move_line(qty, cost, credit_account_id, debit_account_id, description)
        if move_lines:
            date = self._context.get('force_period_date', fields.Date.context_today(self))
            new_account_move = AccountMove.sudo().create({
                'journal_id': journal_id,
                'line_ids': move_lines,
                'date': date,
                'ref': description,
                'stock_move_id': self.id,
                'stock_valuation_layer_ids': [(6, None, [svl_id])],
                'type': 'entry',
                'branch_id': self.branch_id.id,
            })
            new_account_move.post()

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description):
        res = super(StockMove, self)._generate_valuation_lines_data(partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, description)
        res['debit_line_vals'].update({'branch_id': self.picking_id.branch_id.id})
        res['credit_line_vals'].update({'branch_id': self.picking_id.branch_id.id})
        if 'price_diff_line_vals' in res:
            res['price_diff_line_vals'].update({'branch_id': self.picking_id.branch_id.id})
        return res


class StockQuant(models.Model):
    _inherit = 'stock.quant'

    branch_id = fields.Many2one(related='location_id.branch_id', store=True, readonly=True, string='Branch')


class Inventory(models.Model):
    _inherit = "stock.inventory"

    branch_id = fields.Many2one("res.branch", string='Branch', default=lambda self: self.env.user.branch_id)
    location_ids = fields.Many2many(
        'stock.location', string='Locations',
        readonly=True, check_company=True,
        states={'draft': [('readonly', False)]},
        domain="[('company_id', '=', company_id), ('usage', 'in', ['internal', 'transit']), '|', ('branch_id', '=', branch_id), ('branch_id', '=', False)]")

    @api.model
    def default_get(self, fields):
        res = super(Inventory, self).default_get(fields)
        if res.get('location_id'):
            location_branch = self.env['stock.location'].browse(res.get('location_id')).branch_id.id
            if location_branch:
                res['branch_id'] = location_branch
        else:
            res['branch_id'] = self.env.user.branch_id.id
        return res

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            self.branch_id = False
            if len(branches) > 0:
                self.branch_id = branches[0]
        else:
            return {'domain': {'branch_id': []}}

    def post_inventory(self):
        # The inventory is posted as a single step which means quants cannot be moved from an internal location to another using an inventory
        # as they will be moved to inventory loss, and other quants will be created to the encoded quant location. This is a normal behavior
        # as quants cannot be reuse from inventory location (users can still manually move the products before/after the inventory if they want).
        self.mapped('move_ids').filtered(lambda move: move.state != 'done')._action_done()
        for move_id in self.move_ids:
            account_move = self.env['account.move'].search([('stock_move_id', '=', move_id.id)])
            account_move.write({'branch_id': self.branch_id.id})
            for line in account_move.line_ids:
                line.write({'branch_id': self.branch_id.id})


class StockRule(models.Model):
    """ A rule describe what a procurement should do; produce, buy, move, ... """
    _inherit = 'stock.rule'

    branch_id = fields.Many2one("res.branch", string='Branch', related='warehouse_id.branch_id')
