from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.comment import Comment
from app.schemas.schemas import Create_comment,  Update_comment

router = APIRouter(prefix = "/posts/{post_id}/comments", tags=['Comment'])

# 댓글 조회
@router.get('')
def read_comment(post_id: int, db: Session = Depends(get_db)):
    return db.query(Comment).filter(Comment.post_id == post_id).all()

# 댓글 생성
@router.post('/post')
def create_comment(create_item : Create_comment, post_id : int, db: Session = Depends(get_db)):
    tmp = create_item

    create_comment = Comment(username = tmp.username, content = tmp.content, post_id = post_id)
    db.add(create_comment)
    db.commit()

    return 'create success'

# 댓글 수정
@router.patch('/{comment_id}/update')
def update_comment(post_id : int, comment_id : int, update_item: Update_comment, db : Session = Depends(get_db)):
    tmp = update_item
    comment = db.query(Comment).get(comment_id)
    comment.content = tmp.content

    db.commit()

    return 'update success'

# 댓글 삭제
@router.delete('/{comment_id}/delete')
def del_comment(comment_id: int, db : Session = Depends(get_db)):
    cmt = db.query(Comment).get(comment_id)
    db.delete(cmt)
    db.commit()

    return 'delete success'