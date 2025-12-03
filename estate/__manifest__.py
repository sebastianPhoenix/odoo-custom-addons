{
    'name': 'Estate',
    'summary': 'Real estate tutorial module',
    'version': '1.0.0',
    'author': 'Sebastian',
    'license': 'LGPL-3',
    'category': 'Tutorial',
    'depends': ['base'],
    'data': [
        'security/ir.model.access.csv',      # Security
        'views/estate_property_views.xml',   # Action
        'views/estate_menus.xml',            # Menüs
    ],
    'installable': True,
    'application': True,
}