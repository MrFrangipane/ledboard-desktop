from typing import get_type_hints, Annotated, get_origin, get_args

from ledboard.serial_.types import SerializationAnnotation


class CHeaderExporter:

    def __init__(self):
        self._output = list()
        self._indent_level = 0

    def _append_line(self, text):
        self._output.append(("    " * self._indent_level) + text)

    def export(self, object_) -> str:
        self._output = list()
        self._indent_level = 0

        default_object = type(object_)()
        self._render_object(default_object)
        return "\n".join(self._output)

    def _render_object(self, object_):
        self._append_line(f"struct {type(object_).__name__} {{")
        self._indent_level += 1

        items = get_type_hints(object_, include_extras=True).items()
        for name, type_hint in items:
            self._render_attribute(name, getattr(object_, name), type_hint)

        self._indent_level -= 1
        self._append_line("};")

    def _render_attribute(self, name, value, type_hint):
        if get_origin(type_hint) == Annotated:
            type_, annotation = get_args(type_hint)
            if get_origin(type_) == list:
                self._render_list(name, value, type_)
            else:
                self._render_basic_type(name, value, type_, annotation)
        else:
            self._render_object(type_hint)

    def _render_basic_type(self, name, value, type_, annotation):
        assert isinstance(annotation, SerializationAnnotation)

        c_name = self._render_attribute_name(name)
        c_type = annotation.c_name
        c_value = self._render_basic_value(value, type_, annotation)

        if type_ == bytes:
            c_name += f"[{annotation.length}]"

        elif type_ == str:
            c_name += f"[{annotation.length}]"

        self._append_line(f"{c_type} {c_name} = {c_value};")

    def _render_list(self, name, value, type_):
        # FIXME: check Annotation length
        sub_hint = get_args(type_)[0]
        type_, annotation = get_args(sub_hint)
        if type_ in [bool, int, float]:
            c_name = self._render_attribute_name(name)
            c_name += f"[{len(value)}]"
            c_type = annotation.c_name
            c_value = f"{{{', '.join([self._render_basic_value(item, type_, annotation) for item in value])}}}"
            self._append_line(f"{c_type} {c_name} = {c_value};")
        else:
            pass

    @staticmethod
    def _render_attribute_name(name):
        return "".join([word.capitalize() if i > 0 else word for i, word in enumerate(name.split("_"))])

    @staticmethod
    def _render_basic_value(value, type_, annotation):  # FIXME find a better name
        if type_ == bytes:
            return f"{{0x{', 0x'.join(value.hex(sep=' ').split(' '))}}}"

        elif type_ == bool:
            return str(value).lower()

        elif type_ == str:
            if len(value) < annotation.length:
                return f'"{ value + " " * (annotation.length - len(value)) }"'
            else:
                return f'"{ value[:annotation.length] }"'

        elif type_ in [float, int]:
            return str(value)
