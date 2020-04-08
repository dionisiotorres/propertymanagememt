# -*- coding: utf-8 -*-
{
    'name':
    "Property Management System",
    'description':
    """Property Management System for Payment Bill Transporting Analysis""",
    'author':
    "Aung Myo Swe",
    'summary':
    """Property Management System""",
    'website':
    "www.zandotech.com",
    'category':
    'base',
    'version':
    '1.0.9',
    'depends': ['base', 'contacts', 'uom', 'account', 'mail', 'web'],
    'data': [
        'security/property_security.xml',
        'security/ir.model.access.csv',
        'data/pms_config_data.xml',
        'data/pms.api.integration.csv',
        'data/pms.api.integration.line.csv',
        'data/pms_generate_rs_data.xml',
        'data/pms.company.category.csv',
        'data/ir_sequence_data.xml',
        'data/pms_lease_schedular_data.xml',
        'data/pos_run_schedule_data_view.xml',
        'wizard/pms_cancel_wizard_view.xml',
        'wizard/pms_extend_wizard_view.xml',
        'wizard/pms_invoice_wizard_view.xml',
        'wizard/pms_generate_rent_schedule_view.xml',
        'wizard/pms_activate_wizard_view.xml',
        'wizard/pms_terminate_wizard_view.xml',
        'data/pms.utilities.supply.type.csv',
        'data/res.country.state.csv',
        'data/pms.city.csv',
        'data/pms.township.csv',
        'data/pms.calculation.method.csv',
        'data/pms.charge_types.csv',
        'views/pms_property_type_view.xml',
        'views/pms_properties_view.xml',
        'views/pms_floor_views.xml',
        'views/pms_rule_configuration_view.xml',
        'views/pms_format_view.xml',
        'views/pms_leaseterms_view.xml',
        'views/pms_terms_view.xml',
        'views/pms_space_unit_management.xml',
        'views/pms_space_unit_view.xml',
        'views/pms_facilities_view.xml',
        'views/pms_uom_view.xml',
        'views/pms_bank_view.xml',
        'views/pms_city_view.xml',
        'views/pms_township_view.xml',
        'views/pms_country_view.xml',
        'views/pms_currency_view.xml',
        'views/pms_contacts_view.xml',
        'views/pms_department_view.xml',
        'views/pms_company_type.xml',
        'views/pms_space_type.xml',
        'views/pms_lease_aggrement.xml',
        'views/pms_utilities_type.xml',
        'views/pms_equipment_type.xml',
        'views/pms_equipment_view.xml',
        'views/pms_lease_agreement_line_view.xml',
        'views/account_invoice_view.xml',
        'views/pms_api_integration.xml',
        'views/users_view.xml',
        'views/pos_daily_sale_view.xml',
        'views/pms_applicable_charge_type.xml',
        'views/pms_applicable_space_type_view.xml',
        'views/pms_utilities_monthly_view.xml',
        'views/pms_rent_schedule.xml',
        'views/pms_lease_unit_pos_view.xml',
        'views/unit_config_view.xml',
        'views/unit_survey_view.xml',
    ],
    'qweb': ['static/src/xml/*.xml'],
    'installable':
    True,
    'application':
    True,
}
