'''ЗАДАЧА РЕПОЗИТОРИЙ

С использованием SQLAlchemy описать 2+ модели связанные между собой
Под модели описать схемы Pydantic
Реализовать Класс Репозитория для каждой модели (желательно чтобы репозитории наследовались от абстракции)
Суть репозитория:
save - принимает схему pydantic -> записывает в БД и возвращает заполненную схему pydantic
get - принимает ID и возвращает схему pydantic с данными объекта из БД
update - принимает схему, изменяет модель в БД и возвращает схему с новыми данными'''



from sqlalchemy import Column, Integer, String, ForeignKey, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from pydantic import BaseModel

Base = declarative_base()
engine = create_engine('sqlite:///example.db')
session = sessionmaker(bind=engine)



class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    age = Column(Integer)
    addresses = relationship('Address', back_populates='user')


class Address(Base):
    __tablename__ = 'addresses'

    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True)
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='addresses')


Base.metadata.create_all(engine)


class AddressSchema(BaseModel):
    id: int
    email: str
    user_id: int


class UserSchema(BaseModel):
    id: int
    name: str
    age: int
    addresses: list[AddressSchema]



class AbstractRepository:
    def save(self, schema):
        raise NotImplementedError

    def get(self, id):
        raise NotImplementedError

    def update(self, schema):
        raise NotImplementedError



class UserRepository(AbstractRepository):
    def save(self, schema: UserSchema):
        with session() as session:
            user = User(name=schema.name, age=schema.age)
            session.add(user)
            session.commit()
            return schema.copy(update={'id': user.id})

    def get(self, id: int):
        with session() as session:
            user = session.query(User).filter_by(id=id).first()
            return UserSchema.from_orm(user)

    def update(self, schema: UserSchema):
        with session() as session:
            user = session.query(User).filter_by(id=schema.id).first()
            if user:
                user.name = schema.name
                user.age = schema.age
                session.commit()
            return schema



class AddressRepository(AbstractRepository):
    def save(self, schema: AddressSchema):
        with session() as session:
            address = Address(email=schema.email, user_id=schema.user_id)
            session.add(address)
            session.commit()
            return schema.copy(update={'id': address.id})

    def get(self, id: int):
        with session() as session:
            address = session.query(Address).filter_by(id=id).first()
            return AddressSchema.from_orm(address)

    def update(self, schema: AddressSchema):
        with session() as session:
            address = session.query(Address).filter_by(id=schema.id).first()
            if address:
                address.email = schema.email
                session.commit()
            return schema
