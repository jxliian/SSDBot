import discord
from discord.ext import commands
import requests
import security # Asegúrate de que este archivo contenga el token security.json
import os
import json


################################################
# Author: Jxlig0d
# Date: 2025-07-16
# Description: Bot de Discord con comandos de administración y seguridad en español.
# License: MIT
# Version: 1.4.3 (BETA)
################################################


intents = discord.Intents.default() # Le decimos a discord que queremos recibir eventos de mensajes
intents.members = True  # Permitir que el bot gestione roles
intents.message_content = True # Habilitar acceso a los mensajes

# Establecemos el bot con el prefijo "%" con lo que llamaremos a nuestro bot y los intents definidos
bot = commands.Bot(command_prefix="%", intents=intents)


# Comandos de administración del bot de las palabras prohibidas - Son muchas funciones, así que las agrupamos aquí
# =============================================================================================================

# Cargar palabras restringidas desde un archivo JSON
restricted_words_file = "restricted_words.json"


# Cargar las palabras restringidas desde un archivo JSON
def load_restricted_words():
    if os.path.exists(restricted_words_file):
        with open(restricted_words_file, 'r') as file:
            return json.load(file)
    else:
        return []  # Devuelve una lista vacía si el archivo no existe

# Guardar las palabras restringidas en un archivo JSON
def save_restricted_words():
    with open(restricted_words_file, 'w') as file:
        json.dump(restricted_words, file)

# Inicializamos la lista de palabras restringidas
restricted_words = load_restricted_words()

# Función para agregar palabras al filtro
def add_words_to_filter(words):
    new_words = [word.strip().lower() for word in words]  # Convertir todas las palabras a minúsculas y limpiar espacios
    added_words = []  # Lista para las palabras que realmente se agregaron

    for word in new_words:
        if word not in restricted_words:  # Evitar agregar palabras duplicadas
            restricted_words.append(word)
            added_words.append(word)

    save_restricted_words()  # Guardar cambios en el archivo JSON

    if added_words:
        return f"Las palabras {', '.join(added_words)} han sido añadidas al filtro."
    else:
        return "No se han añadido nuevas palabras, ya estaban en el filtro."

# Función para eliminar palabras del filtro
def remove_words_from_filter(words):
    removed_words = []  # Lista para las palabras que realmente se eliminaron
    for word in words:
        if word in restricted_words:  # Solo eliminar si la palabra está en la lista
            restricted_words.remove(word)
            removed_words.append(word)
    
    save_restricted_words()  # Guardar cambios en el archivo JSON

    if removed_words:
        return f"Las palabras {', '.join(removed_words)} han sido eliminadas del filtro."
    else:
        return "No se han encontrado palabras para eliminar."

# Función para verificar si un mensaje contiene palabras restringidas
def check_message_for_restricted_words(message):
    message_content = message.content.lower()  # Convertir el mensaje a minúsculas
    for word in restricted_words:
        if word in message_content:
            return True  # Si el mensaje contiene alguna palabra restringida
    return False  # Si no contiene ninguna palabra restringida

# Comando para agregar una palabra o una lista de palabras al filtro
@bot.command()
@commands.has_permissions(administrator=True)  # Solo administradores pueden agregar palabras
async def addfilter(ctx, *words: str):
    """Comando para agregar palabras al filtro de palabras restringidas.
    Acepta una o más palabras separadas por coma."""
    if not words:
        await ctx.send("Debes proporcionar al menos una palabra.")
        return

    # Convierte los argumentos en una lista de palabras separadas por coma
    all_words = ', '.join(words).split(',')
    word_filter_enabled = True  # Activamos el filtro de palabras si no estaba activado

    # Llamamos a la función para agregar las palabras a la lista de palabras restringidas
    response = add_words_to_filter(all_words)  
    await ctx.send(response)

# Comando para eliminar una palabra o una lista de palabras del filtro
@bot.command()
@commands.has_permissions(administrator=True)  # Solo administradores pueden eliminar palabras
async def removefilter(ctx, *words: str):
    """Comando para eliminar palabras del filtro de palabras restringidas.
    Acepta una o más palabras separadas por coma."""
    if not words:
        await ctx.send("Debes proporcionar al menos una palabra para eliminar.")
        return

    # Convierte los argumentos en una lista de palabras separadas por coma
    all_words = ', '.join(words).split(',')
    word_filter_enabled = False  # Desactivamos el filtro de palabras si no estaba activado

    # Llamamos a la función para eliminar las palabras de la lista de palabras restringidas
    response = remove_words_from_filter(all_words)  
    await ctx.send(response)

