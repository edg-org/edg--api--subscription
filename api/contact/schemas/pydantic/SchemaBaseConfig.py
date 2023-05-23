from typing import Optional

from pydantic.main import ModelMetaclass


class AllOptional(ModelMetaclass):
    def __new__(cls, name, bases, namespace, **kwargs):
        annotations = namespace.get('__annotations__', {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith('__'):
                annotations[field] = annotations[field] | None
        namespace['__annotations__'] = annotations
        return super().__new__(cls, name, bases, namespace, **kwargs)


class OmitFields(ModelMetaclass):
    def __new__(self, name, bases, namespaces, **kwargs):
        omit_fields = getattr(namespaces.get("Config", {}), "omit_fields", {})
        fields = namespaces.get('__fields__', {})
        annotations = namespaces.get('__annotations__', {})
        for base in bases:
            fields.update(base.__fields__)
            annotations.update(base.__annotations__)
        merged_keys = fields.keys() & annotations.keys()
        [merged_keys.add(field) for field in fields]
        new_fields = {}
        new_annotations = {}
        for field in merged_keys:
            if not field.startswith('__') and field not in omit_fields:
                new_annotations[field] = annotations.get(field, fields[field].type_)
                new_fields[field] = fields[field]
        namespaces['__annotations__'] = new_annotations
        namespaces['__fields__'] = new_fields
        return super().__new__(self, name, bases, namespaces, **kwargs)


