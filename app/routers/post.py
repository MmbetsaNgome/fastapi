from typing import List, Optional
from fastapi import Depends, FastAPI, Response, status, HTTPException, APIRouter
from sqlalchemy.orm import Session
from .. import schemas,models,oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=["Posts"]
)

@router.get("/" ,response_model= List[schemas.Post])
def get_posts(db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user), limit:int = 10, skip:int = 0, search:Optional[str] = "" ):
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # cursor.execute(""" SELECT * FROM posts""")
    # posts = cursor.fetchall()
    # return{"data" : posts}
    print(current_user.id)
    return posts

@router.get("/{id}",response_model= schemas.Post)
def get_post(id:int, response:Response , db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):
   post = db.query(models.Post).filter(models.Post.id == id).first()
#    cursor.execute(""" SELECT * FROM posts WHERE id = %s """ ,(str(id)))
#    post = cursor.fetchone()
#    post = find_post(id)
   if not post:
       raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail= f"Post with id: {id} was not found")
    #    response.status_code = status.HTTP_404_NOT_FOUND
    #    return {"message" : f"Post with id: {id} was not found"}
   return post

@router.post("/" , status_code=status.HTTP_201_CREATED, response_model= schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):

    ## Using sqlalchemy orm 
# new_post = models.Post(title = post.title , content=post.content, published=post.published)
    new_post = models.Post(owner_id=current_user.id ,**post.model_dump())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    ##end of sqlalchemy orm

    ## Using regular sql
#    post.model_dump()
#    cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s,%s,%s)RETURNING * """, 
#                   (post.title, post.content, post.published))

#    new_post = cursor.fetchone()
#    conn.commit()
    ## end of regular sql

    return new_post



@router.put("/{id}" ,response_model= schemas.Post)
def update_post(id:int , post : schemas.PostCreate, db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    
    updated_post = post_query.first()
    
    # cursor.execute(""" UPDATE posts SET title = %s, content = %s, published = %s WHERE id = %s RETURNING * """, (post.title, post.content, post.published, str(id),))
    # post = cursor.fetchone()
    # conn.commit()
    # index = find_index_post(id)
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail= f"Post with id: {id} was not found")
    
    if updated_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorised to perform requested action")
    
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    db.refresh(updated_post)

    # post_dict = post.model_dump()
    # post_dict["id"] = id
    # my_post[index] = post_dict
    return updated_post

@router.delete("/{id}" , status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id:int, db: Session = Depends(get_db), current_user : int = Depends(oauth2.get_current_user)):

    post_query = db.query(models.Post).filter(models.Post.id == id)
        # cursor.execute(""" DELETE FROM posts where id = %s RETURNING * """, (str(id),))
    # post = cursor.fetchone()
    # conn.commit()
    # index = find_index_post(id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail= f"Post with id: {id} was not found")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Not authorised to perform requested action")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    # my_post.pop(index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)