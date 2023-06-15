from typing import Dict, Type

from toolbox.DataModels import BaseModel

#: Dict storing the class responsible of each
#: data model. The key is a string of the data model type.
data_models_catalog: Dict[str, Type[BaseModel]] = {}


def register_data_model(data_model):
    """Decorator to register a data model class to the ``data_models_catalog``.
    """
    data_models_catalog[data_model.get_type()] = data_model
    return data_model
