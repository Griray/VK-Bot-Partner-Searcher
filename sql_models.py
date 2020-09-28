import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from Partner_Searcher_Vk_Bot import identity, get_vk_name

engine = sq.create_engine('postgresql+psycopg2://postgres:postgres@localhost:5439//VKTINDER')
Session = sessionmaker(bind=engine)
Session.configure(bind=engine)
connection = engine.connect()
Base = declarative_base()

class User(Base):
    __tablename__ = 'Client'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    second_name = sq.Column(sq.String, nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    range_age = sq.Column(sq.String, nullable=False)
    city = sq.Column(sq.String, nullable=False)


class Partner(Base):
    __tablename__ = 'DatingUser'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    second_name = sq.Column(sq.String, nullable=False)
    age = sq.Column(sq.Integer, nullable=False)
    id_User = sq.Column(sq.Integer, sq.ForeignKey('Client.id'))

class PhotoData(Base):
    __tablename__ = 'Photos'

    id = sq.Column(sq.Integer, primary_key=True)
    id_DatingUser = sq.Column(sq.Integer, sq.ForeignKey('DatingUser.id'), nullable=False)
    link_photo = sq.Column(sq.String, nullable=False)
    count_likes = sq.Column(sq.Integer, nullable=False)
