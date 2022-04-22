# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Multi Branches',
    'version': '1.3',
    'summary': 'Application provides functionality of manage multi branches for companies.',
    'sequence': 30,
    'description': """
        This application provide functionality of manage multi branches for Company.
        Multi Branches functionality covered in CRM, Sales, Purchase, Account, Warehouse, Locations and Inventory.
        Also maintain User and Manager level access rights.
    """,
    'category': 'Sales/Accounting',
    'author': 'erp-bank.',
    'website': 'http://www.erp-bank.com',
    'depends': ['sale_management', 'purchase', 'sale_stock', 'crm', 'stock_account'],
    'data': [
        'security/multi_branches_security.xml',
        'security/ir.model.access.csv',
        'data/branch_data.xml',
        'views/res_branch.xml',
        'views/res_config_settings_view.xml',
        'views/res_partner_view.xml',
        'views/res_users_view.xml',
        'views/stock_view.xml',
        'views/crm_lead_view.xml',
        'views/sale_view.xml',
        'views/account_payment_view.xml',
        'views/purchase_view.xml',
        'views/account_move.xml',
        # 'views/products_view.xml',
        'views/account_bank_statement.xml',
        # 'views/hr_employee_views.xml',
        'menu.xml',
        ],
    'demo': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'OPL-1'
}