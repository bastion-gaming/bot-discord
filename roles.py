import discord
from discord.ext import commands

client = discord.Client()

@client.event  # event decorator/wrapper.
async def on_ready():  # méthode attendue par le client. Cela fonctionne une fois connecté
    print('| Roles Module | >> Connecté !')  # notification de login.

async def autorole(member):
    role = discord.utils.get(member.guild.roles, name="Joueurs")
    await member.add_roles(role)


def creategame(message, game, categorie):
	"""
    Permet de créer un nouveau role pour un jeu de d'ajouter ce jeu dans un grand salon
    Paramètres:
    - game: Nom du jeu/role
    - categorie: Nom du grand salon (combat/societe/tirs/voiture/rpg/sandbox/strategie/divers)
    """
    guild = message.guild
    member = message.author
    rolesearch = discord.utils.get(member.guild.roles, name=game)
    if rolesearch == None:
        await guild.create_role(name=game)
        msg = "Le jeu '"+game+"' a été créé"

        if categorie != None:
            rolesearch = discord.utils.get(member.guild.roles, name=game)
            categorie = categorie.lower()

            if categorie == "combat":
                channeladd = guild.get_channel(589944955800256515)
            elif categorie == "societe":
                channeladd = guild.get_channel(589945591203889152)
            elif categorie == "tirs":
                channeladd = guild.get_channel(589946246437797888)
            elif categorie == "voiture":
                channeladd = guild.get_channel(589946276540448821)
            elif categorie == "rpg":
                channeladd = guild.get_channel(589946305917222916)
            elif categorie == "sandbox":
                channeladd = guild.get_channel(589946380416581632)
            elif categorie == "strategie":
                channeladd = guild.get_channel(589953946639007764)
            else:
                channeladd = guild.get_channel(590664052318142474)
            await channeladd.set_permissions(rolesearch, overwrite=discord.PermissionOverwrite(read_messages=True))
            msg = "Ajout d'un nouveau jeu dans la catégorie {}: {}".format(channeladd.mention, rolesearch.mention)
            channel = guild.get_channel(417449076775321600)
            return (channel.send(msg))
        else:
            return(message.channel.send(msg))
    else:
        return(message.channel.send("Le jeu "+game+" existe déjà"))




#async def create(message, meco):
#    """Commande !create game <nom du jeu>, <Categorie du jeu: combat/societe/tirs/voiture/rpg/sandbox/strategie/divers>"""
#    mecoS = meco.split(',')
#    guild = message.guild
#    member = message.author
#    rolesearch = discord.utils.get(member.guild.roles, name=mecoS[0])
#    if rolesearch == None:
#        await guild.create_role(name=mecoS[0])
#        await message.channel.send("Le jeu '"+mecoS[0]+"' a été créé")
#
#        if mecoS[1] != None:
#            rolesearch = discord.utils.get(member.guild.roles, name=mecoS[0])
#            mecoS[1] = mecoS[1].replace(" ", "")
#            mecoS[1] = mecoS[1].lower()
#
#            if mecoS[1] == "combat":
#                channel = guild.get_channel(589944955800256515)
#            elif mecoS[1] == "societe":
#                channel = guild.get_channel(589945591203889152)
#            elif mecoS[1] == "tirs":
#                channel = guild.get_channel(589946246437797888)
#            elif mecoS[1] == "voiture":
#                channel = guild.get_channel(589946276540448821)
#            elif mecoS[1] == "rpg":
#                channel = guild.get_channel(589946305917222916)
#            elif mecoS[1] == "sandbox":
#                channel = guild.get_channel(589946380416581632)
#            elif mecoS[1] == "strategie":
#                channel = guild.get_channel(589953946639007764)
#            else:
#                channel = guild.get_channel(590664052318142474)
#            await channel.set_permissions(rolesearch, overwrite=discord.PermissionOverwrite(read_messages=True))
#            await channel.send(f"Ajout d'un nouveau jeu dans la catégorie {channel.mention}: {rolesearch.mention}")
#    else:
#        await message.channel.send("Le jeu '"+mecoS[0]+"' existe déjà")
