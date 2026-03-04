from typing import Optional
from sqlmodel import Field, SQLModel, create_engine, Session

class SurgeonProfile(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    email: str = Field(index=True)
    full_name: str
    surgeon_level: str
    procedure_count: int
    risk_index: int
    overrun_freq: float = 0.0
    skills: str = "" # Comma-separated tags

# SQLite database file
sqlite_file_name = "surgeons.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session
