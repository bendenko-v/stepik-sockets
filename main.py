from pathlib import Path

import socketio
from fastapi import FastAPI
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.staticfiles import StaticFiles

from models import Riddle, Player
from utils import load_riddles

fast_app = FastAPI()
fast_app.mount("/assets", StaticFiles(directory="assets"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / 'templates')

sio = socketio.AsyncServer(async_mode='asgi', cors_allowed_origins='*')
app = socketio.ASGIApp(sio, fast_app)

riddles = [Riddle(**r) for r in load_riddles()]
players = {}


@sio.event
async def connect(sid, environ):
    players[sid] = Player(sid=sid)


@sio.event
async def disconnect(sid):
    del players[sid]


@sio.on('next')
async def next(sid, data):
    player = players[sid]
    if player.last_asked == len(riddles):
        await sio.emit('over', data={}, to=sid)
        return
    riddle = riddles[player.last_asked]
    await sio.emit('riddle', data={'text': riddle.text}, to=sid)


@sio.on('answer')
async def answer(sid, data):
    player = players[sid]
    riddle = riddles[player.last_asked]
    answer = data.get('text', '')
    if riddle.answer.lower() == answer.lower():
        await sio.emit(
            'result',
            data={'riddle': riddle.text, 'is_correct': True, 'answer': riddle.answer},
            to=sid
        )
        player.score += 1
        await sio.emit('score', data={'value': player.score}, to=sid)
    else:
        await sio.emit('result', data={'is_correct': False}, to=sid)
    player.last_asked += 1
    if player.last_asked == len(riddles):
        await sio.emit('over', data={}, to=sid)
        return


@fast_app.get('/')
async def index(request: Request):
    return templates.TemplateResponse(
        'index.html',
        {'request': request, 'riddle': riddles[0].model_dump()}  # тут просто передал загадку под 0 индексом
        # не до конца понятно что надо именно так передавать что-то чтобы шаблон первую загадку показывал?
    )


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app, host='127.0.0.1', port=8000)
