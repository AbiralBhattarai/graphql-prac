from src.domain.models.input import RawDataModel
from src.domain.models.output import ProcessedDataModel



class DataPreprocess:
    def __init__(self,raw_data: RawDataModel):
        self.raw_data = raw_data

    async def process(self):
        id = self.raw_data.id
        name = self.raw_data.name
        followers = self.raw_data.followers
        followings = self.raw_data.followings
        likes = self.raw_data.likes
        comments = self.raw_data.comments
        impressions = self.raw_data.impressions
        has_bio = self.raw_data.has_bio
        has_pfp = self.raw_data.has_pfp
        likes_followers_ratio = round(likes/followers,4)
        likes_comments_ratio = round(likes/comments,4)
        likes_impressions_ratio = round(likes/impressions,4)

        result = ProcessedDataModel(id=id,name=name,followers=followers,followings=followings,likes=likes,comments=comments,
                                    has_bio=has_bio,has_pfp=has_pfp,impressions=impressions,likes_followers_ratio=likes_followers_ratio,likes_comments_ratio=likes_comments_ratio,likes_impressions_ratio=likes_impressions_ratio)
        return result.model_dump()