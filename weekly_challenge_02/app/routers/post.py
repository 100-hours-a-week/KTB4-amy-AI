import ollama
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.post import Post
from app.schemas.schemas import Create_post, Update_post

router = APIRouter(prefix="/posts", tags=['Post'])

# 게시글 요약
@router.get('/{post_id}/summary')
def get_summary(post_id: int, db : Session = Depends(get_db)) -> str:
    post = db.query(Post).get(post_id)
    content = post.content

    response = ollama.chat(
        model = 'gemma4:e2b',
        messages=[
            {
                "role": "user",
                "content": f"다음 게시글 내용을 핵심만 요약해줘: {content}"
            }
        ]
    )

    return response['message']['content']

# 게시글 목록 조회
@router.get("")
def read_list(db : Session = Depends(get_db)):
    return db.query(Post).all()

# 게시글 추가 (create)
@router.post("/add")
def add(item_input : Create_post, db: Session = Depends(get_db)):
    tmp = item_input

    create_post = Post(username = tmp.username, title = tmp.title, content = tmp.content)
    db.add(create_post)
    db.commit()

    return 'create success'

# 특정 게시글 조회 + 조회수 증가
@router.get('/read/{post_id}')
def read_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).get(post_id)
    post.views += 1

    db.commit()
    return db.query(Post).get(post_id)

# 게시글 수정
@router.patch("/update/{post_id}")
def update_post(post_id: int, item_input : Update_post, db : Session = Depends(get_db)):
    tmp = item_input.model_dump()
    post = db.query(Post).get(post_id)
    post.title = tmp['title']
    post.content = tmp['content']

    db.commit()

    return "update success"

# 게시글 삭제
@router.delete("/delete/{post_id}")
def delete_post(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).get(post_id)
    db.delete(post)
    db.commit()

    return 'delete success'

# 좋아요
@router.patch("/like/{post_id}")
def like(post_id: int, db: Session = Depends(get_db)):
    post = db.query(Post).get(post_id)

    post.like += 1

    db.commit()

    return "success"
