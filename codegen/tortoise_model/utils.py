import json
import re
from typing import Any, Dict, List, Tuple


class colors:
    bs = '\033[1m'
    be = '\033[0;0m'
    yellow = "\u001b[33m"
    blue = "\u001b[34m"
    green = "\u001b[32m"


def validate_text(_, x: str) -> bool:
    if x.strip() == "":
        return False

    if " " in x.strip():
        return False

    return True


def tuple_to_str(x: Tuple[Any, Any]) -> str: return f"{x[0]}={x[1]}"


def graceful_exit(msg: str):
    print(msg)
    exit(0)


def pluralize(txt: str) -> str:
    if not txt.endswith("s"):
        txt += "s"

    return txt


def handle_common_attrs(
    field_arr: List[str],
    kv: Dict[str, Any],
    attr_string: str,
    opts: Dict[str, Any]
):
    for attr in attr_string.split(","):
        attr = attr.strip()
        attr_lower = attr.lower()
        if attr_lower == 'null' or attr_lower == 'unique':
            kv[attr_lower] = True
        elif 'default_expr' in opts and re.search(opts['default_expr'], attr):
            value = attr.split("=")[1]
            fn = opts['default_fn'] if 'default_fn' in opts else json.dumps
            kv['default'] = fn(value)
        elif 'custom_attrs' in opts and attr_lower in opts['custom_attrs']:
            kv[attr_lower] = opts['custom_attrs'][attr_lower]
        else:
            graceful_exit(
                f"\n{colors.bs}Attribute {attr} was not found for {field_arr[1]} in {field_arr[0]}."
                f" Use it without quotations!{colors.be}")
