from datetime import datetime

from sqlalchemy.sql.schema import Column
from sqlalchemy.sql.sqltypes import Integer, String, DateTime

from app.database import Base


class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, nullable=False)
    title = Column(String, nullable=False)
    content = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.now)
    like = Column(Integer, default= 0)
    views = Column(Integer, default = 0)