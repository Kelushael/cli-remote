#!/usr/bin/env python3
import asyncio,json,uuid
from datetime import datetime
from aiohttp import web
import aiohttp
sessions={}
admin_connections=set()
async def handle_client(request):
    ws=web.WebSocketResponse();await ws.prepare(request)
    sid=str(uuid.uuid4())[:8]
    sessions[sid]={"ws":ws,"approved":False,"history":[]}
    for a in admin_connections:
        try:await a.send_json({"type":"client_connected","session_id":sid})
        except:pass
    await ws.send_json({"type":"session_created","session_id":sid})
    try:
        async for msg in ws:
            if msg.type==aiohttp.WSMsgType.TEXT:
                data=json.loads(msg.data)
                if data.get("type")=="approve":
                    sessions[sid]["approved"]=True
                    for a in admin_connections:
                        try:await a.send_json({"type":"session_approved","session_id":sid})
                        except:pass
                elif data.get("type")=="output":
                    for a in admin_connections:
                        try:await a.send_json({"type":"command_output","session_id":sid,"output":data.get("output","")})
                        except:pass
    finally:
        del sessions[sid]
        for a in admin_connections:
            try:await a.send_json({"type":"client_disconnected","session_id":sid})
            except:pass
    return ws
async def handle_admin(request):
    ws=web.WebSocketResponse();await ws.prepare(request)
    admin_connections.add(ws)
    await ws.send_json({"type":"session_list","sessions":[{"session_id":s,"approved":sessions[s]["approved"]}for s in sessions]})
    try:
        async for msg in ws:
            if msg.type==aiohttp.WSMsgType.TEXT:
                data=json.loads(msg.data)
                if data.get("type")=="command":
                    sid=data.get("session_id");cmd=data.get("command")
                    if sid in sessions and sessions[sid]["approved"]:
                        await sessions[sid]["ws"].send_json({"type":"command","command":cmd})
    finally:admin_connections.discard(ws)
    return ws
async def handle_index(r):return web.FileResponse("./static/client.html")
async def handle_admin_page(r):return web.FileResponse("./static/admin.html")
async def handle_carwash(r):return web.FileResponse("./static/carwash.html")
app=web.Application()
app.router.add_get("/",handle_index)
app.router.add_get("/admin",handle_admin_page)
app.router.add_get("/carwash",handle_carwash)
app.router.add_get("/ws/client",handle_client)
app.router.add_get("/ws/admin",handle_admin)
app.router.add_static("/carwash/dl/","./static/carwash")
app.router.add_static("/static/","./static")
if __name__=="__main__":web.run_app(app,port=8765)
