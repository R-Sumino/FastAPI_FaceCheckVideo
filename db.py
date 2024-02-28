from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import and_, or_, not_

Base = declarative_base()
RDB_PATH = 'sqlite:///db.sqlite3'
ECHO_LOG = False

engine = create_engine(
    RDB_PATH, echo=ECHO_LOG
)

Session = sessionmaker(bind=engine,
                       expire_on_commit=False)
session = Session()
