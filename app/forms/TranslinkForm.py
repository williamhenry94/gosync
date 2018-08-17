from marshmallow import Schema, fields, validate


class TranslinkForm(Schema):

    gocard_number = fields.Str(required=True, validate=[validate.Length(min=16, max=16,
                                                                        error='There should be between {min} and {max} digits.')])
    password = fields.Str(required=True)
