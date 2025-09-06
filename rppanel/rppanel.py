from red_commons.logging import getLogger
from redbot.core import commands, app_commands, Config
import discord
from typing import Optional, Dict, Any
from datetime import datetime

log = getLogger("red.rppanel")

class RPPanel(commands.Cog):
    """Basic role-play utilities panel with separated prefix and slash commands.

    - Prefix: [p]rppanel ping
    - Slash: /rppanel ping
    """

    # Slash group (not directly invokable, only subcommands)
    rppanel_app = app_commands.Group(name="rppanel", description="RP panel commands")

    def __init__(self, bot):
        self.bot = bot
        # Config: store instances per guild.
        # Structure: { name_lower: {"display": original_name, "created_by": user_id, "created_at": iso, "active": bool } }
        self.config: Config = Config.get_conf(self, identifier=0x5A7A2F11C0, force_registration=True)
        self.config.register_guild(instances={})
        log.debug("RPPanel initialized")

    # ---------- Prefix commands ----------
    @commands.group(name="rppanel")
    async def rppanel_group(self, ctx: commands.Context):
        """RP command group (prefix)."""
        if ctx.invoked_subcommand is None:
            await ctx.send("Use a valid subcommand. E.g.: [p]rppanel ping")

    @rppanel_group.command(name="ping")
    async def ping_prefix(self, ctx: commands.Context, mode: Optional[str] = None):
        """Ping (prefix) with optional mode.

        mode: normal | ephemeral | debug (case-insensitive)
        """
        mode_l = (mode or "normal").lower()
        latency_ms = round(self.bot.latency * 1000, 2) if self.bot.latency else 0
        base = f"Pong! Latency: {latency_ms} ms"
        if mode_l.startswith("debug"):
            base += f" | Raw WS: {self.bot.latency:.4f}s"
        await ctx.send(base)

    # ---------- Slash commands ----------
    @rppanel_app.command(name="ping", description="Ping response test")
    @app_commands.describe(mode="normal | ephemeral | debug")
    async def ping_slash(self, interaction: discord.Interaction, mode: Optional[str] = None):  # type: ignore[override]
        """Ping (slash) with autocomplete argument."""
        mode_l = (mode or "normal").lower()
        latency_ms = round(interaction.client.latency * 1000, 2) if interaction.client.latency else 0
        ephemeral = False
        extra = ""
        if mode_l.startswith("eph"):
            ephemeral = True
        if mode_l.startswith("debug"):
            extra = f" | Raw: {interaction.client.latency:.4f}s"
        content = f"Pong! Latency: {latency_ms} ms{extra}"
        await interaction.response.send_message(content, ephemeral=ephemeral)

    @ping_slash.autocomplete("mode")
    async def ping_slash_mode_autocomplete(self, interaction: discord.Interaction, current: str):  # type: ignore[override]
        options = [
            ("normal", "normal"),
            ("ephemeral (only you see it)", "ephemeral"),
            ("debug (extra info)", "debug"),
        ]
        current_l = current.lower()
        filtered = [c for c in options if current_l in c[1]] if current else options
        return [app_commands.Choice(name=n, value=v) for n, v in filtered[:5]]

    # ---------- Helper methods ----------
    async def _get_instances(self, guild: discord.Guild) -> Dict[str, Dict[str, Any]]:
        return await self.config.guild(guild).instances()

    async def _save_instances(self, guild: discord.Guild, data: Dict[str, Dict[str, Any]]):
        await self.config.guild(guild).instances.set(data)

    def _sanitize_name(self, name: str) -> str:
        return name.strip().lower()

    # ---------- Prefix: create instance ----------
    @rppanel_group.command(name="create")
    async def create_prefix(self, ctx: commands.Context, name: str):
        """Create a new instance with the given name."""
        if not name or len(name) > 50:
            return await ctx.send("Name must be between 1 and 50 characters.")
        guild = ctx.guild
        if guild is None:
            return await ctx.send("Guild only.")
        key = self._sanitize_name(name)
        instances = await self._get_instances(guild)
        if key in instances:
            return await ctx.send(f"An instance with that name already exists: {instances[key]['display']}")
        instances[key] = {
            "display": name,
            "created_by": ctx.author.id,
            "created_at": datetime.utcnow().isoformat(),
            "active": True,
        }
        await self._save_instances(guild, instances)
        await ctx.send(f"Instance '{name}' created.")

    # ---------- Prefix: delete instance ----------
    @rppanel_group.command(name="delete")
    async def delete_prefix(self, ctx: commands.Context, name: str):
        """Delete an existing instance by name (case-insensitive)."""
        if not name:
            return await ctx.send("Provide a name to delete.")
        guild = ctx.guild
        if guild is None:
            return await ctx.send("Guild only.")
        key = self._sanitize_name(name)
        instances = await self._get_instances(guild)
        if key not in instances:
            return await ctx.send("Instance not found.")
        removed = instances.pop(key)
        await self._save_instances(guild, instances)
        await ctx.send(f"Instance '{removed['display']}' deleted.")

    @rppanel_group.command(name="list")
    async def list_prefix(self, ctx: commands.Context):
        """List stored instances (prefix)."""
        guild = ctx.guild
        if guild is None:
            return await ctx.send("Guild only.")
        instances = await self._get_instances(guild)
        if not instances:
            return await ctx.send("No instances found.")
        # Sort by creation time (oldest first)
        def _sort_key(item):
            return item[1].get("created_at", "")
        items = sorted(instances.items(), key=_sort_key)
        lines = []
        for key, meta in items[:20]:
            lines.append(self._format_instance_line(meta))
        if len(items) > 20:
            lines.append(f"… {len(items) - 20} more not shown")
        await ctx.send("Instances:\n" + "\n".join(lines))

    # ---------- Slash: create instance ----------
    @rppanel_app.command(name="create", description="Create a new instance")
    @app_commands.describe(name="Instance name")
    async def create_slash(self, interaction: discord.Interaction, name: str):  # type: ignore[override]
        if not interaction.guild:
            return await interaction.response.send_message("Guild only.", ephemeral=True)
        if not name or len(name) > 50:
            return await interaction.response.send_message("Name must be between 1 and 50 characters.", ephemeral=True)
        key = self._sanitize_name(name)
        instances = await self._get_instances(interaction.guild)
        if key in instances:
            return await interaction.response.send_message("Instance already exists.", ephemeral=True)
        instances[key] = {
            "display": name,
            "created_by": interaction.user.id,
            "created_at": datetime.utcnow().isoformat(),
            "active": True,
        }
        await self._save_instances(interaction.guild, instances)
        await interaction.response.send_message(f"Instance '{name}' created.", ephemeral=True)

    # ---------- Slash: delete instance ----------
    @rppanel_app.command(name="delete", description="Delete an instance")
    @app_commands.describe(name="Instance name")
    @app_commands.autocomplete(name=lambda self, interaction, current: self._instance_name_choices(interaction, current))
    async def delete_slash(self, interaction: discord.Interaction, name: str):  # type: ignore[override]
        if not interaction.guild:
            return await interaction.response.send_message("Guild only.", ephemeral=True)
        key = self._sanitize_name(name)
        instances = await self._get_instances(interaction.guild)
        if key not in instances:
            return await interaction.response.send_message("Instance not found.", ephemeral=True)
        removed = instances.pop(key)
        await self._save_instances(interaction.guild, instances)
        await interaction.response.send_message(f"Instance '{removed['display']}' deleted.", ephemeral=True)

    @rppanel_app.command(name="list", description="List instances")
    async def list_slash(self, interaction: discord.Interaction):  # type: ignore[override]
        if not interaction.guild:
            return await interaction.response.send_message("Guild only.", ephemeral=True)
        instances = await self._get_instances(interaction.guild)
        if not instances:
            return await interaction.response.send_message("No instances found.", ephemeral=True)
        def _sort_key(item):
            return item[1].get("created_at", "")
        items = sorted(instances.items(), key=_sort_key)
        lines = []
        for key, meta in items[:25]:
            lines.append(self._format_instance_line(meta))
        if len(items) > 25:
            lines.append(f"… {len(items) - 25} more not shown")
        content = "Instances:\n" + "\n".join(lines)
        # Use ephemeral to avoid clutter
        await interaction.response.send_message(content, ephemeral=True)

    # Autocomplete for a future 'instance' parameter in other commands (re-usable)
    async def instance_name_autocomplete(self, interaction: discord.Interaction, current: str):
        # Deprecated helper; kept for backward compatibility if referenced elsewhere.
        return await self._instance_name_choices(interaction, current)

    async def _instance_name_choices(self, interaction: discord.Interaction, current: str):
        if not interaction.guild:
            return []
        instances = await self._get_instances(interaction.guild)
        current_l = current.lower()
        matches = [meta for key, meta in instances.items() if current_l in key or current_l in meta["display"].lower()]
        return [app_commands.Choice(name=m["display"], value=m["display"]) for m in matches[:20]]

    def _format_instance_line(self, meta: Dict[str, Any]) -> str:
        disp = meta.get("display", "?")
        created_at = meta.get("created_at")
        active = meta.get("active", True)
        ts_part = ""
        try:
            if created_at:
                dt = datetime.fromisoformat(created_at)
                ts_part = f" <t:{int(dt.timestamp())}:R>"
        except Exception:
            pass
        status = "active" if active else "inactive"
        return f"- {disp} ({status}){ts_part}"

    # ---------- Internal utilities ----------
    def cog_unload(self):
        # Remove the group from the tree on unload to prevent duplicates on reload.
        try:
            self.bot.tree.remove_command("rppanel")  # type: ignore[attr-defined]
        except Exception:  # pragma: no cover
            pass
