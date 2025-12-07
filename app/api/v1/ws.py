from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query

from app.core.security import decode_access_token
from app.core.ws_manager import manager
from app.db.base import SessionLocal
from app.db.models import User

router = APIRouter(tags=["ws"])


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str | None = Query(default=None)):
    """
    WebSocket endpoint.

    Client connects as:
      ws://127.0.0.1:8000/ws?token=<JWT>

    - Validates token
    - Resolves user
    - Registers connection in manager
    - Keeps connection open until disconnect
    """
    if not token:
        await websocket.close(code=1008)  # policy violation
        return

    user_id = decode_access_token(token)
    if not user_id:
        await websocket.close(code=1008)
        return

    # Check user exists in DB
    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == int(user_id)).first()
    finally:
        db.close()

    if not user:
        await websocket.close(code=1008)
        return

    # Register connection
    await manager.connect(user.id, websocket)

    try:
        # Simple receive loop: we don't expect client messages now,
        # but we must keep the connection alive.
        while True:
            # wait for any message or ping from client
            await websocket.receive_text()
    except WebSocketDisconnect:
        await manager.disconnect(user.id, websocket)
    except Exception:
        await manager.disconnect(user.id, websocket)
