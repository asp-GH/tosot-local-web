import asyncio
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import Optional
from greeclimate.discovery import Discovery
from greeclimate.device import Device, Mode, FanSpeed

app = FastAPI()
_dev = None
_lock = asyncio.Lock()

async def get_dev():
    global _dev
    if _dev is None:
        infos = await Discovery().scan(wait_for=5)
        d = Device(infos[0])
        await d.bind()
        _dev = d
    return _dev

async def read_state():
    d = await get_dev()
    await d.update_state()
    await asyncio.sleep(1.5)
    return {"power": bool(d.power), "mode": int(d.mode), "target": d.target_temperature,
            "current": d.current_temperature, "fan": int(d.fan_speed)}

class Cmd(BaseModel):
    power: Optional[bool] = None
    mode: Optional[int] = None
    target: Optional[int] = None
    fan: Optional[int] = None

@app.get("/api/state")
async def state():
    async with _lock:
        return await read_state()

@app.post("/api/set")
async def set_state(c: Cmd):
    async with _lock:
        d = await get_dev()
        if c.power is not None: d.power = c.power
        if c.mode is not None: d.mode = Mode(c.mode)
        if c.target is not None: d.target_temperature = c.target
        if c.fan is not None: d.fan_speed = FanSpeed(c.fan)
        await d.push_state_update()
        return await read_state()

PAGE = """<!doctype html><meta name=viewport content="width=device-width,initial-scale=1">
<style>body{font-family:-apple-system,sans-serif;max-width:360px;margin:30px auto;text-align:center}
button{font-size:18px;padding:12px 16px;margin:4px;border-radius:10px;border:1px solid #888;background:#fff}
button.on{background:#222;color:#fff}#t{font-size:64px;margin:10px}</style>
<div>В комнате: <b id=cur>-</b>°</div>
<div id=t>-</div>
<div><button onclick="chg(-1)">−</button><button onclick="chg(1)">+</button></div>
<div><button id=pw onclick="tog()">Вкл/Выкл</button></div>
<div id=modes></div><div id=fans></div>
<script>
let S={};
const M={1:'Холод',4:'Тепло',2:'Осушение',3:'Вент.',0:'Авто'};
const F={0:'Авто',1:'1',3:'2',5:'3'};
function draw(){cur.textContent=S.current;t.textContent=S.target+'°';
pw.className=S.power?'on':'';
modes.innerHTML=Object.entries(M).map(([k,v])=>`<button class="${S.mode==k?'on':''}" onclick="set({mode:${k}})">${v}</button>`).join('');
fans.innerHTML=Object.entries(F).map(([k,v])=>`<button class="${S.fan==k?'on':''}" onclick="set({fan:${k}})">${v}</button>`).join('');}
async function load(){S=await (await fetch('/api/state')).json();draw()}
async function set(b){S=await (await fetch('/api/set',{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify(b)})).json();draw()}
function chg(d){set({target:S.target+d})}
function tog(){set({power:!S.power})}
load();setInterval(load,15000);
</script>"""

@app.get("/", response_class=HTMLResponse)
async def index():
    return PAGE
