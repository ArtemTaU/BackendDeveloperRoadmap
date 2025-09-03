from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()
engine = create_engine("sqlite:///test.db", connect_args={"check_same_thread": False})

Base.metadata.create_all(engine)
