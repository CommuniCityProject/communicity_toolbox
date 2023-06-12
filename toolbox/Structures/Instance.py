from __future__ import annotations

from typing import Any, List, Optional


class Instance:
    """Structure used to store the output of a machine learning model.

    Overloaded operators:
        __getattr__
        __getitem__
        __setattr__
        __eq__
        __iter__
        __str__

    Example:
        instance = Instance().set("label", "dog").set("confidence", 0.8)
        confidence = instance.confidence
    """

    def __init__(self, fields: Optional[dict] = None):
        """Initialize an Instance. If fields is not None, it will be used to
        set the initial attributes.

        Args:
            fields (Optional[dict], optional): Optional values to set.
                Defaults to None.
        """
        self._fields = {}
        if fields is not None:
            self.set_dict(fields)

    def set_dict(self, fields: dict) -> Instance:
        """Set multiple values at once. The keys of the dictionary will be used
        as the names of the attributes.

        Args:
            fields (dict): Dictionary of values to set.

        Returns:
            Instance: self
        """
        for key, value in fields.items():
            self.set(key, value)
        return self

    def set(self, name: str, value: Any) -> Instance:
        """Store a value with the given name.

        Args:
            name (str): Name that will be used to access the value.
            value (Any): Any object.

        Returns:
            Instance: Self.
        """
        self._fields[name] = value
        return self

    def get(self, name: str, default: Any = None) -> Any:
        """Get an attribute by its name.

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

    def __setattr__(self, name: str, value: Any) -> Instance:
        """Set an the value of an existing attribute.

        Args:
            name (str): Name of the attribute.
            value (Any): Value to set.

        Returns:
            Instance: Self.
        """
        if name.startswith("_") or name in self.__dict__:
            super(Instance, self).__setattr__(name, value)
        else:
            if name not in self._fields:
                raise AttributeError(
                    f"Instance has no field '{name}' "
                    f"({list(self._fields.keys())})")
            self._fields[name] = value
            return self

    def __getattr__(self, name: str) -> Any:
        """Get an attribute by its name.

        Args:
            name (str): Name of the attribute.

        Raises:
            AttributeError: If the instance has no attribute named ``name``.

        Returns:
            Any: The stored value with the key ``name``.
        """
        if name.startswith("_") or name in self.__dict__:
            return super(Instance, self).__getattribute__(name)
        if name not in self._fields:
            raise AttributeError(
                f"Instance has no field '{name}' ({list(self._fields.keys())})")
        return self._fields[name]

    def __getitem__(self, name: str) -> Any:
        """Get an attribute by its name.

        Args:
            name (str): Name of the attribute.

        Raises:
            KeyError: If the instance has no attribute named ``name``.

        Returns:
            Any: The stored value with the key ``name``.
        """
        if name not in self._fields:
            raise KeyError(
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
        for f in self.fields:
            if f not in other.fields:
                return False
            if self._fields[f] != other._fields[f]:
                return False
        return True

    # Enable dict conversion with ``dict(instance)``
    def __iter__(self):
        for f in self.fields:
            yield (f, self._fields[f])

    def __str__(self):
        return str(dict(self))
