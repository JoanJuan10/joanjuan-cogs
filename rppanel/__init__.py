from .rppanel import RpPanel

__all__ = ["RpPanel"]
__version__ = "0.0.2"


async def setup(bot):
    """Load the cog into Red.

    Red looks for an async setup(bot) coroutine to add cogs.
    """
    await bot.add_cog(RpPanel(bot))
