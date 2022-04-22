# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

from odoo import fields, models, api, _


class EmployeeReports(models.TransientModel):
    _name = "employee.head.count"
    _description = "Employee Head Count Report"

    based_on = fields.Selection([('Department', 'Department'), ('Job', 'Job'), ('Manager', 'Manager')],
                                string='Based on')
    department_ids = fields.Many2many('hr.department', string='Department')
    job_ids = fields.Many2many('hr.job', string='Job')
    manager_ids = fields.Many2many('hr.employee', string='Manager')

    def print_reports(self):
        self.ensure_one()
        return self.env.ref('saudi_hr.action_report_hr_employee').report_action(self)

    @api.onchange('based_on')
    def onchange_based_on(self):
        self.department_ids = False
        self.job_ids = False
        self.manager_ids = False

    def get_dept(self):
        data = []
        if self.based_on == 'Department':
            department_domain = [('id', 'in', self.department_ids.ids)] if self.department_ids else []
            departments = self.env['hr.department'].search(department_domain)
            for department in departments:
                data.append(department.name)
        if self.based_on == 'Job':
            job_domain = [('id', 'in', self.job_ids.ids)] if self.job_ids else []
            jobs = self.env['hr.job'].search(job_domain)
            for job in jobs:
                data.append(job.name)
        if self.based_on == 'Manager':
            manager_domain = [('id', 'in', self.manager_ids.ids)] if self.manager_ids else [('manager', '=', True)]
            managers = self.env['hr.employee'].search(manager_domain)
            for manager in managers:
                data.append(manager.name)
        return data

    def get_emp(self, data_id):
        emp = []
        if self.based_on == 'Department':
            dep = self.env['hr.department'].browse(data_id)
            employee = self.env['hr.employee'].search([('department_id', '=', dep.id)])
        if self.based_on == 'Job':
            job = self.env['hr.job'].browse(data_id)
            employee = self.env['hr.employee'].search([('job_id', '=', job.id)])
        if self.based_on == 'Manager':
            manager = self.env['hr.employee'].browse(data_id)
            employee = self.env['hr.employee'].search([('parent_id', '=', manager.id)])
        for rec in employee:
            emp_dict = {'code': rec.code,
                        'name': rec.name,
                        'joining_date': rec.date_of_join,
                        'status': dict(rec._fields['employee_status'].selection).get(rec.employee_status)}
            emp.append(emp_dict)
        return emp
