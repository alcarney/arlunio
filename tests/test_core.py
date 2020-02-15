import inspect

import arlunio as ar
import py.test


def test_definition_name():
    """Ensure that the returned definition keeps the name of the decorated function."""

    @ar.definition
    def Circle():
        return 1

    assert Circle.__name__ == "Circle"


def test_use_definition_as_tag():
    """Ensure that the definition decorator can be used as a simple tag."""

    @ar.definition
    def z123_(width, height):
        return width

    p = z123_()
    assert p(4, 2) == 4


def test_use_definition_as_function():
    """Ensure that the definition decorator can be used as a function."""

    @ar.definition()
    def Param(width, height):
        return height

    p = Param()
    assert p(4, 2) == 2


def test_definition_constant():
    """Ensure that we can define as constant definition."""

    @ar.definition()
    def Constant():
        return 1

    const = Constant()
    assert const(10, 10) == 1


def test_definition_width_only():
    """Ensure that we can define a definition with respect to width only."""

    @ar.definition()
    def Width(width):
        return width + 1

    w = Width()
    assert w(100, 2) == 101


def test_definition_height_only():
    """Ensure that we can define a definition with respect to height only."""

    @ar.definition()
    def Height(height):
        return height - 1

    h = Height()
    assert h(2, 100) == 99


def test_definition_attributes():
    """Ensure that we can define a definition that takes a number of attributes."""

    @ar.definition()
    def Param(width, height, *, offset=0):
        return (width + height) - offset

    p = Param()
    assert p(1, 1) == 2

    q = Param(offset=2)
    assert q(1, 1) == 0


def test_definition_attribute_validation():
    """Ensure that if an attribute is given a type hint we can perform some basic
    validation on it."""

    @ar.definition()
    def Param(width, height, *, a: int = 0):
        pass

    with py.test.raises(TypeError):
        Param(a="string")


def test_derived_definition():
    """Ensure that we can derive a definition that's based on other definitions."""

    @ar.definition()
    def Adder(width, height):
        return height + width

    @ar.definition()
    def Subber(a: Adder):
        return a - 2

    s = Subber()
    assert s(1, 1) == 0
    assert s(1, 2) == 1


def test_derived_definition_checks_input_annotations():
    """Ensure that any inputs that are not a base definition or annotated are complained
    about."""

    with py.test.raises(TypeError) as err:

        @ar.definition()
        def Parameter(width, height, x):
            return width * height - x

    assert "Unknown input 'x'" in str(err.value)


def test_derived_definition_checks_input_annotation_type():
    """Ensure that any inputs that are annotated with a class that's not a Parameter are
    compained about."""

    with py.test.raises(TypeError) as err:

        @ar.definition()
        def Parameter(width, height, x: int):
            return width * height - x

    assert "Invalid input 'x', type 'int' is not a Definition" in str(err.value)


def test_derived_definition_exposes_properties():
    """Ensure that any properties on base definitions are exposed on the derived
    property."""

    @ar.definition()
    def Base(width, height, *, offset=0):
        return offset

    @ar.definition()
    def Derived(b: Base, *, start=1):
        return start - b

    d = Derived()
    d(1, 1) == 1

    d = Derived(start=5, offset=-1)
    d(1, 1) == 6


def test_derived_definition_exposes_base_definitions():
    """Ensure that any base definitions are available to be inspected."""

    @ar.definition()
    def Base(width, height):
        return 2

    assert Base.definitions == {
        "width": inspect.Parameter.empty,
        "height": inspect.Parameter.empty,
    }

    @ar.definition()
    def Derived(width, base: Base):
        return 4

    assert Derived.definitions == {"width": inspect.Parameter.empty, "base": Base}


def test_derived_definition_attributes_property():
    """Ensure that the attributes property exposes all available attributes on the
    definition."""

    @ar.definition
    def Base(width, height, *, a=1, b=2):
        return 3

    assert Base().attributes == {"a": 1, "b": 2}

    @ar.definition()
    def Derived(base: Base, *, b=3, d=4):
        return 5

    assert Derived().attributes == {"a": 1, "b": 3, "d": 4}


def test_derived_definition_attribs_property():
    """Ensure that the attribs property only exposes the attributes that are directly
    defined on the definition."""

    @ar.definition
    def Base(width, height, *, a=1, b=2):
        return 3

    assert Base().attribs == {"a": 1, "b": 2}

    @ar.definition
    def Derived(base: Base, *, b=3, d=4):
        return 5

    assert Derived().attribs == {"b": 3, "d": 4}