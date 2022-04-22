# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Air Allowance",
    'summary': """ HR Air Allowance """,
    'description': """
        By this module we can calculate the air allowances, deduct the amount from employee payslip
     """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'Generic Modules/Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': [
        # 'saudi_hr_contract',
        'saudi_hr_dependent',
        'saudi_hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'data/hr_payroll_data.xml',
        'wizard/generate_air_allowance_view.xml',
        'wizard/generate_annual_ticket.xml',
        'views/air_allowance_view.xml',
        'views/annual_ticket_view.xml',
        'wizard/annual_ticket_report_view.xml',

        'report/empcontract_report_qweb.xml'
    ],
    # only loaded in demonstration mode
    'demo': ['demo/demo.xml'],
    'images': [
        'static/description/main_screen.jpg'
    ],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}
