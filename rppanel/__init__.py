from .rppanel import RPPanel

async def setup(bot):
    await bot.add_cog(RPPanel(bot))
