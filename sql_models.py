import sqlalchemy as sq
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

Base = declarative_base()
engine = sq.create_engine('postgresql+psycopg2://postgres:postgres@localhost/VKTINDER')
Session = sessionmaker(bind=engine)
session = Session()



class User(Base):
    __tablename__ = 'Client'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    second_name = sq.Column(sq.String, nullable=False)
    range_age_from = sq.Column(sq.Integer, nullable=False)
    range_age_to = sq.Column(sq.Integer, nullable=False)
    city = sq.Column(sq.String, nullable=False)
    age = sq.Column(sq.String)

    def __init__(self, vk_id, first_name, second_name, range_age_from, range_age_to, city, age):
        self.vk_id = vk_id
        self.first_name = first_name
        self.second_name = second_name
        self.range_age_from = range_age_from
        self.range_age_to = range_age_to
        self.city = city
        self.age = age

    def __repr__(self):
        return "<User('%s','%s', '%s', '%s', '%s', '%s', '%s')>" % \
               (self.vk_id, self.first_name, self.second_name, self.range_age_from, self.range_age_to,
                self.city, self.age)


class Partner(Base):
    __tablename__ = 'DatingUser'

    id = sq.Column(sq.Integer, primary_key=True)
    vk_id = sq.Column(sq.Integer, nullable=False, unique=True)
    first_name = sq.Column(sq.String, nullable=False)
    second_name = sq.Column(sq.String, nullable=False)
    age = sq.Column(sq.String)
    id_User = sq.Column(sq.Integer, sq.ForeignKey('Client.id'))

    def __init__(self, vk_id, first_name, second_name, age, id_User):
        self.vk_id = vk_id
        self.first_name = first_name
        self.second_name = second_name
        self.age = age
        self.id_User = id_User

    def __repr__(self):
        return "<User('%s','%s', '%s', '%s', '%s')>" % \
               (self.vk_id, self.first_name, self.second_name, self.age, self.id_User)


class PhotoData(Base):
    __tablename__ = 'Photos'

    id = sq.Column(sq.Integer, primary_key=True)
    id_DatingUser = sq.Column(sq.Integer, sq.ForeignKey('DatingUser.id'), nullable=False)
    link_photo = sq.Column(sq.String, nullable=False)
    count_likes = sq.Column(sq.Integer, nullable=False)

    def __init__(self, id_DatingUser, link_photo, count_likes):
        self.id_DatingUser = id_DatingUser
        self.link_photo = link_photo
        self.count_likes = count_likes

    def __repr__(self):
        return "<User('%s','%s', '%s')>" % \
               (self.id_DatingUser, self.link_photo, self.count_likes)


def create_tables():
    Base.metadata.create_all(engine)
    print('DataBase create')

