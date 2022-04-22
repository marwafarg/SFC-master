# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'HR Warning',
    'summary': 'Employee Salary, Employees Details',
    'description': """
        Generate Warning and send individual or group warning mail""",
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': [
        'mail',
        'hr',
        'saudi_hr_payroll',
        'saudi_hr',
    ],
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'data/warning.xml',
        'data/warning_types.xml',
        'data/mail_template.xml',
        'views/issue_warning.xml',
        'views/warning_type_view.xml',
        'views/hr_view.xml',
        'report/issue_warning_report_template.xml',
    ],
    'qweb': [],
    'demo': [
        'demo/demo.xml',
    ],
    'images': [],
    'installable': True,
    'application': True,
    'auto_install': False,
}
