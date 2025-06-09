"""Aggregate PC API endpoints"""
from .pc import FeedAPI, SearchAPI, DetailAPI, CommentAPI


class XHS_Apis(FeedAPI, SearchAPI, DetailAPI, CommentAPI):
    def __init__(self) -> None:
        super().__init__()

