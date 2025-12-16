from sqlalchemy import create_engine
from core_registry.models import Base

# This creates the database file in the same folder
DATABASE_URL = "sqlite:///veridian_cortex.db"

def init_db():
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)
    print(f"STATUS: Database initialized successfully at {DATABASE_URL}")
    print("STATUS: Schema 'SuspectEntity' created.")

if __name__ == "__main__":
    init_db()
