from database import engine
from models import metadata

metadata.create_all(engine)

print("Tables created successfully.")