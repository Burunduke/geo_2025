# 3️⃣ События в радиусе
@router.get("/nearby")
def get_nearby_events(
    lat: float = Query(...),
    lon: float = Query(...),
    radius: float = Query(1000, description="Радиус в метрах"),
    event_type: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Найти события в радиусе"""
    user_point = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
    
    query = db.query(
        Event.id,
        Event.title,
        Event.event_type,
        Event.description,
        func.ST_X(Event.geom).label('lon'),
        func.ST_Y(Event.geom).label('lat'),
        Event.start_time,
        Event.end_time,
        func.ST_Distance(
            func.ST_Transform(Event.geom, 3857),
            func.ST_Transform(user_point, 3857)
        ).label('distance')
    ).filter(
        func.ST_DWithin(
            func.ST_Transform(Event.geom, 3857),
            func.ST_Transform(user_point, 3857),
            radius
        )
    )
    
    if event_type:
        query = query.filter(Event.event_type == event_type)
    
    results = query.order_by(text('distance')).all()
    
    return {
        "count": len(results),
        "events": [
            {
                "id": evt.id,
                "title": evt.title,
                "event_type": evt.event_type,
                "description": evt.description,
                "lat": evt.lat,
                "lon": evt.lon,
                "start_time": evt.start_time,
                "end_time": evt.end_time,
                "distance": round(evt.distance, 2)
            }
            for evt in results
        ]
    }

# 4️⃣ Типы событий
@router.get("/types")
def get_event_types(db: Session = Depends(get_db)):
    """Получить список типов событий"""
    types = db.query(
        Event.event_type,
        func.count(Event.id).label('count')
    ).group_by(Event.event_type).all()
    
    return [
        {"type": t[0], "count": t[1]}
        for t in types
    ]