from typing import List, Literal, Optional, Union

from pydantic import BaseModel, Field
from typing_extensions import Annotated

class EventBase(BaseModel):
    type: Literal["Event"] = "Event"
    source: str


class BlockFoundEvent(EventBase):
    event_type: Literal["Block found"] = "Block found"


class Statistics(BaseModel):
    hashrate_s: float
    blocks_s: float
    time_error: float
    block_count: int


class StatisticsEvent(EventBase):
    event_type: Literal["Statistics"] = "Statistics"
    payload: Statistics


Event = Annotated[
    Union[BlockFoundEvent, StatisticsEvent], Field(discriminator="event_type")
]


class MiningControllerState:

    majority_statistics: Statistics
    minority_statistics: Statistics
    majority_block_count: int
    minority_block_count: int