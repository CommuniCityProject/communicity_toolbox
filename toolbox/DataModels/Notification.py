from datetime import datetime
from typing import List

from pydantic import BaseModel, Field


class Notification(BaseModel):
    """Data model for the context broker subscription notifications.
    """

    id: str = Field(description="Notification identifier")
    type: str = Field(description="``Notification``")
    subscriptionId: str = Field(description="Subscription identifier")
    notifiedAt: datetime = Field(description="DateTime corresponding to the "
                                 "instant when the notification was generated")
    data: List[dict] = Field(description="List of entities that provoked "
                             "the notification")
