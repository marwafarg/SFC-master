# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo.exceptions import UserError
from odoo import models, fields, api, _

clearance_context = False


class ClearanceDepartmentData(models.Model):
    _inherit = 'clearance.department.data'

    department_type = fields.Selection(selection_add=[('it', 'IT')])


class ClearanceDepartment(models.Model):
    _inherit = 'clearance.department'

    it_dept_id = fields.Many2one('hr.employee.clearance', 'IT Department')
    department_type = fields.Selection(selection_add=[('it', 'IT')])


class HrEmployeeClearance(models.Model):
    _inherit = 'hr.employee.clearance'

    it_dept_ids = fields.One2many('equipment.registration', 'it_dept_id', 'IT Departments')
    state = fields.Selection(selection_add=[('emp_dept', 'Waiting IT Approval'),
                    ('it_dept', 'Waiting Finance Approval')])

    def write(self, vals):
        for rec in self:
            if vals.get('it_dept_ids') and self.env.user.employee_id and not self.user_has_groups('hr.group_hr_user')\
                and not self.user_has_groups('saudi_hr.group_line_manager'):
                raise UserError(_("You are not modify departments data please contact your administator."))
        return super(HrEmployeeClearance, self).write(vals)


    def _add_followers(self):
        """
            Add employee and manager in followers
        """
        partner_ids = []
        for rec in self:
            partner_ids.append(rec.employee_id.user_partner_id.id)
            # if rec.state == 'confirm':
            #     hr_groups_config_ids = self.env['hr.groups.configuration'].sudo().search([('branch_id', '=', self.location.id), ('hr_ids', '!=', False)])
            #     if hr_groups_config_ids:
            #         partner_ids = hr_groups_config_ids and [employee.user_id.partner_id.id for employee in
            #                                                 hr_groups_config_ids.hr_ids if employee.user_id] or []
            # elif rec.state == 'emp_dept':
            #     helpdesk_groups_config_ids = self.env['hr.groups.configuration'].sudo().search(
            #         [('branch_id', '=', self.location.id), ('helpdesk_ids', '!=', False)])
            #     if helpdesk_groups_config_ids:
            #         partner_ids = helpdesk_groups_config_ids and [employee.user_id.partner_id.id for employee in
            #                                                       helpdesk_groups_config_ids.helpdesk_ids if employee.user_id] or []
            # elif rec.state == 'it_dept':
            #     finance_groups_config_ids = self.env['hr.groups.configuration'].sudo().search(
            #         [('branch_id', '=', self.location.id), ('finance_ids', '!=', False)])
            #     if finance_groups_config_ids:
            #         partner_ids = finance_groups_config_ids and [employee.user_id.partner_id.id for employee in
            #                                                      finance_groups_config_ids.finance_ids if
            #                                                       employee.user_id] or []
            # elif rec.state == 'finance_dept':
            #     admin_groups_config_ids = self.env['hr.groups.configuration'].sudo().search(
            #         [('branch_id', '=', self.location.id), ('admin_ids', '!=', False)])
            #     if admin_groups_config_ids:
            #         partner_ids = admin_groups_config_ids and [employee.user_id.partner_id.id for employee in
            #                                                    admin_groups_config_ids.admin_ids if
            #                                                      employee.user_id] or []
        self.message_subscribe(partner_ids=partner_ids)

    def clearance_next(self):
        for rec in self:
            if rec.state == 'confirm':
                if 'na' in rec.employee_dept_ids.mapped('item_state'):
                    raise UserError(_('Please Update Employee Department Status.'))
                emp_registration = self.env['hr.employee.registration'].search([('employee_id', '=', self.employee_id.id)])
                if emp_registration:
                    rec.update({'it_dept_ids': [(6, 0, emp_registration.it_dept_ids.ids)]})
                rec.state = 'emp_dept'
                self._add_followers()
            elif rec.state == 'emp_dept':
                if 'na' in rec.it_dept_ids.mapped('item_state'):
                    raise UserError(_('Please Update IT Department Status.'))
                rec.state = 'it_dept'
                clearance_dept_ids = self.env['clearance.department.data'].search([('department_type', '=', 'finance')])
                for clearance_dept_id in clearance_dept_ids:
                    self.env['clearance.department'].create({'department_type': clearance_dept_id.department_type,
                                                             'item': clearance_dept_id.item,
                                                             'item_state': clearance_dept_id.item_state,
                                                             'finance_dept_id': self.id})
                self._add_followers()
            elif rec.state == 'it_dept':
                if 'na' in rec.finance_dept_ids.mapped('item_state'):
                    raise UserError(_('Please Update Finance Department Status.'))
                rec.state = 'finance_dept'
                clearance_dept_ids = self.env['clearance.department.data'].search([('department_type', '=', 'admin')])
                for clearance_dept_id in clearance_dept_ids:
                    self.env['clearance.department'].create({'department_type': clearance_dept_id.department_type,
                                                             'item': clearance_dept_id.item,
                                                             'item_state': clearance_dept_id.item_state,
                                                             'admin_dept_id': self.id})
                self._add_followers()
            elif rec.state == 'finance_dept':
                if 'na' in rec.admin_dept_ids.mapped('item_state'):
                    raise UserError(_('Please Update HR Department Status.'))
                rec.state = 'admin_dept'
