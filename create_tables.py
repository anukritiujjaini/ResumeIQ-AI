from db import engine, base
import models

base.metadata.create_all(bind=engine)

print("Tables Created Successfully!")
