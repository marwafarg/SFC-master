# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _


class Users(models.Model):
    _inherit = 'res.users'

    def check_installed_modules(self):
        installed_modules = self.env['ir.module.module'].sudo().search([('state', '=', 'installed')])
        for rec in self:
            rec.sudo().installed_modules = ''
            if installed_modules:
                rec.sudo().installed_modules = ','.join(installed_modules.mapped('name'))

    branch_id = fields.Many2one("res.branch", string='Current Branch', default=lambda self: self.env.user.branch_id)
    branch_ids = fields.Many2many('res.branch', string='Allowed Branches', default=lambda self: self.env.user.branch_id)
    installed_modules = fields.Text(string="Installd Modules", compute=check_installed_modules)

    @api.onchange('company_ids')
    def _onchange_company_ids(self):
        if self.company_ids:
            self.branch_ids = self.env['res.branch'].search([('company_id', 'in', self.company_ids.ids)]) or False
            return {'domain': {'branch_ids': [('company_id', 'in', self.company_ids.ids)]}}
        else:
            self.branch_ids = False
            return {'domain': {'branch_ids': []}}

    @api.model
    def create(self, vals):
        res = super(Users, self).create(vals)
        res.clear_caches()
        return res

    def write(self, vals):
        res = super(Users, self).write(vals)
        self.clear_caches()
        return res
