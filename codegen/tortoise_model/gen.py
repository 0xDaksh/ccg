from typing import List, Tuple

import inquirer
from codegen.generator import Generator

from .handlers import parsers
from .utils import colors, graceful_exit, tuple_to_str, validate_text

model_template = colors.yellow + """
from tortoise import models, fields
from tortoise.contrib.pydantic import pydantic_model_creator
""" + colors.blue + """
class {model_name}(models.Model):
  id = fields.IntField(pk=True)
{fields}
  created_at = fields.DatetimeField(auto_now_add=True)
  updated_at = fields.DatetimeField(auto_now=True)

  def __str__(self):
    return self.{str_field_name}
""" + colors.green + """
{model_name}_Pydantic = pydantic_model_creator({model_name}, name='{model_name}')
{model_name}In_Pydantic = pydantic_model_creator({model_name}, name='{model_name}In', exclude_readonly=True)
"""


def parse_gen_str(model_name: str, gen_str: str) -> Tuple[List[str], str]:
    fields_str = ''
    field_names = []
    fields = gen_str.split(" ")

    for field in fields:
        values = field.split(":")
        field_name = values[0]
        field_names.append(field_name)

        if not field_name.isidentifier():
            graceful_exit(f'Field name {field_name} is invalid!')

        try:
            field_type = values[1].lower()
        except IndexError:
            graceful_exit(f"you forgot to provide the type for {field_name}!")

        if field_type not in parsers:
            graceful_exit(
                f"{field_name}'s field type of {field_type} does not exist!")

        if field_type in ('fk', 'm2m'):
            model_name_parsed = model_name

            if '.' in model_name_parsed:
                model_name_parsed = model_name_parsed.split(".")[1]

            tpl, kv = parsers[field_type](model_name_parsed, values)
        else:
            tpl, kv = parsers[field_type](values)

        char_fields_str = tpl.format(", ".join(map(tuple_to_str,
                                                   kv.items()))) + "\n"

        # left pad each line
        fields_str += "".join(
            ["  " + x + "\n" for x in char_fields_str.strip().split("\n")])

    return field_names, fields_str


class TortoiseModel(Generator):
    help_text = "Generate tortoise orm models."

    def generate(_self) -> str:
        print(
            f"\n{colors.bs}Fields such as ID, created_at, updated_at are auto generated.{colors.be}\n")
        ques = [
            inquirer.Text('model_name',
                          message='Enter your model name', validate=validate_text),
            inquirer.Text('field_str',
                          message='Enter the model gen commands', validate=lambda _, x: x.strip() != '')
        ]
        ans = inquirer.prompt(ques)
        model_name = ans['model_name'].strip()
        gen_str = ans['field_str'].strip()

        field_names, field_content = parse_gen_str(model_name, gen_str)

        obj = inquirer.prompt(
            [inquirer.List(
                name="str_field_name",
                message="Choose the field to be used in __str__ method",
                choices=field_names
            )]
        )

        generated = model_template.format(
            model_name=model_name, fields=field_content, str_field_name=obj['str_field_name'])

        print("✨ Sucessfully Generated:")
        return generated
