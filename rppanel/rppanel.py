from red_commons.logging import getLogger
from redbot.core import commands

log = getLogger("red.rppanel")

class RPPanel(commands.Cog):
    """Panel básico para utilidades de rol (placeholder) con soporte para slash commands."""

    def __init__(self, bot):
        self.bot = bot
        log.debug("RPPanel inicializado")

    @commands.hybrid_group(name="rppanel")
    async def rppanel_group(self, ctx: commands.Context):
        """Comandos del panel RP.

        (Slash) Usa /rppanel ping
        (Prefijo) Usa [p]rppanel ping
        """
        # Solo mostramos el mensaje si es invocado por prefijo sin subcomando.
        if ctx.invoked_subcommand is None and ctx.interaction is None:
            await ctx.send("Usa un subcomando válido. Ej: rppanel ping")

    @rppanel_group.command(name="ping", with_app_command=True)
    async def ping(self, ctx: commands.Context):
        """Prueba de respuesta (slash + prefijo)."""
        # ctx.send funciona tanto para interacciones (slash) como para prefijo.
        await ctx.send("RPPanel activo.")
