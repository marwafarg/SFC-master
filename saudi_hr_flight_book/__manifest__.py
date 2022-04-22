# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Employee Flight Booking",
    'summary': """Employee Flight Booking details""",
    'description': """
        In case of Business tour/Meeting/Training employee will request to HR Manager for flight booking.
        HR Manager will approve employee request & Admin Manager will book tickets for employee.
        If booking is related to employee's personal work Admin Manager add employee contribution for expense. Which is directly deducted from employee's current month payslip (Salary).
    """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['hr_expense_payment', 'saudi_hr_air_allowance'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/data.xml',
        'views/flight_view.xml',
        'views/menu.xml',
        'wizard/admin_reports_view.xml',
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
