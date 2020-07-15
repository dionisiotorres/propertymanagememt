import datetime
from odoo import api, fields, models, tools, _


class PMSLeaseActivateWizard(models.TransientModel):
    _name = "pms.unit.facilities.wizard"
    _description = "Unit Facilites Wizard"

    facility_ids = fields.Many2many("pms.facilities",'pms_unit_facilities_rel','space_id','facilites_id', "Facilities")

    @api.multi
    def action_add_facilities(self):
        space_units = self.env['pms.space.unit'].browse(self._context.get('active_id', []))
        if self.facility_ids:
            for fc in self.facility_ids:
                for fcl in fc.facilities_line:
                    vals={
                        'name':fc.name,
                        'digit':fc.utilities_no.digit,
                        'interface_type':fc.interface_type,
                        'meter_type':fc.e_meter_type,
                        'facility_id':fc.id,
                        'facility_line_id':fcl.id,
                        'unit_id':space_units.id,
                        'source_type_id':fcl.source_type_id.id,
                        'property_id':fcl.property_id.id,
                        'lmr_date':fcl.lmr_date,
                        'lmr_value':fcl.lmr_value,
                        'end_date':fcl.end_date,
                        'inuse':True,
                    }
                    self.env['pms.space.unit.facility.lines'].create(vals)
                fc.write({'inuse':True})
        return True

