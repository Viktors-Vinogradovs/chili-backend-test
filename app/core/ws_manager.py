from typing import Dict, Set

from fastapi import WebSocket
from starlette.websockets import WebSocketDisconnect


class ConnectionManager:
    """
    Holds active WebSocket connections per user.
    key = user_id, value = set of WebSockets.
    """

    def __init__(self) -> None:
        self.active_connections: Dict[int, Set[WebSocket]] = {}

    async def connect(self, user_id: int, websocket: WebSocket) -> None:
        """Accept connection and register it for this user."""
        await websocket.accept()
        if user_id not in self.active_connections:
            self.active_connections[user_id] = set()
        self.active_connections[user_id].add(websocket)

    def _remove(self, user_id: int, websocket: WebSocket) -> None:
        sockets = self.active_connections.get(user_id)
        if not sockets:
            return
        sockets.discard(websocket)
        if not sockets:
            self.active_connections.pop(user_id, None)

    async def disconnect(self, user_id: int, websocket: WebSocket) -> None:
        """Remove socket on disconnect."""
        self._remove(user_id, websocket)

    async def broadcast_avatar_changed(self, user_id: int, avatar_url: str) -> None:
        """
        Send avatar change event to all sockets of given user.
        """
        sockets = list(self.active_connections.get(user_id, []))
        if not sockets:
            return

        message = {
            "event": "avatar_changed",
            "avatar_url": avatar_url,
        }

        for ws in sockets:
            try:
                await ws.send_json(message)
            except WebSocketDisconnect:
                self._remove(user_id, ws)
            except Exception:
                # any send error → drop connection
                self._remove(user_id, ws)

    async def disconnect_user(self, user_id: int) -> None:
        """
        Close & remove all sockets for this user (for delete endpoint later).
        """
        sockets = list(self.active_connections.get(user_id, []))
        for ws in sockets:
            try:
                await ws.close()
            except Exception:
                pass
        self.active_connections.pop(user_id, None)


# Global manager instance
manager = ConnectionManager()
