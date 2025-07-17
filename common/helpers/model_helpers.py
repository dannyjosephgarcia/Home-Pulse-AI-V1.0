def validate_subfield_types(item, field_name, field_type):
    if not isinstance(item[field_name], field_type):
        return False
    return True