# Evento para eliminar mensajes con palabras restringidas
@bot.event
async def on_message(message):
    # Evitar que el bot se procese a sí mismo
    if message.author == bot.user:
        return

    # Verificar si el mensaje contiene palabras restringidas
    if check_message_for_restricted_words(message):
        await message.delete()  # Eliminar el mensaje si contiene palabras restringidas
        await message.channel.send(f"No, no, no, eso no se dice, {message.author.mention}.")
    
    await bot.process_commands(message)  # Asegura que otros comandos sigan funcionando

# Función para verificar el estado de la seguridad del servidor
# Variables globales que controlan el estado de seguridad
antiraid_enabled = False
antispam_enabled = False
word_filter_enabled = False

@bot.command()
async def securitystatus(ctx):
    """Mostrar el estado actual de las protecciones del servidor."""
    
    # Creamos el mensaje de estado de seguridad
    status_message = "**Estado de la Seguridad del Servidor:**\n"
    
    # Verifica el estado de cada configuración de seguridad
    status_message += f"Anti-Raid: {'Activado' if antiraid_enabled else 'Desactivado'}\n"
    status_message += f"Anti-Spam: {'Activado' if antispam_enabled else 'Desactivado'}\n"
    status_message += f"Filtro de Palabras: {'Activado' if word_filter_enabled else 'Desactivado'}\n"
    
    # Enviar el mensaje con el estado
    await ctx.send(status_message)

# Función para eliminar todas las palabras del filtro
def removeall_words_from_filter():
    global restricted_words
    restricted_words.clear()  # Vaciar la lista de palabras restringidas
    save_restricted_words()  # Guardar los cambios en el archivo JSON
    return "Todas las palabras han sido eliminadas del filtro."

# Comando para eliminar todas las palabras del filtro
@bot.command()
@commands.has_permissions(administrator=True)  # Solo administradores pueden eliminar todas las palabras
async def removeallfilter(ctx):
    """Comando para eliminar todas las palabras del filtro de palabras restringidas."""
    response = removeall_words_from_filter()  # Llamamos a la función para eliminar todas las palabras
    await ctx.send(response)

# =============================================================================================================

# Funciones iniciales para probar el bot
# =============================================================================================================

# Comando test 
@bot.command()
async def test(ctx, *args):
    respuesta = ' '.join(args)
    await ctx.send(f"¡Hola! Has enviado: {respuesta}")

# Comandos que haremos a partir de ahora con decoradores "@"

# Comando para obtener información del creador con enlace de Github
@bot.command()
async def creador(ctx):
    await ctx.send("¡Hola! Soy un bot creado por Jxlig0d. Puedes ver mi código en GitHub [aquí](https://github.com/jxliian)")

# Comandos de administración del bot
# =============================================================================================================

# Comando para reiniciar el bot (util para cada vez que se actualiza el código)

@bot.command()
@commands.is_owner()  # Solo el dueño del bot puede ejecutar este comando
async def reboot(ctx):
    await ctx.send("Reiniciando el bot...")
    await bot.close()  # Cierra el bot
    os.system("python3 main.py")  # Reinicia el bot ejecutando nuevamente el script

# Comando para verificar el estado del bot

@bot.command()
@commands.is_owner()  # Solo el dueño del bot puede ejecutar este comando
async def status(ctx):
    await ctx.send(f"El bot está {'online' if bot.is_ready() else 'offline'}.")


# Comando para mostrar el tiempo de actividad del bot

import time

start_time = time.time()

@bot.command()
async def uptime(ctx):
    uptime_seconds = int(time.time() - start_time)
    hours = uptime_seconds // 3600
    minutes = (uptime_seconds % 3600) // 60
    seconds = uptime_seconds % 60
    await ctx.send(f"El bot ha estado en línea durante {hours} horas, {minutes} minutos y {seconds} segundos.")

# =============================================================================================================

# Comandos de logs del bot
# =============================================================================================================

# Para mostrar los logs del servidor

