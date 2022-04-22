# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "HR Employee Card",
    'summary': """ HR Employee Card """,
    'description': """
        Employee can put request for their business card, ID card and access card. HR Officer can print the ID card and Business card.
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'report/icard_report_view.xml',
        'views/hr_employee_card_view.xml',
        'views/menu.xml',
        'wizard/business_card.xml',
    ],
    'demo': [
        'demo/employee_card_demo.xml',
    ],
    'images': [
        'static/description/main_screen.jpg'
    ],
    "price": 0.0,
    "currency": "EUR",
    'installable': True,
    'application': True,
    'auto_install': False,
}
