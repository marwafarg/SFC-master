# -*- coding: utf-8 -*-
# Part of Odoo. See COPYRIGHT & LICENSE files for full copyright and licensing details.

{
    'name': "Accommodation Booking",
    'summary': """ HR Accommodation Booking """,
    'description': """
        In case of Business tour/Client Meeting/Personal Work employee will request to Admin Manager for accommodation booking.
        Admin Manager will add accommodation & expense (company & employee contribution) details & approve employee request.
        Employee contribution (expense) is directly deducted from employee payslip.

        Basic Flow of this module like this:
        New -> Confirm(Employee) -> Approve(HR Officer) -> Book(Admin Manager)add accommodation details -> Generate Expense(Admin Manager) -> Stay Over(Admin Manager)
        """,
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'category': 'HR',
    'version': '1.0',
    'license': 'OPL-1',
    'depends': ['hr_admin', 'hr_expense_payment'],
    'data': [
        'security/ir.model.access.csv',
        'security/security.xml',
        'data/hr_admin_operations_data.xml',
        'data/product_data.xml',
        'views/accomodation_view.xml',
        'wizard/admin_reports_view.xml',
        'views/menu.xml',
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
