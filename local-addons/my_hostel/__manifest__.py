{
        'name': 'Hostel Management',
        'summary': 'Manage Hostel easily',
        'description' : "Efficiently manage the entire residential facility in the school",
        'author' : 'Raphaël O.',
        'website' : 'https://github.com/Raphael-Carina',
        'category' : 'Uncategorized',
        'version': '17.0.1.0.0',
        'depends' : ['base'],

        'data' : [
            "security/hostel_security.xml",
            "security/ir.model.access.csv",
            "data/data.xml",
            "views/hostel.xml",
        ],

        'assets': {
            'web.assets_backend': [
                'my_hostel/static/description/icon.png',
            ],
        },
}
