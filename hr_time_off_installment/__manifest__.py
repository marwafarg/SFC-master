# -*- coding: utf-8 -*-
# Part of odoo. See LICENSE file for full copyright and licensing details.

{
    'name': "HR Time off Installment",
    'summary': """ HR Time off Installment""",
    'description': """
       HR Time off Installment
    """,
    'author': "erp-bank",
    'category': 'Generic Modules/Human Resources',
    'version': '1.0',
    'depends': [
        'base','hr','hr_contract','hr_holidays','portal','mail','hr_work_entry_contract','sync_employee_advance_salary'
    ],
    'data': [
        'data/demo.xml',
        'security/ir.model.access.csv',
        'security/ir_rule.xml',
        'data/installment_method_data.xml',
        'data/ir_sequence.xml',
        'views/installment_calculation_method_view.xml',
        'views/hr_time_off_installment_view.xml',
        'views/hr_leave_view.xml',
        'wizard/create_journal_entry_view.xml',
    ],
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
