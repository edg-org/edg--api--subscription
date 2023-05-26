from typing import Optional, Set

from pydantic.main import ModelMetaclass, BaseModel


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


class OmitFields(BaseModel):
    class Config:
        omit_fields: Set[str] = set()

    @classmethod
    def __init_subclass__(cls, **kwargs):
        omit_fields = getattr(cls.Config, "omit_fields", set())
        fields = cls.__fields__
        new_fields = {}

        for field_name, field in fields.items():
            if field_name not in omit_fields:
                new_fields[field_name] = field

        cls.__fields__ = new_fields

        super().__init_subclass__(**kwargs)
