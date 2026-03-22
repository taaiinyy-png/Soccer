python
import discord
from discord.ext import commands, tasks
import requests
import os
from dotenv import load_dotenv

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

API_KEY = os.getenv('FOOTBALL_API_KEY')
BASE_URL = "https://v3.football.api-sports.io/"

HEADERS = {
    'x-apisports-key': API_KEY
}

@bot.event
async def on_ready():
    print(f'¡Bot conectado como {bot.user} nya~!')
    check_live_matches.start()  # Inicia la tarea de chequeo periódico (opcional)

@bot.command(name='live')
async def live_score(ctx, *, team_name: str):
    """Muestra el marcador en vivo de un equipo (ej: !live Barcelona)"""
    params = {
        'live': 'all',
        'search': team_name  # Busca por nombre del equipo
    }
    
    try: response = requests.get(BASE_URL + "fixtures", headers=HEADERS, params=params)
        data = response.json()
        
        if data['results'] == 0:
            await ctx.send(f"No hay partido en vivo para **{team_name}** ahora mismo nya~")
            return
        
        match = data['response'][0]  # Toma el primero que coincida
        home = match['teams']['home']['name']
        away = match['teams']['away']['name']
        score_home = match['goals']['home'] or 0
        score_away = match['goals']['away'] or 0
        minute = match['fixture']['status']['elapsed'] or '?'
        league = match['league']['name']
        
        msg = f"**{league}** (Minuto {minute})\n"
        msg += f"{home} {score_home} - {score_away} {away}\n"
        
        # Agrega eventos recientes si hay
        events = match.get('events', [])
        if events:
            msg += "\nEventos recientes:\n"
            for e in events[-3:]:  # Últimos 3
                time = e['time']['elapsed']
                player = e['player']['name'] or '?'
                type_e = e['type']
                detail = e['detail']
                msg += f"{time}' - {type_e}: {player} ({detail})\n"
        
        await ctx.send(msg)
    
    except Exception as e:
        await ctx.send(f"¡Ups! Algo salió mal al consultar la API nya~ ({str(e)})")

@tasks.loop(minutes=5)  # Chequea cada 5 min (opcional, para notificar automáticamente)
async def check_live_matches():
    # Aquí podrías buscar partidos específicos (ej: Barcelona o LaLiga) y enviar a un canal fijo
    # Por ahora lo dejamos simple, pero puedes expandirlo
    pass

bot.run(os.getenv('DISCORD_TOKEN'))
