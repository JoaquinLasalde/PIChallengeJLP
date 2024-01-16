#Run http://server/docs to test the paths  

#Import the necessary modules and classes from FastAPI, Pydantic, and SQLAlchemy to run the code.
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy import create_engine, Column, Integer, String, select
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

#We create an instance of the FastAPI class, which represents the main app.
app = FastAPI()

#We set up the DB URL for SQLite and create the SQLAlchemy engine, so than the app could find our SQLite DB.
DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(DATABASE_URL)

#We create the 'characters' table in the DB, this is where other models will inherit from. 
Base = declarative_base()

#Now, we define our main data structure - the Character model, where we define what each character looks like in our DB.
class Character(Base):
    __tablename__ = "characters"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    height = Column(Integer)
    mass = Column(Integer)
    hair_color = Column(String)
    skin_color = Column(String)
    eye_color = Column(String)
    birth_year = Column(Integer)

#Here, we create the 'characters' table in the DB based on our model, this is where the character´s info will be hold.
Base.metadata.create_all(bind=engine)

#Setting up a system to talk to our database - creating a session maker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

#Now we define the blueprint for creating a new character, we tell the app how the character should look.
class CharacterCreate(BaseModel):
    name: str
    height: int
    mass: int
    hair_color: str
    skin_color: str
    eye_color: str
    birth_year: int

#Route for creating a new character via HTTP POST request. 
@app.post("/character/add")
def create_character(character: CharacterCreate):
    db = SessionLocal() #Create a DB session
    db_character = Character(**character.model_dump()) #Create a new character instance from the received data.
    db.add(db_character) #Add the new Character to the DB.
    db.commit()  #Commit the changes to the DB.
    db.refresh(db_character) #Refresh the character object to get the updated values.
    db.close() #Close the database session.
    return db_character #Return the created Character as a response.

#Route for reitrieving all characters via HTTP GET request. 
@app.get("/character/getAll")
def get_all_characters():
    db = SessionLocal()
    characters = db.query(Character).all() #Query characters from the DB
    db.close()
    return characters #Return the list of characters 

#Route for retrieving a specific character by ID via an HTTP GET request.
@app.get("/character/get/{character_id}")
def get_character(character_id: int):
    db = SessionLocal()
    character = db.query(Character).filter(Character.id == character_id).first() #Query a character bt its ID from the DB.
    db.close()
    #If the Character is not found, we raise an HTTPException with a 404 status code.
    if character is None:
        raise HTTPException(status_code=404, detail="Character not found")
    return character # Return the found Character as a response.

#Route for deleting a specific character by ID via HTTP DELETE request.
@app.delete("/character/delete/{character_id}")
def delete_character(character_id: int):
    db = SessionLocal()
    character = db.query(Character).filter(Character.id == character_id).first() #Query a character bt its ID from the DB.
    #If the character exists, we delete it from the DB.
    if character:
        db.delete(character)
        db.commit()
        db.close()
        return {"status": "Character deleted"} #Return a response indicating that the character has been deleted.
    db.close()
    #If the character is not found, we raise an HTTPException with a 404 status code.
    raise HTTPException(status_code=404, detail="Character not found")
