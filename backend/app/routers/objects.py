from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, text
from geoalchemy2.functions import ST_Distance, ST_DWithin, ST_AsGeoJSON, ST_MakePoint
from typing import List, Optional
from ..database import get_db
from ..models import Object, District
from ..schemas import ObjectResponse, ObjectCreate, NearbyObjectsRequest

router = APIRouter()

# Получить все объекты
@router.get("/", response_model=List[ObjectResponse])
def get_objects(
    object_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Получить все объекты с опциональной фильтрацией по типу"""
    query = db.query(
        Object.id,
        Object.name,
        Object.type,
        Object.address,
        Object.created_at,
        func.ST_X(Object.geom).label('lon'),
        func.ST_Y(Object.geom).label('lat')
    )
    
    if object_type:
        query = query.filter(Object.type == object_type)
    
    objects = query.all()
    
    return [
        ObjectResponse(
            id=obj.id,
            name=obj.name,
            type=obj.type,
            address=obj.address,
            lat=obj.lat,
            lon=obj.lon,
            created_at=obj.created_at
        )
        for obj in objects
    ]

# Найти объекты в радиусе
@router.post("/nearby")
def get_nearby_objects(
    request: NearbyObjectsRequest,
    db: Session = Depends(get_db)
):
    """Найти все объекты в заданном радиусе от точки"""
    user_point = func.ST_SetSRID(func.ST_MakePoint(request.lon, request.lat), 4326)
    
    query = db.query(
        Object.id,
        Object.name,
        Object.type,
        Object.address,
        func.ST_X(Object.geom).label('lon'),
        func.ST_Y(Object.geom).label('lat'),
        func.ST_Distance(
            func.ST_Transform(Object.geom, 3857),
            func.ST_Transform(user_point, 3857)
        ).label('distance')
    ).filter(
        func.ST_DWithin(
            func.ST_Transform(Object.geom, 3857),
            func.ST_Transform(user_point, 3857),
            request.radius
        )
    )
    
    if request.object_type:
        query = query.filter(Object.type == request.object_type)
    
    query = query.order_by(text('distance'))
    
    results = query.all()
    
    return {
        "count": len(results),
        "objects": [
            {
                "id": obj.id,
                "name": obj.name,
                "type": obj.type,
                "address": obj.address,
                "lat": obj.lat,
                "lon": obj.lon,
                "distance": round(obj.distance, 2)
            }
            for obj in results
        ]
    }

# Найти ближайший объект
@router.get("/nearest")
def get_nearest_object(
    lat: float = Query(..., description="Широта"),
    lon: float = Query(..., description="Долгота"),
    object_type: Optional[str] = Query(None, description="Тип объекта"),
    db: Session = Depends(get_db)
):
    """Найти ближайший объект заданного типа"""
    user_point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
    
    query = db.query(
        Object.id,
        Object.name,
        Object.type,
        Object.address,
        func.ST_X(Object.geom).label('lon'),
        func.ST_Y(Object.geom).label('lat'),
        func.ST_Distance(
            func.ST_Transform(Object.geom, 3857),
            func.ST_Transform(user_point, 3857)
        ).label('distance')
    )
    
    if object_type:
        query = query.filter(Object.type == object_type)
    
    result = query.order_by(text('distance')).first()
    
    if not result:
        raise HTTPException(status_code=404, detail="Объекты не найдены")
    
    return {
        "id": result.id,
        "name": result.name,
        "type": result.type,
        "address": result.address,
        "lat": result.lat,
        "lon": result.lon,
        "distance": round(result.distance, 2)
    }

# Создать новый объект
@router.post("/", response_model=ObjectResponse)
def create_object(
    obj: ObjectCreate,
    db: Session = Depends(get_db)
):
    """Создать новый объект инфраструктуры"""
    new_object = Object(
        name=obj.name,
        type=obj.type,
        address=obj.address,
        geom=func.ST_SetSRID(func.ST_MakePoint(obj.lon, obj.lat), 4326)
    )
    
    db.add(new_object)
    db.commit()
    db.refresh(new_object)
    
    return ObjectResponse(
        id=new_object.id,
        name=new_object.name,
        type=new_object.type,
        address=new_object.address,
        lat=obj.lat,
        lon=obj.lon,
        created_at=new_object.created_at
    )

# Получить типы объектов
@router.get("/types")
def get_object_types(db: Session = Depends(get_db)):
    """Получить список всех типов объектов"""
    types = db.query(Object.type, func.count(Object.id)).group_by(Object.type).all()
    
    return [
        {"type": t[0], "count": t[1]}
        for t in types
    ]