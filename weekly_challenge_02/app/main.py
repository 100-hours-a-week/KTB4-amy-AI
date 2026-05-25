from fastapi import FastAPI
from app.database import Base, engine
from app.routers.post import router as post_router
from app.routers.comment import router as comment_router

app = FastAPI()

Base.metadata.create_all(bind=engine)

# 3. FastAPI 객체에 라우터 부품들을 조립(합체)합니다.
app.include_router(post_router)
app.include_router(comment_router)

@app.get("/")
def root():
    return {"finish"}