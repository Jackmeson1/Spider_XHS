"""Aggregate PC API endpoints"""
from .pc import FeedAPI, SearchAPI, DetailAPI, CommentAPI


class XHS_Apis(FeedAPI, SearchAPI, DetailAPI, CommentAPI):
    def __init__(self, rate_limit: float = 0.0) -> None:
        super().__init__(rate_limit)

