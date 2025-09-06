from .rppanel import RPPanel

async def setup(bot):
    cog = RPPanel(bot)
    await bot.add_cog(cog)
    # Añadimos el grupo slash manualmente
    try:
        bot.tree.add_command(cog.rppanel_app)  # type: ignore[attr-defined]
    except Exception:
        # Si ya existe, lo ignoramos.
        pass

async def teardown(bot):  # Red lo llamará al descargar
    try:
        bot.tree.remove_command("rppanel")
    except Exception:
        pass
