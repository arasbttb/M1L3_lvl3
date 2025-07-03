import discord
from discord.ext import commands
from config import token  # Tokeni config dosyasından alıyoruz

# Gerekli intent'leri ayarlıyoruz
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.message_content = True

bot = commands.Bot(command_prefix='!', intents=intents)

# Bot hazır olduğunda konsola yazdır
@bot.event
async def on_ready():
    print(f'Giriş yapıldı: {bot.user.name}')

@bot.event
async def on_member_join(member):
    guild = member.guild
    kanal = discord.utils.get(guild.text_channels, name="「🚪」gelen-giden")  # Veya welcome kanalı
    if kanal:
        await kanal.send(f"👋 {member.mention}, {guild.name} sunucusuna hoş geldin! Yardım için `!help` yazabilirsin.")
    print(f"{member.name} sunucuya katıldı.")
@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if "http://" in message.content or "https://" in message.content:
        if not message.author.guild_permissions.administrator:
            await message.channel.send(f"{message.author.mention} link paylaşımı nedeniyle yasaklandı! 🚫")
            try:
                await message.guild.ban(message.author, reason="İzinsiz link paylaşımı")
            except discord.Forbidden:
                await message.channel.send("❌ Ban işlemi başarısız: Botun yetkisi yetersiz.")
            except discord.HTTPException as e:
                await message.channel.send(f"❌ Ban sırasında bir hata oluştu: {e}")
            return

    await bot.process_commands(message)

# Basit bir başlangıç komutu
@bot.command()
async def start(ctx):
    await ctx.send("Merhaba! Ben bir sohbet yöneticisi botuyum!")

# Ban komutu - sadece ban yetkisi olanlar kullanabilir
@bot.command()
@commands.has_permissions(ban_members=True)
async def ban(ctx, member: discord.Member = None):
    if member is None:
        await ctx.send("Lütfen banlamak istediğiniz kullanıcıyı etiketleyin. Örnek: `!ban @kullanıcı`")
        return

    if ctx.author.top_role <= member.top_role and ctx.author != ctx.guild.owner:
        await ctx.send("🚫 Bu kullanıcı sizden yüksek ya da eşit yetkide, banlanamaz.")
        return

    if ctx.guild.me.top_role <= member.top_role:
        await ctx.send("❌ Bu kullanıcı bot ile aynı veya daha yüksek rolde, banlanamaz.")
        return

    try:
        await ctx.guild.ban(member, reason=f"{ctx.author} tarafından banlandı.")
        await ctx.send(f"✅ Kullanıcı {member.name} başarıyla banlandı.")
    except discord.Forbidden:
        await ctx.send("❌ Botun yetkisi yetersiz, kullanıcı banlanamadı.")
    except discord.HTTPException as e:
        await ctx.send(f"❌ Ban işlemi sırasında hata oluştu: {e}")

# Ban hatalarını yakala
@ban.error
async def ban_error(ctx, error):
    if isinstance(error, commands.MissingPermissions):
        await ctx.send("🚫 Bu komutu kullanmak için 'ban_members' yetkisine sahip olmalısınız.")
    elif isinstance(error, commands.MemberNotFound):
        await ctx.send("❌ Kullanıcı bulunamadı.")
    else:
        await ctx.send(f"❌ Bir hata oluştu: {error}")

# Botu başlat
bot.run(token)