@bot.command()
@commands.has_permissions(view_audit_log=True)  # Solo los usuarios con permisos de ver los registros pueden usarlo
async def securitylog(ctx, limit: int = 5):  # El argumento `limit` ahora tiene un valor predeterminado de 5
    # Obtener los registros de auditoría con el límite especificado
    logs = [log async for log in ctx.guild.audit_logs(limit=limit)]  # Usamos limit como parámetro con nombre
    
    # Obtener el número total de registros de auditoría disponibles de manera asíncrona
    total_logs = 0
    async for _ in ctx.guild.audit_logs():
        total_logs += 1  # Contar los logs disponibles
    
    if logs:
        log_message = f"**Últimos {len(logs)} de {total_logs} eventos de seguridad:**\n"  # Muestra el número total de logs
        for log in logs:
            log_message += f"{log.action} por {log.user} - {log.target} ({log.reason if log.reason else 'Sin razón especificada'})\n"
        await ctx.send(log_message)
    else:
        await ctx.send(f"No se han encontrado registros de seguridad recientes (últimos {limit} logs).")

# =============================================================================================================

# ================================================== Comandos de Protección ======================================================================s


antiraid_enabled = False

@bot.command()
@commands.has_permissions(administrator=True)
async def antiraid_on(ctx):
    """Activar la protección anti-raid."""
    global antiraid_enabled
    antiraid_enabled = True
    await ctx.send("Protección anti-raid activada.")



@bot.command()
@commands.has_permissions(administrator=True)
async def antiraid_off(ctx):
    """Desactivar la protección anti-raid."""
    global antiraid_enabled
    antiraid_enabled = False
    await ctx.send("Protección anti-raid desactivada.")



antispam_enabled = False

@bot.command()
@commands.has_permissions(administrator=True)
async def antispam_on(ctx):
    """Activar la protección contra spam."""
    global antispam_enabled
    antispam_enabled = True
    await ctx.send("Protección contra spam activada.")


@bot.command()
@commands.has_permissions(administrator=True)
async def antispam_off(ctx):
    """Desactivar la protección contra spam."""
    global antispam_enabled
    antispam_enabled = False
    await ctx.send("Protección contra spam desactivada.")


from collections import defaultdict
import asyncio

user_message_count = defaultdict(int)
MAX_MESSAGES_PER_MINUTE = 5

@bot.event
async def on_message(message):
    if message.author.bot:
        return
    
    if antispam_enabled:
        user_message_count[message.author.id] += 1
        
        if user_message_count[message.author.id] > MAX_MESSAGES_PER_MINUTE:
            await message.delete()  # Eliminar el mensaje
            await message.author.send("Estás enviando mensajes demasiado rápido. Por favor, modera tu actividad. 1 minuto de espera")
        
        await asyncio.sleep(60)  # Esperar 1 minuto antes de permitir más mensajes
        user_message_count[message.author.id] = 0  # Reiniciar el contador

    await bot.process_commands(message)

joined_recently = defaultdict(int)
JOIN_LIMIT = 5
JOIN_TIMEFRAME = 60  # Tiempo de 1 minuto

@bot.event
async def on_member_join(member):
    if antiraid_enabled:
        current_time = int(time.time())
        if current_time - joined_recently[member.guild.id] < JOIN_TIMEFRAME:
            # Si más de 5 miembros se han unido en menos de 1 minuto
            await member.kick(reason="Protección contra raid activada.")
            await member.send("Has sido expulsado debido a la activación de la protección anti-raid.")
        else:
            joined_recently[member.guild.id] = current_time




# ================================================== Comandos de Protección ======================================================================s



# ================================================== COMANDOS DE VERIFICACION ======================================================================s


@bot.command()
async def userinfo(ctx, user: discord.Member):
    """Mostrar información del usuario (incluyendo advertencias, bans, etc.)."""
    # Información básica
    embed = discord.Embed(title=f"Información de {user}", color=discord.Color.blue())
    embed.add_field(name="ID", value=user.id)
    embed.add_field(name="Nombre", value=user.name)
    embed.add_field(name="Apodo", value=user.nick if user.nick else "No tiene apodo")
    embed.add_field(name="Fecha de unión", value=user.joined_at.strftime("%d/%m/%Y"))
    embed.add_field(name="Fecha de creación de cuenta", value=user.created_at.strftime("%d/%m/%Y"))

    # Comprobación de advertencias
    user_id = str(user.id)
    if user_id in warns and warns[user_id]:
        warnings_list = "\n".join([f"Razón: {warning['reason']} - Moderador: {warning['moderator']} - Fecha: {warning['date']}" for warning in warns[user_id]])
        embed.add_field(name="Advertencias", value=warnings_list)
    else:
        embed.add_field(name="Advertencias", value="Este usuario no tiene advertencias.")

    await ctx.send(embed=embed)



