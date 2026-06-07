from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user_model import User
from app.schemas.item_schema import ItemCreate, ItemUpdate, ItemResponse
from app.services.items_service import ItemsService
from app.auth.dependencies import get_current_user

router = APIRouter(prefix="/items", tags=["Study Items"])

# =====================================================================
# 1. READ ALL ITEMS FOR CURRENT USER (GET)
# =====================================================================
@router.get("", response_model=List[ItemResponse], summary="Retrieve all study items for logged-in user")
async def read_items(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Fetch all study items belonging to the authenticated user.
    """
    items = await ItemsService.get_all(db, current_user.id)
    return items

# =====================================================================
# 2. READ SINGLE ITEM BY ID (GET)
# =====================================================================
@router.get("/{item_id}", response_model=ItemResponse, summary="Retrieve a study item by its ID")
async def read_item(
    item_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Fetch a single study item by its ID, if it belongs to the authenticated user.
    """
    item = await ItemsService.get_by_id(db, item_id, current_user.id)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study item with ID {item_id} not found"
        )
    return item

# =====================================================================
# 3. CREATE A NEW ITEM (POST)
# =====================================================================
@router.post("", response_model=ItemResponse, status_code=status.HTTP_201_CREATED, summary="Create a new study item")
async def create_item(
    item_data: ItemCreate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Create a new study item linked to the authenticated user.
    """
    new_item = await ItemsService.create(db, item_data, current_user.id)
    return new_item

# =====================================================================
# 4. UPDATE AN ITEM (PUT)
# =====================================================================
@router.put("/{item_id}", response_model=ItemResponse, summary="Update a study item")
async def update_item(
    item_id: int, 
    item_data: ItemUpdate, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Update details of a study item by ID.
    Only allows updates if the item belongs to the authenticated user.
    """
    updated_item = await ItemsService.update(db, item_id, item_data, current_user.id)
    if not updated_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study item with ID {item_id} not found"
        )
    return updated_item

# =====================================================================
# 5. DELETE AN ITEM (DELETE)
# =====================================================================
@router.delete("/{item_id}", status_code=status.HTTP_200_OK, summary="Delete a study item")
async def delete_item(
    item_id: int, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """
    Remove a study item from the database.
    Only succeeds if the item belongs to the authenticated user.
    """
    deleted = await ItemsService.delete(db, item_id, current_user.id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Study item with ID {item_id} not found"
        )
    return {"detail": "Item deleted successfully"}
