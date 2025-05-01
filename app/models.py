from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Text


Base = declarative_base()


class Post(Base):
    __tablename__ = "post"

    post_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
