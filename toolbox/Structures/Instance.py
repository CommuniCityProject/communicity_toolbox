from __future__ import annotations

from typing import Any, List


class Instance:
    """Structure used to store the output of a machine learning model.
    The stored attributes can be plain values (int, float, str, etc.),
    Structures (BoundingBox, keypoints, etc.) or another instances.

    Example:
        instance = Instance().set("label", "dog").set("confidence", 0.8)
        confidence = instance.confidence

    Methods:
        set(name, value) -> Instance
        has(name) -> bool
        remove(name)

    Overloaded operators:
        __getattr__
        __getitem__
        __eq__
        __iter__
        __str__

    Properties (read-only):
        fields (List[str]): List of names of the attributes set.
    """

    def __init__(self):
        """Initialize an empty Instance.
        """
        self._fields = {}

    def set(self, name: str, value: Any) -> Instance:
        """Store a value with the given name.

        Args:
            name (str): Name that will be used to access the value.
            value (Any): Any object.
        """
        self._fields[name] = value
        return self

    def get(self, name: str, default: Any = None) -> Any:
        """Get a an attribute by its name.

        Args:
            name (str): The name of the attribute.
            default (Any, optional): Default value in case the attribute does
                not exist. Defaults to None.

        Returns:
            Any: The value of the attribute or the default value if it does not
                exists.
        """
        if name in self._fields:
            return self._fields[name]
        return default

    def __getattr__(self, name: str) -> Any:
        """Get an attribute by its name.

        Args:
            name (str): Name of the attribute.

        Raises:
            AttributeError: If the instance has no attribute named ``name``.

        Returns:
            Any: The stored value with the key ``name``.
        """
        if name not in self._fields:
            raise AttributeError(
                f"Instance has no field '{name}' ({list(self._fields.keys())})")
        return self._fields[name]

    def __getitem__(self, name: str) -> Any:
        """Get an attribute by its name.

        Args:
            name (str): Name of the attribute.

        Raises:
            AttributeError: If the instance has no attribute named ``name``.

        Returns:
            Any: The stored value with the key ``name``.
        """
        if name not in self._fields:
            raise AttributeError(
                f"Instance has no field '{name}' ({list(self._fields.keys())})")
        return self._fields[name]

    @property
    def fields(self) -> List[str]:
        """List of names of the attributes set.

        Returns:
            List[str]: List of attribute names.
        """
        return list(self._fields.keys())

    def has(self, name: str) -> bool:
        """Check if the instance has an attribute named ``name``.

        Args:
            name (str): The name of an attribute.

        Returns:
            bool: True if an attribute with the given name exits.
        """
        return name in self._fields

    def remove(self, name: str):
        """Remove an attribute from the instance by its name.

        Args:
            name (str): Name of the attribute to remove.
        """
        del self._fields[name]

    def __eq__(self, other: Instance) -> bool:
        if not isinstance(other, Instance):
            return False
        eq = True
        for f in self.fields:
            if f not in other.fields:
                return False
            eq = eq and self._fields[f] == other._fields[f]
        return eq

    # Enable dict conversion with ``dict(instance)``
    def __iter__(self):
        for f in self.fields:
            yield (f, self._fields[f])

    def __str__(self):
        return str(dict(self))
