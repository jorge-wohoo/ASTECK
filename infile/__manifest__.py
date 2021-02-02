# -*- coding: utf-8 -*-
{
    'name': "Infile",

    'summary': """
        Comunicación con infile para facturacion electronica""",

    'description': """
        Módulo para la generación de las firmas electrónicas de los documentos tributarios electronicos de la organizacion por medio de Infile
    """,

    'author': "i-tecnologia",
    'website': "https://itecnologiagt.tk",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/master/odoo/addons/base/module/module_data.xml
    # for the full list
    'category': 'Uncategorized',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['base', 'account', 'sale','stock'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'views/templates.xml',
        'views/views.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
}