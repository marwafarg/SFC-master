# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Saudi HR: GOSI Contribution",
    'summary': """Saudi HR GOSI Contribution""",
    'description': """
        The General Organization for Social Insurance (GOSI) is a Saudi Arabian government agency concerned with social insurance in the country.
        Calculations for the GOSI are based on earning of an employee, employee's nationality and deduct the amount from employee payslip.
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'Generic Modules/Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr',
                'hr_payroll',
                # 'sync_hr_payroll'
                ],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/hr_payroll_data.xml',
        'views/hr_employee_gosi_view.xml',
        'views/hr_payroll_view.xml',
    ],
    'demo': [
        'demo/employee_gosi_demo.xml',
    ],
    'images': [
        'static/description/main_screen.jpg'
    ],
    "price": 250.0,
    "currency": "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}
