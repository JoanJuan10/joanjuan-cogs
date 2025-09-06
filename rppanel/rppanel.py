from redbot.core import commands, Config
from redbot.core.bot import Red
from typing import Final


class RpPanel(commands.Cog):
    """Basic tools for managing a roleplay (RP) panel.

    This is a starting skeleton you can extend with more features.
    """

    __author__: Final[str] = "JoanJuan10"
    __version__: Final[str] = "0.1.0"

    def __init__(self, bot: Red):
        self.bot = bot
        self.config: Config = Config.get_conf(self, identifier=0xA11A11A11, force_registration=True)
    # Default guild-level config structure
        default_guild = {
            "enabled": True,
            "panels": {},  # panel_id -> {"title": str|None, "stats": {label: value}}
        }
        self.config.register_guild(**default_guild)

    # --------------------------------------------------
    # Info & utilities
    # --------------------------------------------------
    def format_help_for_context(self, ctx: commands.Context) -> str:  # type: ignore[override]
        base = super().format_help_for_context(ctx)
    return f"{base}\n\nAuthor: {self.__author__} | Version: {self.__version__}"

    async def red_delete_data_for_user(self, **kwargs):  # noqa: D401
        """This cog stores no persistent user data."""
        return

    @commands.hybrid_group(name="rppanel")
    async def rppanel(self, ctx: commands.Context):
        """RP panel commands."""
        pass

    @rppanel.command(name="ping")
    async def rppanel_ping(self, ctx: commands.Context):
        """Check if the cog is alive."""
        await ctx.send("RpPanel alive ✅")

    @rppanel.command(name="version")
    async def rppanel_version(self, ctx: commands.Context):
        """Show the cog version."""
        await ctx.send(f"RpPanel version {self.__version__}")

    # --------------------------------------------------
    # Toggle simple a nivel de servidor
    # --------------------------------------------------
    @rppanel.command(name="toggle")
    @commands.admin_or_permissions(manage_guild=True)
    async def rppanel_toggle(self, ctx: commands.Context):
        """Enable or disable the RP panel in this guild."""
        current = await self.config.guild(ctx.guild).enabled()
        await self.config.guild(ctx.guild).enabled.set(not current)
        state = "enabled" if not current else "disabled"
        await ctx.send(f"RP panel {state} for this guild.")

    # --------------------------------------------------
    # Panel management
    # --------------------------------------------------
    def _validate_panel_id(self, panel_id: str) -> bool:
        import re
        return bool(re.fullmatch(r"[A-Za-z0-9_\-]{1,30}", panel_id))

    @rppanel.command(name="create")
    @commands.admin_or_permissions(manage_guild=True)
    async def rppanel_create(self, ctx: commands.Context, panel_id: str, *, title: str | None = None):
        """Create a new panel with an identifier.

        panel_id: Alphanumeric, dash and underscore only (max 30 chars)
        title: Optional panel title.
        """
        if ctx.guild is None:
            return await ctx.send("Guild only command.")
        if not self._validate_panel_id(panel_id):
            return await ctx.send("Invalid panel_id. Use only letters, numbers, - and _. Max length 30.")
        panels = await self.config.guild(ctx.guild).panels()
        if panel_id in panels:
            return await ctx.send("Panel ID already exists.")
        panels[panel_id] = {"title": title, "stats": {}}
        await self.config.guild(ctx.guild).panels.set(panels)
        await ctx.send(f"Created panel `{panel_id}`{' with title' if title else ''}.")

    @rppanel.command(name="delete")
    @commands.admin_or_permissions(manage_guild=True)
    async def rppanel_delete(self, ctx: commands.Context, panel_id: str):
        """Delete a panel and its stats."""
        if ctx.guild is None:
            return await ctx.send("Guild only command.")
        panels = await self.config.guild(ctx.guild).panels()
        if panel_id not in panels:
            return await ctx.send("Panel not found.")
        del panels[panel_id]
        await self.config.guild(ctx.guild).panels.set(panels)
        await ctx.send(f"Deleted panel `{panel_id}`.")

    @rppanel.command(name="set")
    @commands.admin_or_permissions(manage_guild=True)
    async def rppanel_set(self, ctx: commands.Context, panel_id: str, label: str, *, value: str):
        """Add or update a stat label for a panel.

        Example: [p]rppanel set character1 HP 120/150
        """
        if ctx.guild is None:
            return await ctx.send("Guild only command.")
        if len(label) > 40:
            return await ctx.send("Label too long (max 40 chars).")
        if len(value) > 200:
            return await ctx.send("Value too long (max 200 chars).")
        panels = await self.config.guild(ctx.guild).panels()
        panel = panels.get(panel_id)
        if panel is None:
            return await ctx.send("Panel not found.")
        panel["stats"][label] = value
        await self.config.guild(ctx.guild).panels.set(panels)
        await ctx.send(f"Stat `{label}` set for panel `{panel_id}`.")

    @rppanel.command(name="remove")
    @commands.admin_or_permissions(manage_guild=True)
    async def rppanel_remove(self, ctx: commands.Context, panel_id: str, label: str):
        """Remove a stat label from a panel."""
        if ctx.guild is None:
            return await ctx.send("Guild only command.")
        panels = await self.config.guild(ctx.guild).panels()
        panel = panels.get(panel_id)
        if panel is None:
            return await ctx.send("Panel not found.")
        if label not in panel["stats"]:
            return await ctx.send("Stat label not found.")
        del panel["stats"][label]
        await self.config.guild(ctx.guild).panels.set(panels)
        await ctx.send(f"Removed `{label}` from `{panel_id}`.")

    @rppanel.command(name="show")
    async def rppanel_show(self, ctx: commands.Context, panel_id: str):
        """Display a panel with its stats."""
        if ctx.guild is None:
            return await ctx.send("Guild only command.")
        panels = await self.config.guild(ctx.guild).panels()
        panel = panels.get(panel_id)
        if panel is None:
            return await ctx.send("Panel not found.")
        stats = panel["stats"]
        if not stats:
            return await ctx.send("Panel has no stats yet.")
        from discord import Embed
        title = panel.get("title") or f"Panel: {panel_id}"
        embed = Embed(title=title)
        for label, value in stats.items():
            # Prevent empty field issue
            embed.add_field(name=label[:256] or "-", value=value[:1024] or "-", inline=False)
        embed.set_footer(text=f"RpPanel v{self.__version__}")
        await ctx.send(embed=embed)

    @rppanel.command(name="list")
    async def rppanel_list(self, ctx: commands.Context):
        """List available panel IDs."""
        if ctx.guild is None:
            return await ctx.send("Guild only command.")
        panels = await self.config.guild(ctx.guild).panels()
        if not panels:
            return await ctx.send("No panels created.")
        ids = ", ".join(sorted(panels.keys()))
        await ctx.send(f"Panels: {ids}")