@bot.command()
async def serverinfo(ctx):
    """Mostrar información sobre el servidor (miembros, roles, canales)."""
    server = ctx.guild
    embed = discord.Embed(title=f"Información de {server.name}", color=discord.Color.green())

    # Miembros
    total_members = len(server.members)
    online_members = len([m for m in server.members if m.status != discord.Status.offline])
    embed.add_field(name="Miembros", value=f"Total: {total_members}\nEn línea: {online_members}")

    # Roles
    roles = [role.name for role in server.roles]
    embed.add_field(name="Roles", value=", ".join(roles), inline=False)

    # Canales
    text_channels = len(server.text_channels)
    voice_channels = len(server.voice_channels)
    embed.add_field(name="Canales", value=f"Texto: {text_channels}\nVoz: {voice_channels}")

    await ctx.send(embed=embed)


@bot.command()
@commands.has_permissions(administrator=True)
async def auditlog(ctx, limit: int = 5):
    """Ver el registro de auditoría del servidor."""
    # Obtener el generador de los registros de auditoría
    logs = [entry async for entry in ctx.guild.audit_logs(limit=limit)]  # Convertimos el generador a lista

    embed = discord.Embed(title="Registro de Auditoría", color=discord.Color.purple())

    for entry in logs:
        embed.add_field(name=f"{entry.action}", value=f"Usuario: {entry.user}\nFecha: {entry.created_at.strftime('%d/%m/%Y %H:%M:%S')}", inline=False)

    await ctx.send(embed=embed)




# ================================================== COMANDOS DE VERIFICACION ======================================================================s


# ================================================== Comandos de Seguridad de Servidor ======================================================================s



@bot.command()
@commands.has_permissions(manage_channels=True)
async def lockdown(ctx, channel: discord.TextChannel = None):
    """Bloquear un canal para todos excepto administradores."""
    channel = channel or ctx.channel  # Si no se especifica un canal, usar el canal actual
    overwrite = discord.PermissionOverwrite()
    overwrite.send_messages = False  # Bloquear mensajes

    # Aplicar los permisos de bloqueo a todos los miembros
    for member in ctx.guild.members:
        if not member.guild_permissions.administrator:
            await channel.set_permissions(member, overwrite=overwrite)
    
    await ctx.send(f"Canal **{channel.name}** bloqueado para todos excepto administradores.")



@bot.command()
@commands.has_permissions(manage_channels=True)
async def unlock(ctx, channel: discord.TextChannel = None):
    """Desbloquear un canal."""
    channel = channel or ctx.channel  # Si no se especifica un canal, usar el canal actual
    overwrite = discord.PermissionOverwrite()
    overwrite.send_messages = None  # Restaurar los permisos predeterminados

    # Restaurar permisos a todos los miembros
    for member in ctx.guild.members:
        if not member.guild_permissions.administrator:
            await channel.set_permissions(member, overwrite=overwrite)
    
    await ctx.send(f"Canal **{channel.name}** desbloqueado.")


@bot.command()
@commands.has_permissions(administrator=True)
async def setprefix(ctx, new_prefix: str):
    """Cambiar el prefijo del bot."""
    # Guardar el nuevo prefijo en una variable o en una base de datos/configuración
    bot.prefix = new_prefix
    await ctx.send(f"El prefijo del bot ha sido cambiado a `{new_prefix}`.")


@bot.command()
@commands.has_permissions(administrator=True)
async def setlog(ctx, channel: discord.TextChannel):
    """Establecer un canal para logs de moderación."""
    # Guardar el canal en una variable o base de datos
    bot.log_channel = channel
    await ctx.send(f"El canal de registros de moderación ha sido configurado a {channel.mention}.")


@bot.command()
@commands.has_permissions(administrator=True)
async def setmod(ctx, role: discord.Role):
    """Establecer el rol de moderador."""
    bot.mod_role = role
    await ctx.send(f"El rol de moderador ha sido establecido a **{role.name}**.")

# ================================================== Comandos de Seguridad de Servidor ======================================================================


# ================================================== COMANDOS DE MODERACION GENERAL ======================================================================s




