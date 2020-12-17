import discord
import asyncio
import re
from discord.ext import commands
import sys
import traceback
import datetime
import setup
time_regex = re.compile("(?:(\d{1,5})(h|s|m|d))+?")
time_dict = {"h":3600, "s":1, "m":60, "d":86400}

class TimeConverter(commands.Converter):
    async def convert(self, ctx, argument):
        args = argument.lower()
        matches = re.findall(time_regex, args)
        time = 0
        for v, k in matches:
            try:
                time += time_dict[k]*float(v)
            except KeyError:
                raise commands.BadArgument("{} is an invalid time-key! h/m/s/d are valid!".format(k))
            except ValueError:
                raise commands.BadArgument("{} is not a number!".format(v))
        return time

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mod_color = discord.Colour(0x7289da)
    async def mod_embed(self, ctx, user, success, method, reason):
        """ Helper func to format an embed to prevent extra code """
        modembed = discord.Embed(color=self.mod_color)
        modembed.set_author(name=method.title(), icon_url=user.avatar_url)
        modembed.set_footer(text=f'User ID: {user.id}')
        if success:
        	modembed.description = f"{str(member)} just got {method}."
        else:
        	modembed.description = f"You do not have the permissions to {method} users."
        await ctx.send(embed=modembed)

    @commands.command(no_pm=True)
    @commands.has_any_role(setup.modrolenames())
    async def kick(self,ctx,member: discord.Member=None, *,reason=None):
        """ ᗣ Kick someone from the server """
        if not member:
            return await ctx.send('You have to provide the id of the user you wanna kick!')
        if not reason:
            return await ctx.send(f'Provide a reason to kick {member}')
        else:
            try:
                await ctx.guild.kick(member, reason=reason)
            except:
                success = False
            else:
                success = True
        await self.mod_embed(ctx,member,success,"kick",reason)


            
    @commands.command(no_pm=True)
    @commands.has_any_role(setup.modrolenames())
    async def ban(self,ctx,member: discord.Member,*,reason=None):
        """ ᗣ Ban someone from the server """
        if not member:
            return await ctx.send('You have to provide the id or name of the user you wanna unban!')
        if not reason:
            return await ctx.send(f'Provide a reason to ban {member}')
        else:
            try:
                await ctx.guild.ban(member, reason=reason)
            except:
                success = False
            else:
                success = True
					await self.mod_embed(ctx,member,success,"kick",reason)

    @commands.command(no_pm=True)
    @commands.has_any_role(setup.modrolenames())
    async def unban(self, ctx, id=None):
        """ ᗣ Unban someone from the server """
        user = await self.bot.fetch_user(id)
        guild = ctx.guild
        if id is None:
            return await ctx.send('You have to provide the id or name of the user you wanna unban!')
        else:
            try:
                await ctx.guild.unban(user)
            except:
                success = False
            else:
                success = True
            unbanembed = discord.Embed(color=0x7289da)
            unbanembed.set_author(name='Unban', icon_url=user.avatar_url)
            unbanembed.description = f'{str(user)} just got Unbanned.'
            unbanembed.set_footer(text=f'User ID: {user.id}')
            await ctx.send(embed = unbanembed)

    @commands.command(aliases=['del', 'p', 'prune'], bulk=True, no_pm=True)
    @commands.has_any_role(setup.modrolenames())
    async def purge(self, ctx, limit: int):
        """ ᗣ Clean messages from chat """
        if limit is None:
            return await ctx.send(
                'Enter the number of messages you want me to delete.')
        if limit < 101:
            await ctx.message.delete()
            deleted = await ctx.channel.purge(limit=limit)
            purge = discord.Embed(color=0x7289da)
            purge.set_author(name='Purge')
            purge.description = f'Successfully deleted {len(deleted)} message(s)'
            purge.set_footer(text=f'Channel: {ctx.channel}')
            await ctx.send(embed = purge, delete_after=6)
        else:
            await ctx.send(f'Cannot delete `{limit}`, try with less than 100.',delete_after=23)

    @commands.command(no_pm=True)
    @commands.has_any_role(setup.modrolenames())
    async def bans(self, ctx):
        """ ᗣ See a list of banned users """
        try:
            bans = await ctx.guild.bans()
        except:
            return await ctx.send(
                "You don't have the perms to see bans.")
        e = discord.Embed(color=self.mod_color)
        e.set_author(
            name=f'List of Banned Members ({len(bans)}):',
            icon_url=ctx.guild.icon_url)
        result = ',\n'.join(
            ["[" + (str(b.user.id) + "] " + str(b.user)) for b in bans])
        if len(result) < 1990:
            total = result
        else:
            total = result[:1990]
            e.set_footer(text=f'Too many bans to show here!')
        e.description = f'```bf\n{total}```'
        await ctx.send(embed=e)

    @commands.command(no_pm=True)
    @commands.has_any_role(setup.modrolenames())
    async def slowmode(self,ctx, seconds: int):
        """ ᗣ Set the slowmode in the channel """
        await ctx.channel.edit(slowmode_delay=seconds)
        purge = discord.Embed(color=0x7289da)
        purge.set_author(name='Slowmode')
        purge.description = f"Set the slowmode delay in this channel to {seconds} seconds!"
        purge.set_footer(text=f'Channel: {ctx.channel}')
        await ctx.send(embed = purge, delete_after=23)

    @commands.command(no_pm=True)
    @commands.has_any_role(setup.modrolenames())
    async def mute(self, ctx, member:discord.Member, *, time:TimeConverter = None):
		""" ᗣ Mutes someone in the server """
      if time is None:
        tm="∞"
      else:
        tim = time/60
        float_time = tim
        hours, seconds = divmod(float_time * 60, 3600)
        minutes, seconds = divmod(seconds, 60)
        tm = "{:02.0f}:{:02.0f}.{:02.0f}".format(hours, minutes, seconds)
      if discord.utils.get(ctx.guild.roles, name='Muted') == None:
        muted = await ctx.guild.create_role(name="Muted", reason="To use for muting")
        for channel in ctx.guild.channels:
          await channel.set_permissions(muted, send_messages=False)
      role = discord.utils.get(ctx.guild.roles, name="Muted")
      if role in member.roles:
        await ctx.send("This user is already muted.")
      else:
        await member.add_roles(role)
        mute = discord.Embed(color=0x7289da)
        mute.set_author(name='Mute', icon_url=member.avatar_url)
        mute.description = f'{str(member)} got muted for {tm}]'.replace(':','h ').replace(".","m ").replace("]","s")
        mute.set_footer(text=f'User ID: {member.id}')
        await ctx.send(embed = mute)
        if time:
          await asyncio.sleep(time)
          await member.remove_roles(role)
    @commands.command(no_pm=True)
    @commands.has_any_role(setup.modrolenames())
    async def unmute(self, ctx, member: discord.Member):
			""" ᗣ Unmutes someone in the server """
      role = discord.utils.get(ctx.guild.roles, name="Muted")
      if role in member.roles:
        await member.remove_roles(role)
        unmute = discord.Embed(color=0x7289da)
        unmute.set_author(name='Unmute', icon_url=member.avatar_url)
        unmute.description = f'{str(member)} got unmuted.'
        unmute.set_footer(text=f'User ID: {member.id}')
        await ctx.send(embed = unmute)
      else:
        await ctx.send("This user isn't muted!")


def setup(bot):
    bot.add_cog(Moderation(bot))
