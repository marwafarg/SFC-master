# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Employee Grade On Bonus",
    'summary': """ Employee bonus grade details """,
    'description': """
        Once Employee bonus process will be completed grade will be updated on employee's profile.
     """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr_grade', 'saudi_hr_bonus'],
    'data': [
            'views/bonus_view.xml',
    ],
    'demo': [
        'demo/demo.xml'
    ],
    'images': [
        'static/description/main_screen.jpg'
    ],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'auto_install': False,
}
