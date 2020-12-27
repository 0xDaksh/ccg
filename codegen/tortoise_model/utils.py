import json
import re
from typing import Any, Dict, List, Tuple

bs = '\033[1m'
be = '\033[0;0m'


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
    attr: str,
    expr: str
):
    attr = attr.lower()
    if attr == 'null' or attr == 'unique':
        kv[attr] = True
    elif expr and re.search(expr, attr):
        kv['default'] = json.dumps(attr.split("default=")[1])
    else:
        graceful_exit(
            f"\n{bs}Attribute {attr} was not found for {field_arr[1]} in {field_arr[0]}."
            f" Use it without quotations!{be}")
