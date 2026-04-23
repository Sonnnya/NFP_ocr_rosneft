#!/usr/bin/env python
"""Script to dump all Pydantic models from schemas to JSON files.

Usage:
poetry run python ./scripts/dump_schemas.py
"""

import importlib.util
import json
from pathlib import Path

from pydantic import BaseModel


def dump_schemas():
    """Load all models from schemas and dump them to JSON files."""
    schemas_dir = Path(__file__).parent.parent / "app" / "schemas"
    output_dir = Path(__file__).parent.parent / "app" / "prompts" / "schemas"

    # Create output directory
    output_dir.mkdir(exist_ok=True, parents=True)

    # Find all Python files in schemas directory
    schema_files = [f for f in schemas_dir.glob("*.py") if f.name != "__init__.py"]

    for schema_file in schema_files:
        # Load the module dynamically
        spec = importlib.util.spec_from_file_location(
            f"schemas.{schema_file.stem}", schema_file
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Find all Pydantic models in the module
        for attr_name in dir(module):
            attr = getattr(module, attr_name)
            # Check if it's a Pydantic model class (not instance)
            if (
                isinstance(attr, type)
                and issubclass(attr, BaseModel)
                and attr is not BaseModel
            ):
                # Generate JSON schema
                schema = attr.model_json_schema()

                # Save to file
                output_file = output_dir / f"{attr_name}.json"
                with open(output_file, "w", encoding="utf-8") as f:
                    json.dump(schema, f, indent=2, ensure_ascii=False)

                print(f"✓ Dumped {attr_name} to {output_file}")

    print(f"\nAll schemas dumped to {output_dir}")


if __name__ == "__main__":
    dump_schemas()
