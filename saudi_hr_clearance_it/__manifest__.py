# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "HR Clearance IT",
    'summary': """ HR Clearance IT""",
    'description': """HR Clearance """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr_clearance', 'saudi_hr_it_operations'],
    'data': [
            'security/ir_rule.xml',
            'data/employee_clearance_data.xml',
            'views/hr_employee_clearance_view.xml',
            'reports/hr_employee_clearance_report.xml',
            ],
    'images': [],
    "price": 0.0,
    'demo': [
        # 'demo/demo.xml'
    ],
    'installable': True,
    'auto_install': False,
}
