import json
from typing import Any, Dict, List, Tuple

from .utils import graceful_exit, handle_common_attrs, pluralize


def handle_char(field_arr: List[str]) -> Tuple[str, Dict[str, Any]]:
    tpl = f'{field_arr[0]} = ' + 'fields.CharField({})'
    kv = {}

    try:
        kv['length'] = field_arr[2]
    except IndexError:
        kv['length'] = 255

    try:
        attrs = field_arr[3]
        for attr in attrs.split(","):
            handle_common_attrs(field_arr, kv, attr, '^default=\w+$')
    except IndexError:
        pass

    return tpl, kv


def handle_int(field_arr: List[str]) -> Tuple[str, Dict[str, Any]]:
    tpl = f'{field_arr[0]} = ' + 'fields.IntField({})'
    kv = {}

    try:
        attrs = field_arr[2]
        for attr in attrs.split(","):
            handle_common_attrs(field_arr, kv, attr, '^default=[\+\-]?\d+$')
    except IndexError:
        pass

    return tpl, kv


def handle_float(field_arr: List[str]) -> Tuple[str, Dict[str, Any]]:
    tpl = f'{field_arr[0]} = ' + 'fields.FloatField({})'
    kv = {}

    try:
        attrs = field_arr[2]
        for attr in attrs.split(","):
            handle_common_attrs(field_arr, kv, attr,
                                '^default=[\+\-]?\d+\.\d+$')
    except IndexError:
        pass

    return tpl, kv


def handle_decimal(field_arr: List[str]) -> Tuple[str, Dict[str, Any]]:
    tpl = f'{field_arr[0]} = ' + 'fields.DecimalField({})'
    kv = {}

    try:
        attrs = field_arr[2]
        for attr in attrs.split(","):
            handle_common_attrs(field_arr, kv, attr,
                                '^default=[\+\-]?\d+\.\d+$')
    except IndexError:
        pass

    return tpl, kv


def handle_datetime_field(field_arr: List[str]) -> Tuple[str, Dict[str, Any]]:
    tpl = f'{field_arr[0]} = ' + 'fields.DatetimeField({})'
    kv = {}

    try:
        attrs = field_arr[2].lower()

        for attr in attrs.split(","):
            if attr == 'auto_now_add' or attr == 'auto_now':
                kv[attr] = True
    except IndexError:
        pass

    return tpl, kv


def handle_text_field(field_arr: List[str]) -> Tuple[str, Dict[str, Any]]:
    tpl = f'{field_arr[0]} = ' + 'fields.TextField({})'
    kv = {}

    try:
        attrs = field_arr[2]
        for attr in attrs.split(","):
            handle_common_attrs(field_arr, kv, attr, None)
    except IndexError:
        pass

    return tpl, kv


def handle_fk_field(model_name: str, field_arr: List[str]) -> Tuple[str, Dict[str, Any]]:
    tpl = f'{field_arr[0]} = ' + 'fields.ForeignKeyField({}, {})'
    kv = {}

    try:
        relation_on = field_arr[2]

        if not (relation_on.isidentifier() or re.search('^\w+\.?\w+$', relation_on)):
            graceful_exit(
                "Please provide a valid name for the fk field of"
                f" {field_arr[0]} instead of {relation_on}")
        else:
            tpl = tpl.format(json.dumps(relation_on), '{}')
    except IndexError:
        graceful_exit(
            f"Please provide a model name for your fk on {field_arr[0]}")

    kv['related_name'] = json.dumps(pluralize(model_name.lower()))

    try:
        attrs = field_arr[3]
        for attr in attrs.split(','):
            handle_common_attrs(field_arr, kv, attr, None)
    except IndexError:
        pass

    tpl = f"# type for reverse relation: fields.ReverseRelation[\"{model_name}\"]\n" + tpl
    tpl = f"# type: fields.ForeignKeyRelation[{relation_on}]\n" + tpl

    return tpl, kv


def handle_m2m_field(model_name, field_arr: List[str]) -> Tuple[str, Dict[str, Any]]:
    tpl = f'{field_arr[0]} = ' + 'fields.ManyToManyField({}, {})'
    kv = {}

    try:
        relation_on = field_arr[2]

        if not (relation_on.isidentifier() or re.search('^\w+\.?\w+$', relation_on)):
            graceful_exit(
                f"{relation_on} is not a valid name for {field_arr[0]}."
                " Since its m2m")
        else:
            tpl = tpl.format(json.dumps(relation_on), '{}')
    except IndexError:
        graceful_exit(
            f"Please provide a model name for your m2m field on {field_arr[0]}")

    kv['related_name'] = json.dumps(pluralize(model_name.lower()))
    kv['through'] = json.dumps(model_name.lower() + "_" + field_arr[0].lower())

    try:
        attrs = field_arr[3]
        for attr in attrs.split(','):
            handle_common_attrs(field_arr, kv, attr, None)
    except IndexError:
        pass

    tpl = f"# type for reverse relation: fields.ReverseRelation[\"{model_name}\"]\n" + tpl
    tpl = f"# type: fields.ManyToManyRelation[\"{relation_on}\"]\n" + tpl

    return tpl, kv


parsers = {
    'int': handle_int,
    'float': handle_float,
    'decimal': handle_decimal,
    'char': handle_char,
    'text': handle_text_field,
    'datetime': handle_datetime_field,
    'fk': handle_fk_field,
    'm2m': handle_m2m_field
}