@bot.command()
@commands.has_permissions(kick_members=True)
async def kick(ctx, user: discord.Member, *, reason: str = None):
    """Expulsar a un usuario con una razón opcional"""
    try:
        await user.kick(reason=reason)
        await ctx.send(f"**{user}** ha sido expulsado del servidor. Razón: {reason if reason else 'No se proporcionó razón.'}")
    except discord.DiscordException as e:
        await ctx.send(f"Error al expulsar a {user}: {e}")



@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, user: discord.Member, *, reason: str = None):
    """Banear a un usuario con una razón opcional"""
    try:
        await user.ban(reason=reason)
        await ctx.send(f"**{user}** ha sido baneado del servidor. Razón: {reason if reason else 'No se proporcionó razón.'}")
    except discord.DiscordException as e:
        await ctx.send(f"Error al banear a {user}: {e}")


@bot.command()
@commands.has_permissions(ban_members=True)
async def unban(ctx, user: discord.User):
    """Desbanear a un usuario"""
    try:
        await ctx.guild.unban(user)
        await ctx.send(f"**{user}** ha sido desbaneado del servidor.")
    except discord.DiscordException as e:
        await ctx.send(f"Error al desbanear a {user}: {e}")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def mute(ctx, user: discord.Member, *, reason: str = None):
    """Silenciar a un usuario con una razón opcional"""
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if not mute_role:
        mute_role = await ctx.guild.create_role(name="Muted")

    # Asignar permisos para "Silenciar"
    await user.add_roles(mute_role, reason=reason)
    await ctx.send(f"**{user}** ha sido silenciado. Razón: {reason if reason else 'No se proporcionó razón.'}")


@bot.command()
@commands.has_permissions(manage_roles=True)
async def unmute(ctx, user: discord.Member):
    """Desilenciar a un usuario"""
    mute_role = discord.utils.get(ctx.guild.roles, name="Muted")
    if mute_role:
        await user.remove_roles(mute_role)
        await ctx.send(f"**{user}** ha sido desilenciado.")
    else:
        await ctx.send("No se encontró un rol de 'Muted'.")


warns_file = "warns.json"

# Función para cargar las advertencias desde el archivo
def load_warns():
    if os.path.exists(warns_file):
        try:
            with open(warns_file, "r") as file:
                warns_data = json.load(file)
                # Asegúrate de que el dato cargado es un diccionario
                if not isinstance(warns_data, dict):
                    return {}  # Si no es un diccionario, devolvemos un diccionario vacío
                return warns_data
        except json.JSONDecodeError:
            # Si el archivo tiene un error de formato, inicializamos un diccionario vacío
            print(f"Error en el archivo {warns_file}. Inicializando con un archivo vacío.")
            return {}  # Retorna un diccionario vacío si el archivo tiene datos inválidos
    return {}  # Si el archivo no existe, inicializa con un diccionario vacío


# Función para guardar las advertencias en el archivo
def save_warns(warns):
    with open(warns_file, "w") as file:
        json.dump(warns, file, indent=4)

# Cargar las advertencias al iniciar el bot
warns = load_warns()

