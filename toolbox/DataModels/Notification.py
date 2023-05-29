from datetime import datetime
from typing import List, Literal

from pydantic import BaseModel, Field


class Notification(BaseModel):
    """Data model for the context broker subscription notifications.

    Attributes:
        id (str): Notification identifier.
        type (Literal["Notification"]): Notification.
        notifiedAt (datetime): DateTime corresponding to the instant when the
            notification was generated.
        data (List[dict]): List of entities that provoked the notification.
    """

    id: str = Field(description="Notification identifier")
    type: str = Field(description="``Notification``")
    subscriptionId: str = Field(description="Subscription identifier")
    notifiedAt: datetime = Field(description="""DateTime corresponding to the
        instant when the notification was generated""")
    data: List[dict] = Field(description="""List of entities that provoked
        the notification""")
