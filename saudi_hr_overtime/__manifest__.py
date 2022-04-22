# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'Middle East Human Resource Overtime',
    'summary': 'Middle East Human Resource Overtime',
    'description': """
        Calculate employee overtime based on employee attendance and overtime limit.
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['hr_attendance',
                # 'saudi_hr_contract'
                ],
    'data': [
        'views/saudi_hr_overtime_view.xml',
    ],
    'demo': [
            'demo/demo.xml',
            'demo/contract_demo.xml',
            ],
    "price": 80,
    "currency": "EUR",
    'images': [
        'static/description/main_screen.jpg'
    ],
    'installable': True,
    'auto_install': False,
}