@bot.command()
@commands.has_permissions(kick_members=True)
async def warn(ctx, user: discord.Member, *, reason: str = None):
    """Advertir a un usuario y almacenar la advertencia en un archivo"""
    user_id = str(user.id)  # Usamos el ID del usuario como clave, ya que es único
    
    if user_id not in warns:
        warns[user_id] = []  # Si el usuario no tiene advertencias, iniciamos una lista vacía

    # Agregamos la razón de la advertencia a la lista de advertencias
    warns[user_id].append({"reason": reason, "moderator": str(ctx.author), "date": str(ctx.message.created_at)})

    # Guardar las advertencias en el archivo
    save_warns(warns)

    # Enviamos un mensaje de confirmación
    await ctx.send(f"**{user}** ha recibido una advertencia. Razón: {reason if reason else 'No se proporcionó razón.'}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def warnings(ctx, user: discord.Member):
    """Mostrar las advertencias de un usuario"""
    user_id = str(user.id)
    
    if user_id not in warns or not warns[user_id]:
        await ctx.send(f"**{user}** no tiene advertencias.")
        return

    # Mostrar las advertencias
    warnings_list = "\n".join(
        [f"Razón: {warning['reason']} - Moderador: {warning['moderator']} - Fecha: {warning['date']}"
         for warning in warns[user_id]]
    )

    await ctx.send(f"**Advertencias de {user}:**\n{warnings_list}")

@bot.command()
@commands.has_permissions(kick_members=True)
async def clearwarns(ctx, user: discord.Member):
    """Eliminar todas las advertencias de un usuario"""
    user_id = str(user.id)

    if user_id not in warns or not warns[user_id]:
        await ctx.send(f"**{user}** no tiene advertencias.")
        return

    # Limpiar las advertencias del usuario
    warns[user_id] = []

    # Guardar los cambios en el archivo
    save_warns(warns)

    await ctx.send(f"Todas las advertencias de **{user}** han sido eliminadas.")

@bot.command()
@commands.has_permissions(kick_members=True)
async def removewarning(ctx, user: discord.Member, index: int):
    """Eliminar una advertencia específica de un usuario"""
    user_id = str(user.id)

    if user_id not in warns or not warns[user_id]:
        await ctx.send(f"**{user}** no tiene advertencias.")
        return

    # Eliminar la advertencia por índice
    try:
        removed_warning = warns[user_id].pop(index - 1)
        save_warns(warns)
        await ctx.send(f"Advertencia eliminada: Razón: {removed_warning['reason']}")
    except IndexError:
        await ctx.send("Índice de advertencia no válido.")

@bot.command()
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int):
    """Eliminar un número específico de mensajes en el canal"""
    try:
        deleted = await ctx.channel.purge(limit=amount)
        await ctx.send(f"Se han eliminado {len(deleted)} mensajes.", delete_after=5)
    except discord.DiscordException as e:
        await ctx.send(f"Error al eliminar mensajes: {e}")


# ================================================== COMANDOS DE MODERACION GENERAL ======================================================================s



# ================================================= COMANDOS DE GESTIÓN DE ROLES ======================================================================s


# Comando para asignar un rol a un usuario
@bot.command()
@commands.has_permissions(manage_roles=True)
async def addrole(ctx, member: discord.Member, role: discord.Role):
    """Asignar un rol a un usuario"""
    try:
        await member.add_roles(role)
        await ctx.send(f"Se ha asignado el rol {role.name} a {member.name}.")
    except discord.DiscordException as e:
        await ctx.send(f"Error al asignar el rol: {e}")

# Comando para eliminar un rol de un usuario
@bot.command()
@commands.has_permissions(manage_roles=True)
async def removerole(ctx, member: discord.Member, role: discord.Role):
    """Eliminar un rol de un usuario"""
    try:
        await member.remove_roles(role)
        await ctx.send(f"Se ha eliminado el rol {role.name} de {member.name}.")
    except discord.DiscordException as e:
        await ctx.send(f"Error al eliminar el rol: {e}")

# Comando para crear un nuevo rol con permisos opcionales
@bot.command()
@commands.has_permissions(manage_roles=True)
async def createrole(ctx, name: str, *permissions: str):
    """Crear un nuevo rol con permisos opcionales"""
    try:
        # Empezamos con permisos por defecto (ningún permiso)
        perms = discord.Permissions.none()

        # Si se pasan permisos, vamos a añadirlos
        if permissions:
            for perm in permissions:
                # Normalizamos el nombre del permiso a minúsculas y asignamos el permiso correspondiente
                perm = perm.lower()
                if hasattr(discord.Permissions, perm):
                    setattr(perms, perm, True)
                else:
                    await ctx.send(f"El permiso '{perm}' no es válido.")
                    return

        # Crear el rol con los permisos asignados
        new_role = await ctx.guild.create_role(name=name, permissions=perms)
        await ctx.send(f"Rol {new_role.name} creado con éxito con permisos: {', '.join(permissions)}.")
    
    except discord.DiscordException as e:
        await ctx.send(f"Error al crear el rol: {e}")


# Comando para eliminar un rol
@bot.command()
@commands.has_permissions(manage_roles=True)
async def deleterole(ctx, role: discord.Role):
    """Eliminar un rol del servidor"""
    try:
        await role.delete()
        await ctx.send(f"Rol {role.name} eliminado con éxito.")
    except discord.DiscordException as e:
        await ctx.send(f"Error al eliminar el rol: {e}")




# ========================================================================= FINAL =============================================================================s

@bot.event
async def on_ready():
    print(f"Bot {bot.user.name} ha iniciado sesión correctamente.")

bot.run(security.TOKEN)  # Asegúrate de que el token esté definido en security.py

