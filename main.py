import argparse
from codegen import GENERATORS


ccg_parser = argparse.ArgumentParser(
    description="CCG: Generate common code snippets")

ccg_parser.add_argument("name", metavar="name", type=str,
                        help="name of the generator to be used. "
                        "use 'list' to list all generators.")

args = ccg_parser.parse_args()


if args.name in GENERATORS:
    generator_class = GENERATORS[args.name]
    generator = generator_class()
    print(generator.generate())

elif args.name == "list":
    idx = 0
    for cmd, generator in GENERATORS.items():
        print(f"{idx}. {cmd}: {generator.help_text}")
        idx += 1
else:
    print("Generator not found!")
