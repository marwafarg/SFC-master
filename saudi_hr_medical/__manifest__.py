# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Employee Insurance & claim",
    'summary': """ Employee Insurance & claim details""",
    'description': """
        Manage employee insurance details.
        Generate Expense invoice for Insurance premium.
        Automatic invoice creation for Insurance premium.
        Insurance details available on employees profile.
        Manage insurance claim details.
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['saudi_hr', 'attachment_indexation', 'account', 'saudi_hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/product_data.xml',
        'data/email_template_data.xml',
        'data/cron.xml',
        'views/hr_employee_medical_view.xml',
        'reports/insurance_details_report.xml',
        'wizard/insurance_premium_multi_invoice_view.xml',
        'views/menu.xml',
    ],
    'demo': [
        'demo/employee_demo.xml',
    ],
    "price": 80,
    "currency": "EUR",
    'images': [
        'static/description/main_screen.jpg'
    ],
    'installable': True,
    'auto_install': False,
}
