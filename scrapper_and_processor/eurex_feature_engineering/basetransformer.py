"""
This contains the base class every transformer should inherit from.
This class is an abstract class and should not be used directly.
This is to ensure an modular approch to feature engineering and data processing
"""
from abc import ABC, abstractmethod
from typing import Any

class BaseTransformer(ABC):

    registry: list[type] = []
    is_transformation = False

    def __init_subclass__(cls,**kwargs) -> None:
        super().__init_subclass__(**kwargs)

        print(f"Registering transformer: {cls.__name__}")
        
        if getattr(cls, "is_transformation", True):
            BaseTransformer.registry.append(cls)

    @abstractmethod
    def process(self, df):
        """
        This method should process the input dataframe and return the output dataframe
        """
        ...
    
    def __call__(self, df) -> Any:
        return self.process(df)