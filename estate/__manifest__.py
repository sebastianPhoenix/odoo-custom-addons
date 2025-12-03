{
    'name': 'Estate',
    'summary': 'Real estate tutorial module',
    'version': '1.1.0',
    'author': 'Sebastian',
    'license': 'LGPL-3',
    'category': 'Tutorial',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',
        'views/estate_property_views.xml',
        'views/estate_property_type_views.xml',
        'views/estate_menus.xml',
    ],
    'installable': True,
    'application': True,
}