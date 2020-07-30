from odoo import models, fields, api, tools

class PMSSpaceFacilities(models.Model):
    _name = 'pms.space.facilities'
    _description = "Space Facilities"
    _auto = False

    name = fields.Char(default="Utilities No",
                       related='utilities_no.name')
    utilities_type_id = fields.Many2one('pms.utilities.type',
                                        "Utilities Type")
    utilities_no = fields.Many2one("pms.equipment","Utilities No")
    interface_type = fields.Selection([('auto', 'Auto'), ('manual', 'Manual'),
                                       ('mobile', 'Mobile')],
                                      "Data Interface Type")
    inuse = fields.Boolean("In Use")
    property_id = fields.Many2one("pms.properties",
                                  "Property")
    install_date = fields.Date("Installation Date")
    meter_type = fields.Char("Meter Type")
    active = fields.Boolean("Active")

    @api.model_cr  # cr
    def init(self):
          tools.drop_view_if_exists(self.env.cr, self._table)
          self._cr.execute("""create or replace view pms_space_facilities as 
                (SELECT fac.id,
                    fac.name AS name,
                    fac.utilities_type_id as utilities_type_id,
                    fac.utilities_no as utilities_no, 
                    fac.interface_type AS interface_type,
                    fac.inuse AS inuse,
                    fac.property_id AS property_id, 
                    fac.install_date AS install_date,
                    fac.meter_type AS meter_type,
                    fac.active AS active             
                FROM 
                    pms_facilities fac
                WHERE 
                    fac.inuse = false)""")
    
    @api.one
    def select_values(self):
        space_units = self.env['pms.space.unit'].browse(self._context.get('active_id', []))
        facility = self.browse(self._context.get('selection_id', []))
        facilities_line = self.env['pms.facility.lines'].search([('facility_id','=',self._context.get('selection_id', []))])
        print(facilities_line)
        for fcl in facilities_line:
            vals={
                'name':fcl.facility_id.name,
                'digit':fcl.facility_id.utilities_no.digit,
                'interface_type':fcl.facility_id.interface_type,
                'meter_type':fcl.facility_id.meter_type,
                'facility_id':fcl.facility_id.id,
                'facility_line_id':fcl.id,
                'unit_id':space_units.id,
                'source_type_id':fcl.source_type_id.id,
                'property_id':fcl.property_id.id,
                'start_reading_date':fcl.start_date,
                'start_reading_value':fcl.initial_value,
                'end_date':fcl.end_date,
                'inuse':True,
            }
            self.env['pms.space.unit.facility.lines'].create(vals)
            fcl.facility_id.write({'inuse':True})
        return {'type': 'ir.actions.act_window_close'}
