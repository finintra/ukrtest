{
    'name': 'Marketing Cost',

    'summary': 'Marketing Cost',

    'author': 'Kitworks Systems',
    'website': 'https://kitworks.systems/',

    'category': 'Other Category',
    'license': 'OPL-1',
    'version': '15.0.1.0.3',
    'depends': [
        'utm',
        'crm',
        'sale',
        'report_xlsx',
        'generic_mixin',
    ],
    'data': [
        'security/product_security.xml',
        'security/ir.model.access.csv',

        'views/marketing_views.xml',
        'wizard/kw_marketing_cost_wizard_view.xml',
    ],
    'demo': [
        'demo/demo.xml',
    ],
    'installable': True,

    'images': [
        'static/description/cover.png',
        'static/description/icon.png',
    ],

    'post_init_hook': 'kw_utm_str_post_init_hook',
}
