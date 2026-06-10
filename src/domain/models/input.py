from pydantic import BaseModel, field_validator

class RawDataModel(BaseModel):
    id: int
    name: str
    followers: int
    followings: int
    likes: int
    comments: int
    impressions: int
    has_bio: bool = True
    has_pfp : bool = False

    @field_validator('id','followers','followings','likes','comments','impressions')
    @classmethod
    def is_gt_0(cls,value):
        if value < 0:
            raise ValueError('value must be greater than 0')
        else:
            return value


