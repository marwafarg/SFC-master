# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class MaintenanceEquipment(models.Model):
    _inherit = 'maintenance.equipment'

    branch_id = fields.Many2one('res.branch', string='Office', )#default=lambda self: self.env.user.branch_id

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """
            Override method for apply domain on user
        """
        context = dict(self.env.context)
        if context.get('category_id') and context.get('assign_to'):
            args.extend([('category_id', '=', context.get('category_id')),
                         ('equipment_assign_to', '=', context.get('assign_to'))])
            if context.get('assign_to') == 'employee':
                args.append(('employee_id', '=', False))
            elif context.get('assign_to') == 'department':
                args.append(('department_id', '=', False))
        return super(MaintenanceEquipment, self).name_search(name, args=args, operator=operator, limit=limit)

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            team_ids = self.env['maintenance.team'].search([('branch_id', '=', self.branch_id.id)]).ids
            self.maintenance_team_id = False
            if len(team_ids) > 0:
                self.maintenance_team_id = team_ids[0]
            return {'domain': {'maintenance_team_id': [('id', 'in', team_ids)]}}
        else:
            return {'domain': {'maintenance_team_id': []}}

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            self.branch_id = False
            if len(branches) > 0:
                self.branch_id = branches[0]
            return {'domain': {'branch_id': [('id', 'in', branches)]}}
        else:
            return {'domain': {'branch_id': []}}

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     if self.company_id:
    #         branches = self.env['res.branch'].search([('company_id', '=', self.company_id.id)])
    #         self.branch_id = False
    #         if len(branches) > 0:
    #             self.branch_id = branches.ids[0]
    #         return {'domain': {'branch_id': [('id', 'in', branches.ids)]}}
    #     else:
    #         return {'domain': {'branch_id': []}}

    def _create_new_request(self, date):
        self.ensure_one()
        self.env['maintenance.request'].create({
            'name': _('Preventive Maintenance - %s') % self.name,
            'request_date': date,
            'schedule_date': date,
            'category_id': self.category_id.id,
            'equipment_id': self.id,
            'maintenance_type': 'preventive',
            'owner_user_id': self.owner_user_id.id,
            'user_id': self.technician_user_id.id,
            'maintenance_team_id': self.maintenance_team_id.id,
            'duration': self.maintenance_duration,
            'company_id': self.company_id.id or self.env.company.id,
            'branch_id': self.branch_id.id,
            })


class MaintenanceRequest(models.Model):
    _inherit = 'maintenance.request'

    branch_id = fields.Many2one('res.branch', string='Office')#, default=lambda self: self.env.user.branch_id

    @api.onchange('branch_id')
    def _onchange_branch_id(self):
        if self.branch_id:
            team_ids = self.env['maintenance.team'].search([('branch_id', '=', self.branch_id.id)]).ids
            self.maintenance_team_id = False
            if len(team_ids) > 0:
                self.maintenance_team_id = team_ids[0]
            return {'domain': {'maintenance_team_id': [('id', 'in', team_ids)]}}
        else:
            return {'domain': {'maintenance_team_id': []}}

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            self.branch_id = False
            if len(branches) > 0:
                self.branch_id = branches[0]
            return {'domain': {'branch_id': [('id', 'in', branches)]}}
        else:
            return {'domain': {'branch_id': []}}

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     if self.company_id:
    #         branches = self.env['res.branch'].search([('company_id', '=', self.company_id.id)])
    #         self.branch_id = False
    #         if len(branches) > 0:
    #             self.branch_id = branches.ids[0]
    #         return {'domain': {'branch_id': [('id', 'in', branches.ids)]}}
    #     else:
    #         return {'domain': {'branch_id': []}}

    @api.onchange('equipment_id', 'company_id')
    def onchange_equipment_id(self):
        super(MaintenanceRequest, self).onchange_equipment_id()
        if self.equipment_id and self.equipment_id.branch_id:
            self.branch_id = self.equipment_id.branch_id.id


class MaintenanceTeam(models.Model):
    _inherit = 'maintenance.team'

    branch_id = fields.Many2one('res.branch', string='Office')# , default=lambda self: self.env.user.branch_id

    @api.onchange('company_id')
    def _onchange_company_id(self):
        if self.company_id:
            branches = self.env.user.branch_ids.filtered(lambda m: m.company_id.id == self.company_id.id).ids
            self.branch_id = False
            if len(branches) > 0:
                self.branch_id = branches[0]
            return {'domain': {'branch_id': [('id', 'in', branches)]}}
        else:
            return {'domain': {'branch_id': []}}

    # @api.onchange('company_id')
    # def _onchange_company_id(self):
    #     if self.company_id:
    #         branches = self.env['res.branch'].search([('company_id', '=', self.company_id.id)])
    #         self.branch_id = False
    #         if len(branches) > 0:
    #             self.branch_id = branches.ids[0]
    #         return {'domain': {'branch_id': [('id', 'in', branches.ids)]}}
    #     else:
    #         return {'domain': {'branch_id': []}}

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        """
            Override method for apply domain on user
        """
        args = args or []
        context = dict(self.env.context)
        if context.get('branch_id', False):
            args.append(('branch_id', '=', context.get('branch_id')))
        return super(MaintenanceTeam, self).name_search(name, args=args, operator=operator, limit=limit)
