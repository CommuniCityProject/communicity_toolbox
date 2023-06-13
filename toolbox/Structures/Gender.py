from enum import Enum, unique


@unique
class Gender(Enum):
    FEMALE = "FEMALE"
    MALE = "MALE"
    OTHER = "OTHER"

    def __str__(self):
        return self.name
