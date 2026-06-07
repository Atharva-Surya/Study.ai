from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.item_model import Item
from app.schemas.item_schema import ItemCreate, ItemUpdate

# =====================================================================
# CONCEPT: DATABASE-BACKED SERVICE LAYER
# =====================================================================
# Now, we query the SQL database tables using SQLAlchemy ORM.
# All actions are scoped to a specific 'user_id' so users cannot access 
# each other's study items.
class ItemsService:
    @staticmethod
    async def get_all(db: Session, user_id: int) -> List[Item]:
        """
        Retrieve all study items belonging to the current user.
        """
        return db.query(Item).filter(Item.owner_id == user_id).all()

    @staticmethod
    async def get_by_id(db: Session, item_id: int, user_id: int) -> Optional[Item]:
        """
        Retrieve a specific study item by ID, checking that it belongs to the user.
        """
        return db.query(Item).filter(Item.id == item_id, Item.owner_id == user_id).first()

    @staticmethod
    async def create(db: Session, item_data: ItemCreate, user_id: int) -> Item:
        """
        Create a new study item linked to the current user.
        """
        new_item = Item(
            title=item_data.title,
            description=item_data.description,
            completed=False,
            owner_id=user_id  # Link the item to the logged-in user
        )
        db.add(new_item)
        db.commit()
        db.refresh(new_item)
        return new_item

    @staticmethod
    async def update(db: Session, item_id: int, item_data: ItemUpdate, user_id: int) -> Optional[Item]:
        """
        Update a study item, ensuring it belongs to the current user.
        """
        # Find the item first
        item = db.query(Item).filter(Item.id == item_id, Item.owner_id == user_id).first()
        if not item:
            return None
            
        # Convert update schema to dictionary, excluding unset values
        update_dict = item_data.model_dump(exclude_unset=True)
        
        # Apply updates dynamically
        for key, value in update_dict.items():
            setattr(item, key, value)
            
        db.commit()
        db.refresh(item)
        return item

    @staticmethod
    async def delete(db: Session, item_id: int, user_id: int) -> bool:
        """
        Delete a study item, ensuring it belongs to the current user.
        """
        item = db.query(Item).filter(Item.id == item_id, Item.owner_id == user_id).first()
        if not item:
            return False
            
        db.delete(item)
        db.commit()
        return True
