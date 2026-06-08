from pydantic import BaseModel


class ProcessedDataModel(BaseModel):
    id: int
    name: str
    followers: int
    followings: int
    likes: int
    comments: int
    impressions: int
    has_bio: bool = True
    has_pfp: bool = False
    likes_followers_ratio: float
    likes_comments_ratio: float
    likes_impressions_ratio: float
    