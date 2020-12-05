from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import models


class GBDataBase:
    def __init__(self, db_url: str):
        engine = create_engine(db_url)
        models.Base.metadata.create_all(bind=engine)
        self.session_m = sessionmaker(bind=engine)

    @staticmethod
    def __get_or_create(session, model, **data):
        db_model = session.query(model).filter(model.url == data['url']).first()
        if not db_model:
            db_model = model(**data)

        return db_model

    def create_post(self, data):
        session = self.session_m()

        writer = self.__get_or_create(session, models.Writer, **data['writer'])
        post = self.__get_or_create(session, models.Post, **data['post_data'], writer=writer)
        for comment in data['comments']:
            comment_db = models.Comment()
            comment_db.author = comment['author']
            comment_db.text = comment['text']
            # comment = self._get_or_create(session, models.Comment, comment)
            comment_db.post = post
            session.add(comment_db)

        tags = map(lambda tag_data: self.__get_or_create(session, models.Tag, **tag_data), data['tags'])
        post.tags.extend(tags)
        session.add(post)

        try:
            session.commit()
        except SQLAlchemyError as e:
            session.rollback()
        finally:
            session.close()

        print(1)
