import json
import re
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
        handle_common_attrs(field_arr, kv, field_arr[3], {
                            'default_expr': '^default=\w+$'})
    except IndexError:
        pass

    return tpl, kv


def handle_int(field_arr: List[str]) -> Tuple[str, Dict[str, Any]]:
    tpl = f'{field_arr[0]} = ' + 'fields.IntField({})'
    kv = {}

    try:
        handle_common_attrs(
            field_arr, kv, field_arr[2], {'default_expr': '^default=[\+\-]?\d+$'})
    except IndexError:
        pass

    return tpl, kv


def handle_float(field_arr: List[str]) -> Tuple[str, Dict[str, Any]]:
    tpl = f'{field_arr[0]} = ' + 'fields.FloatField({})'
    kv = {}

    try:
        handle_common_attrs(field_arr, kv, field_arr[2],
                            {'default_expr': '^default=[\+\-]?\d+\.\d+$'})
    except IndexError:
        pass

    return tpl, kv


def handle_decimal(field_arr: List[str]) -> Tuple[str, Dict[str, Any]]:
    tpl = f'{field_arr[0]} = ' + 'fields.DecimalField({})'
    kv = {}

    try:
        handle_common_attrs(field_arr, kv, field_arr[2],
                            {'default_expr': '^default=[\+\-]?\d+\.\d+$'})
    except IndexError:
        pass

    return tpl, kv


def handle_bool(field_arr: List[str]) -> Tuple[str, Dict[str, Any]]:
    tpl = f'{field_arr[0]} = ' + 'fields.BooleanField({})'
    kv = {}

    try:
        handle_common_attrs(field_arr, kv, field_arr[2],
                            {'default_expr': '^default=(True|False)$', 'default_fn': str})
    except IndexError:
        pass

    return tpl, kv


def handle_datetime_field(field_arr: List[str]) -> Tuple[str, Dict[str, Any]]:
    tpl = f'{field_arr[0]} = ' + 'fields.DatetimeField({})'
    kv = {}

    try:
        attrs = field_arr[2].lower()
        custom_attrs = {'auto_now_add': True, 'auto_now': True}

        handle_common_attrs(field_arr, kv, field_arr[2], {
                            'custom_attrs': custom_attrs})
    except IndexError:
        pass

    return tpl, kv


def handle_text_field(field_arr: List[str]) -> Tuple[str, Dict[str, Any]]:
    tpl = f'{field_arr[0]} = ' + 'fields.TextField({})'
    kv = {}

    try:
        handle_common_attrs(field_arr, kv, field_arr[2], {})
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
        handle_common_attrs(field_arr, kv, field_arr[3], {})
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
        handle_common_attrs(field_arr, kv, field_arr[3], {})
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
    'bool': handle_bool,
    'datetime': handle_datetime_field,
    'fk': handle_fk_field,
    'm2m': handle_m2m_field
}
