# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "Returned Date",
    'summary': """ Returned Date""",
    'description': """
       Returned Date
    """,
    'author': "erp-bank",
    'category': 'Generic Modules/Human Resources',
    'version': '1.0',
    'depends': [
        'base','hr','hr_holidays','hr_time_off_installment','hr_payroll'
    ],
    'data': [
        'views/hr_leave_view.xml',
    ],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}
