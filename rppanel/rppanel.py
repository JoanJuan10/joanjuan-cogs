from red_commons.logging import getLogger
from redbot.core import commands, app_commands
import discord
from typing import Optional

log = getLogger("red.rppanel")

class RPPanel(commands.Cog):
    """Panel básico para utilidades de rol con soporte a comandos de prefijo y slash separados.

    - Prefijo: [p]rppanel ping
    - Slash: /rppanel ping
    """

    # Definimos el grupo slash (no invocable directamente como comando, solo subcomandos)
    rppanel_app = app_commands.Group(name="rppanel", description="Comandos del panel RP")

    def __init__(self, bot):
        self.bot = bot
        log.debug("RPPanel inicializado")

    # ---------- Comandos de prefijo ----------
    @commands.group(name="rppanel")
    async def rppanel_group(self, ctx: commands.Context):
        """Grupo de comandos RP (prefijo)."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Usa un subcomando válido. Ej: [p]rppanel ping")

    @rppanel_group.command(name="ping")
    async def ping_prefix(self, ctx: commands.Context, modo: Optional[str] = None):
        """Prueba de respuesta (prefijo) con modo opcional.

        modo: normal | efimero | debug (no sensible a mayúsculas)
        """
        modo_l = (modo or "normal").lower()
        latency_ms = round(self.bot.latency * 1000, 2) if self.bot.latency else 0
        base = f"Pong! Latencia: {latency_ms} ms"
        if modo_l.startswith("debug"):
            base += f" | WebSocket latency raw: {self.bot.latency:.4f}s"
        await ctx.send(base)

    # ---------- Comandos slash ----------
    @rppanel_app.command(name="ping", description="Prueba de respuesta")
    @app_commands.describe(modo="normal | efimero | debug")
    async def ping_slash(self, interaction: discord.Interaction, modo: Optional[str] = None):  # type: ignore[override]
        """Prueba de respuesta (slash) con argumento autocompletado."""
        modo_l = (modo or "normal").lower()
        latency_ms = round(interaction.client.latency * 1000, 2) if interaction.client.latency else 0
        ephemeral = False
        extra = ""
        if modo_l.startswith("efi"):
            ephemeral = True
        if modo_l.startswith("debug"):
            extra = f" | raw: {interaction.client.latency:.4f}s"
        content = f"Pong! Latencia: {latency_ms} ms{extra}"
        await interaction.response.send_message(content, ephemeral=ephemeral)

    @ping_slash.autocomplete("modo")
    async def ping_slash_modo_autocomplete(self, interaction: discord.Interaction, current: str):  # type: ignore[override]
        opciones = [
            ("normal", "normal"),
            ("efimero (respuesta solo para ti)", "efimero"),
            ("debug (info extra)", "debug"),
        ]
        current_l = current.lower()
        filtered = [c for c in opciones if current_l in c[1]] if current else opciones
        return [app_commands.Choice(name=n, value=v) for n, v in filtered[:5]]

    # ---------- Utilidades internas ----------
    def cog_unload(self):
        # Intentamos retirar el grupo del árbol al descargar el cog para evitar duplicados en recargas.
        try:
            self.bot.tree.remove_command("rppanel")  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover - silencioso
            pass
