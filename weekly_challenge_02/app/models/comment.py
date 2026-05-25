from datetime import datetime

from sqlalchemy.sql.schema import Column, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String, DateTime

from app.database import Base


class Comment(Base):
    __tablename__ = "comments"

    post_id = Column(Integer, ForeignKey("posts.id")) # 외래키
    id = Column(Integer, primary_key=True, index=True)
    content = Column(String, nullable=False)
    username = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.now)