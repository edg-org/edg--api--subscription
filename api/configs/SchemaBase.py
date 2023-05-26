from typing import Optional, Set
from pydantic.main import ModelMetaclass, BaseModel

class AllOptional(ModelMetaclass):
    def __new__(cls, name, bases, namespace, **kwargs):
        annotations = namespace.get("__annotations__", {})
        for base in bases:
            annotations.update(base.__annotations__)
        for field in annotations:
            if not field.startswith("__"):
                annotations[field] = (annotations[field] | None)
        namespace["__annotations__"] = annotations
        return super().__new__(cls, name, bases, namespace, **kwargs)


class HideFields(BaseModel):
    class Config:
        hide_fields: Set[str] = set()

    @classmethod
    def __init_subclass__(cls, **kwargs):
        hide_fields = getattr(cls.Config, "hide_fields", set())
        fields = cls.__fields__
        new_fields = {}
        for field_name, field in fields.items():
            if field_name not in hide_fields:
                new_fields[field_name] = field
        cls.__fields__ = new_fields
        super().__init_subclass__(**kwargs)
