# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Employee Profile Information",
    'summary': """ Employee Profile Information""",
    'description': """
        Employee Profile Information About Experience, Qualification And Certification
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'Generic Modules/Human Resources',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'views/email_template_view.xml',
        'views/employee_view.xml',
        'data/cron.xml',
        'data/mail_template.xml',
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
