from fastapi import APIRouter, Depends, HTTPException, File, Form, UploadFile
from sqlalchemy.orm import Session  # interact with database
from app.db.session import get_db
from typing import Optional
from fastapi.responses import JSONResponse
from app.services.spot_service import add_document, add_spot, get_spot_list_of_owner, update_spot_details, delete_spot
from app.schemas.spot import AddSpot, EditSpot
from app.db.spot_model import Document, Spot
from fastapi.responses import StreamingResponse
from io import BytesIO

router = APIRouter()

@router.get("/documents", response_class=JSONResponse)
async def get_all_documents(db: Session = Depends(get_db)):
    # Join documents with their spot info
    results = db.query(Spot).all()

    response = []
    for spot in results:
        spot_docs = db.query(Document).filter(Document.spot_id == spot.spot_id).all()

        doc_dict = {}
        for doc in spot_docs:
            doc_dict[doc.document_type] = {
                "filename": doc.filename,
                "url": f"spots/documents/view/{doc.id}"
            }

        response.append({
            "spot_id": spot.spot_id,
            "spot_title": spot.spot_title,
            "spot_address": spot.address,
            "documents": doc_dict
        })

    return response

@router.get("/documents/view/{doc_id}")
async def view_document(doc_id: int, db: Session = Depends(get_db)):
    print("view document")
    document = db.query(Document).filter(Document.id == doc_id).first()
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")

    return StreamingResponse(
        BytesIO(document.content),
        media_type="application/pdf",
        headers={"Content-Disposition": f"inline; filename={document.filename}"}
    )

@router.post("/add-documents")
async def add_documents_route(spot_id: int = Form(...),doc1: UploadFile = File(...),
    doc2: UploadFile = File(...),
    doc3: Optional[UploadFile] = File(None), db: Session = Depends(get_db)):
    try:
        response = await add_document(spot_id, doc1, doc2, doc3, db)
        return response
    except Exception as exception:
        print(exception)
        raise HTTPException(status_code=400, detail=exception.detail)
    

@router.post("/add-spot")
async def add_spot_route(spot_address: str = Form(...),
    owner_id: str = Form(...),
    spot_title: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    available_slots: int = Form(...),
    total_slots: int = Form(...),
    hourly_rate: int = Form(...),
    open_time: str = Form(...),
    close_time: str = Form(...),
    spot_description: Optional[str] = Form(None),
    available_days: list[str] = Form(...),
    image: Optional[list[str]] = Form(None),
    verification_status:int = Form(...),
    db: Session = Depends(get_db)):
    """
    Add a parking spot for the user.

    Args:
        spot_data (AddSpot): Spot data
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        dict: Response message otherwise raise appropriate HTTPException and return the error message

    Example:
        add_spot_route(spot_data)
        add a parking spot for the user
        return the spot details
    """
    try:
        print("Hi")
        spot_data = AddSpot(
        spot_address=spot_address,
        owner_id=owner_id,
        spot_title=spot_title,
        latitude=latitude,
        longitude=longitude,
        available_slots=available_slots,
        total_slots=total_slots,
        hourly_rate=hourly_rate,
        open_time=open_time,
        close_time=close_time,
        spot_description=spot_description,
        available_days=available_days,
        verification_status=verification_status,
        image=image
        )

        response = await add_spot(spot_data, db)
        print(response)
        if "error" in response:
            raise HTTPException(status_code=400, detail=response["detail"])
        return response
    except Exception as exception:
        print(exception)
        raise HTTPException(status_code=400, detail=exception.detail)


@router.get("/owner/{user_id}")
def get_spots_of_owner(user_id: int, db: Session = Depends(get_db)):
    """
    Retrieve all spots owned by a specific user.

    Args:
        user_id (int): User ID
        db (Session, optional): SQLAlchemy database session. Defaults to Depends(get_db).

    Returns:
        List[dict]: List of spots for the specified user
    """
    return get_spot_list_of_owner(user_id, db)


@router.put("/{spot_id}")
async def update_spot(spot_id: int, updated_spot: EditSpot, db: Session = Depends(get_db)):
    """
    Update the details of a parking spot.

    Args:
        spot_id (int): The unique identifier of the parking spot to be updated.
        updated_spot (EditSpot): An object containing the updated details of the parking spot.
        db (Session): The database session dependency.

    Returns:
        dict: The updated parking spot details after applying the changes.
    """
    return await update_spot_details(updated_spot, spot_id, db)


@router.delete("/{spot_id}")
async def delete_selected_spot(spot_id: int, db: Session = Depends(get_db)):
    """
    Deletes a parking spot with the specified ID.

    Args:
        spot_id (int): The ID of the parking spot to be deleted.
        db (Session, optional): The database session dependency. Defaults to the result of `Depends(get_db)`.

    Returns:
        None: The result of the `delete_spot` function, which handles the deletion logic.
    """
    return await delete_spot(spot_id, db)
