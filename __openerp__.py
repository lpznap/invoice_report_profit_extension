# -*- coding: utf-8 -*-
{
    'name': "invoice report port profit extension",

    'summary': """""",

    'description': """
        Calculate total profit for invoice report
    """,

    'author': "My Company",
    'website':"",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/openerp/addons/base/module/module_data.xml
    # for the full list
    'category': 'Report',
    'version': '0.1',
    'auto_install': False,
    # any module necessary for this one to work correctly
    'depends': ['base','account_invoice_margin'],
    'demo': [],
    'update_xml': ['invoice_report_profit_extension_view.xml'],
    'installable': True
}