from odoo import models, fields, api
from dateutil.relativedelta import relativedelta

class EstateProperty(models.Model):
    _name = "estate.property"
    _description = "Real Estate Property"

    name = fields.Char(string="Title", required=True)
    description = fields.Text(string="Description")
    postcode = fields.Char(string="Postcode")

    # Verfügbarkeit: nicht kopieren + Default in 3 Monaten
    date_availability = fields.Date(
        string="Available From",
        copy=False,
        default=lambda self: fields.Date.today() + relativedelta(months=3),
    )

    expected_price = fields.Float(string="Expected Price", required=True)

    # Selling price: readonly + nicht kopieren
    selling_price = fields.Float(
        string="Selling Price",
        readonly=True,
        copy=False,
    )

    # Standard: 2 Schlafzimmer
    bedrooms = fields.Integer(string="Bedrooms", default=2)

    living_area = fields.Integer(string="Living Area (m²)")
    facades = fields.Integer(string="Facades")
    garage = fields.Boolean(string="Has Garage?")
    garden = fields.Boolean(string="Has Garden?")
    garden_area = fields.Integer(string="Garden Area (m²)")

    # Reserved field: active
    active = fields.Boolean(string="Active", default=True)

    garden_orientation = fields.Selection(
        [
            ('north', 'North'),
            ('south', 'South'),
            ('east', 'East'),
            ('west', 'West')
        ],
        string="Garden Orientation",
    )

        # Many2one: Property Type
    property_type_id = fields.Many2one(
        "estate.property.type",
        string="Property Type",
    )

    # Many2one: Käufer (Kunde)
    buyer_id = fields.Many2one(
        "res.partner",
        string="Buyer",
        copy=False,
    )

    # Many2one: Verkäufer / Makler (Odoo User)
    salesperson_id = fields.Many2one(
        "res.users",
        string="Salesperson",
        default=lambda self: self.env.user,
    )

    # Reserved field: state
    state = fields.Selection(
        [
            ('new', 'New'),
            ('offer_received', 'Offer Received'),
            ('offer_accepted', 'Offer Accepted'),
            ('sold', 'Sold'),
            ('cancelled', 'Cancelled'),
        ],
        string="Status",
        required=True,
        copy=False,
        default='new',
    )

    # Many2many: Tags
    tag_ids = fields.Many2many(
    "estate.property.tag",
    string="Tags"
    )

    # One2many: Offer ids
    offer_ids = fields.One2many(
        "estate.property.offer",
        "property_id",
        string="Offers"
    )

