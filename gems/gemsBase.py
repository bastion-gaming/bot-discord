import discord
import random as r
import time as t
import datetime as dt
from DB import DB
from gems import gemsFonctions as GF
from discord.ext import commands
from discord.ext.commands import bot
from discord.utils import get
from operator import itemgetter

class GemsBase(commands.Cog):

	def __init__(self,ctx):
		return(None)



	@commands.command(pass_context=True)
	async def tuto(self, ctx):
		"""Affiche le tutoriel !"""
		ID = ctx.author.id
		link = "https://www.youtube.com/watch?v="
		await ctx.channel.send(":tools: En travaux :pencil:\n{}".format(link))




	@commands.command(pass_context=True)
	async def begin(self, ctx):
		"""Pour t'ajouter dans la base de données !"""
		ID = ctx.author.id
		await ctx.channel.send(DB.newPlayer(ID))




	@commands.command(pass_context=True)
	async def bal(self, ctx, nom = None):
		"""**[nom]** | Êtes vous riche ou pauvre ?"""
		ID = ctx.author.id
		if DB.spam(ID,GF.couldown_c, "bal"):
			#print(nom)
			if nom != None:
				ID = DB.nom_ID(nom)
				nom = ctx.guild.get_member(ID)
				nom = nom.name
			else:
				nom = ctx.author.name
			solde = DB.valueAt(ID, "gems")
			title = "Compte principal de {}".format(nom)
			msg = discord.Embed(title = title,color= 13752280, description = "")
			desc = "{} :gem:\n".format(solde)
			msg.add_field(name="Balance", value=desc, inline=False)

			DB.updateComTime(ID, "bal")
			await ctx.channel.send(embed = msg)
			# Message de réussite dans la console
			print("Gems >> Balance de {} affichée".format(nom))
			return
		else:
			msg = "Il faut attendre "+str(GF.couldown_c)+" secondes entre chaque commande !"
		await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def baltop(self, ctx, n = 10):
		"""**[nombre]** | Classement des joueurs (10 premiers par défaut)"""
		ID = ctx.author.id
		if DB.spam(ID,GF.couldown_c, "baltop"):
			UserList = []
			baltop = ""
			i = 0
			while i < DB.taille():
				user = DB.userID(i)
				gems = DB.userGems(i)
				UserList.append((user, gems))
				i = i + 1
			UserList = sorted(UserList, key=itemgetter(1),reverse=False)
			i = DB.taille() - 1
			j = 0
			while i >= 0 and j != n : # affichage des données trié
				baltop += "{2} | <@{0}> {1}:gem:\n".format(UserList[i][0], UserList[i][1], j+1)
				i = i - 1
				j = j + 1
			DB.updateComTime(ID, "baltop")
			msg = discord.Embed(title = "Classement des joueurs",color= 13752280, description = baltop)
			await ctx.channel.send(embed = msg)
			# Message de réussite dans la console
			print("Gems >> {} a afficher le classement des {} premiers joueurs".format(ctx.author.name,n))
		else:
			msg = "Il faut attendre "+str(GF.couldown_c)+" secondes entre chaque commande !"
			await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def buy (self, ctx,item,nb = 1):
		"""**[item] [nombre]** | Permet d'acheter les items vendus au marché"""
		ID = ctx.author.id
		if DB.spam(ID,GF.couldown_c, "buy"):
			if GF.testInvTaille(ID):
				test = True
				nb = int(nb)
				for c in GF.objetItem :
					if item == c.nom :
						test = False
						prix = 0 - (c.achat*nb)
						if DB.addGems(ID, prix) >= "0":
							DB.add(ID, "inventory", c.nom, nb)
							if c.type != "consommable":
								msg = "Tu viens d'acquérir {0} <:gem_{1}:{2}>`{1}` !".format(nb, c.nom, c.idmoji)
							else:
								msg = "Tu viens d'acquérir {0} :{1}:`{1}` !".format(nb, c.nom)
							# Message de réussite dans la console
							print("Gems >> {} a acheté {} {}".format(ctx.author.name,nb,item))
						else :
							msg = "Désolé, nous ne pouvons pas executer cet achat, tu n'as pas assez de :gem: en banque"
						break
				for c in GF.objetOutil :
					if item == c.nom :
						test = False
						if c.type == "bank":
							soldeMax = DB.nbElements(ID, "banque", "soldeMax")
							if soldeMax == 0:
								soldeMax = c.poids
								DB.add(ID, "banque", "soldeMax", c.poids)
							soldeMult = soldeMax/c.poids
							prix = 0
							i = 1
							while i <= nb:
								prix += c.achat*soldeMult
								soldeMult+=1
								i+=1
							prix = -1 * prix
							prix = int(prix)
						else:
							prix = -1 * (c.achat*nb)
						if DB.addGems(ID, prix) >= "0":
							if c.type == "bank":
								DB.add(ID, "banque", "soldeMax", nb*c.poids)
								msg = "Tu viens d'acquérir {0} <:gem_{1}:{2}>`{1}` !".format(nb, c.nom, c.idmoji)
								# Message de réussite dans la console
								print("Gems >> {} a acheté {} {}".format(ctx.author.name,nb,item))
								await ctx.channel.send(msg)
								return
							else:
								DB.add(ID, "inventory", c.nom, nb)
								msg = "Tu viens d'acquérir {0} <:gem_{1}:{2}>`{1}` !".format(nb, c.nom, c.idmoji)
								if c.nom == "planting_plan":
									if GF.get_durabilite(ID, "planting_plan") == None:
										GF.addDurabilite(ID, "planting_plan", c.durabilite)
						else :
							msg = "Désolé, nous ne pouvons pas executer cet achat, tu n'as pas assez de :gem: en banque"
						break
				for c in GF.objetBox :
					if item == "lootbox_{}".format(c.nom) or item == c.nom :
						test = False
						prix = 0 - (c.achat*nb)
						if DB.addGems(ID, prix) >= "0":
							DB.add(ID, "inventory", "lootbox_{}".format(c.nom), nb)
							msg = "Tu viens d'acquérir {0} <:gem_lootbox:630698430313922580>`{1}` !".format(nb, c.titre)
							# Message de réussite dans la console
							print("Gems >> {} a acheté {} Loot Box {}".format(ctx.author.name,nb,c.nom))
						else :
							msg = "Désolé, nous ne pouvons pas executer cet achat, tu n'as pas assez de :gem: en banque"
						break
				if test :
					msg = "Cet item n'est pas vendu au marché !"

				DB.updateComTime(ID, "buy")
			else:
				msg = "Ton inventaire est plein"
		else:
			msg = "Il faut attendre "+str(GF.couldown_c)+" secondes entre chaque commande !"
		await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def sell (self, ctx,item,nb = 1):
		"""**[item] [nombre]** | Permet de vendre vos items !"""
		#cobble 1, iron 10, gold 50, diams 100
		ID = ctx.author.id
		# print(nb)
		# print(type(nb))
		if DB.spam(ID,GF.couldown_c, "sell"):
			if int(nb) == -1:
				nb = DB.nbElements(ID, "inventory", item)
			nb = int(nb)
			if DB.nbElements(ID, "inventory", item) >= nb and nb > 0:
				test = True
				for c in GF.objetItem:
					if item == c.nom:
						test = False
						gain = c.vente*nb
						DB.addGems(ID, gain)
						if c.type != "consommable":
							msg ="Tu as vendu {0} <:gem_{1}:{3}>`{1}` pour {2} :gem: !".format(nb,item,gain,c.idmoji)
							# Message de réussite dans la console
							print("Gems >> {} a vendu {} {}".format(ctx.author.name,nb,item))
						else:
							msg ="Tu as vendu {0} :{1}:`{1}` pour {2} :gem: !".format(nb,item,gain)
							# Message de réussite dans la console
							print("Gems >> {} a vendu {} {}".format(ctx.author.name,nb,item))
							if c.nom == "grapes" and int (nb/10) >= 1:
								nbwine = int(nb/10)
								DB.add(ID, "inventory", "wine_glass", nbwine)
								msg+="\nTu gagne {}:wine_glass:`verre de vin`".format(nbwine)
						break
				for c in GF.objetOutil:
					if item == c.nom:
						test = False
						gain = c.vente*nb
						DB.addGems(ID, gain)
						msg ="Tu as vendu {0} <:gem_{1}:{3}>`{1}` pour {2} :gem: !".format(nb,item,gain,c.idmoji)
						if DB.nbElements(ID, "inventory", item) == 1:
							if DB.get_durabilite(ID, item) != None:
								GF.addDurabilite(ID, item, -1)
						# Message de réussite dans la console
						print("Gems >> {} a vendu {} {}".format(ctx.author.name,nb,item))
						break

				DB.add(ID, "inventory", item, -nb)
				if test:
					msg = "Cette objet n'existe pas"
			else:
				#print("Pas assez d'élement")
				msg = "Tu n'as pas assez de `{0}`. Il t'en reste : {1}".format(str(item),str(DB.nbElements(ID, "inventory", item)))

			DB.updateComTime(ID, "sell")
		else:
			msg = "Il faut attendre "+str(GF.couldown_c)+" secondes entre chaque commande !"
		await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def inv (self, ctx):
		"""Permet de voir ce que vous avez dans le ventre !"""
		ID = ctx.author.id
		nom = ctx.author.name
		if DB.spam(ID,GF.couldown_c, "inv"):
			msg_inv = ""
			msg_invOutils = ""
			msg_invItems = ""
			msg_invItemsMinerai = ""
			msg_invItemsPoisson = ""
			msg_invItemsPlante = ""
			msg_invItemsConsommable = ""
			msg_invBox = ""
			inv = DB.valueAt(ID, "inventory")
			tailletot = 0
			for c in GF.objetOutil:
				for x in inv:
					if c.nom == str(x):
						if inv[x] > 0:
							msg_invOutils += "<:gem_{0}:{2}>`{0}`: `x{1}` | Durabilité: `{3}/{4}`\n".format(str(x), str(inv[x]), c.idmoji, GF.get_durabilite(ID, c.nom), c.durabilite)
							tailletot += c.poids*int(inv[x])

			for c in GF.objetItem:
				for x in inv:
					if c.nom == str(x):
						if inv[x] > 0:
							if c.type == "minerai":
								msg_invItemsMinerai += "<:gem_{0}:{2}>`{0}`: `x{1}`\n".format(str(x), str(inv[x]), c.idmoji)
							elif c.type == "poisson":
								msg_invItemsPoisson += "<:gem_{0}:{2}>`{0}`: `x{1}`\n".format(str(x), str(inv[x]), c.idmoji)
							elif c.type == "plante":
								msg_invItemsPlante += "<:gem_{0}:{2}>`{0}`: `x{1}`\n".format(str(x), str(inv[x]), c.idmoji)
							elif c.type == "consommable":
								msg_invItemsConsommable += ":{0}:`{0}`: `x{1}`\n".format(str(x), str(inv[x]))
							else:
								msg_invItems += "<:gem_{0}:{2}>`{0}`: `x{1}`\n".format(str(x), str(inv[x]), c.idmoji)

							tailletot += c.poids*int(inv[x])

			for c in GF.objetBox :
				for x in inv:
					name = "lootbox_{}".format(c.nom)
					if name == str(x):
						if inv[x] > 0:
							msg_invBox += "<:gem_lootbox:630698430313922580>`{0}`: `x{1}`\n".format(c.nom, str(inv[x]))

			msg_inv += "\nTaille: `{}/{}`".format(int(tailletot),GF.invMax)
			msg_titre = "Inventaire de {}\n\n".format(nom)
			msg = discord.Embed(title = msg_titre,color= 6466585, description = msg_inv)
			if msg_invOutils != "":
				msg.add_field(name="Outils", value=msg_invOutils, inline=False)
			if msg_invItems != "":
				msg.add_field(name="Items", value=msg_invItems, inline=False)
			if msg_invItemsMinerai != "":
				msg.add_field(name="Minerais", value=msg_invItemsMinerai, inline=False)
			if msg_invItemsPoisson != "":
				msg.add_field(name="Poissons", value=msg_invItemsPoisson, inline=False)
			if msg_invItemsPlante != "":
				msg.add_field(name="Plantes", value=msg_invItemsPlante, inline=False)
			if msg_invItemsConsommable != "":
				msg.add_field(name="Consommables", value=msg_invItemsConsommable, inline=False)
			if msg_invBox != "":
				msg.add_field(name="Loot Box", value=msg_invBox, inline=False)
			DB.updateComTime(ID, "inv")
			await ctx.channel.send(embed = msg)
		else:
			msg = "Il faut attendre "+str(GF.couldown_c)+" secondes entre chaque commande !"
			await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def market (self, ctx, fct = None):
		"""Permet de voir tout les objets que l'on peux acheter ou vendre !"""
		ID = ctx.author.id
		if DB.spam(ID,GF.couldown_c, "market"):
			if fct == None:
				d_market="Permet de voir tout les objets que l'on peux acheter ou vendre !\n\n"
				d_marketOutils = ""
				d_marketItems = ""
				d_marketItemsMinerai = ""
				d_marketItemsPoisson = ""
				d_marketItemsPlante = ""
				d_marketItemsConsommable = ""
				d_marketBox = ""

				for c in GF.objetOutil:
					d_marketOutils += "<:gem_{0}:{1}>`{0}`: ".format(c.nom,c.idmoji)
					if c.vente != 0:
						d_marketOutils += "Vente **{}** | ".format(c.vente)
					if c.nom == "bank_upgrade":
						d_marketOutils += "Achat **Le plafond du compte épargne** "
					else:
						d_marketOutils += "Achat **{}** ".format(c.achat)
					if c.durabilite != None:
						d_marketOutils += "| Durabilité: **{}** ".format(c.durabilite)
					d_marketOutils += "| Poids **{}**\n".format(c.poids)

				for c in GF.objetItem :
					if c.type == "minerai":
						d_marketItemsMinerai += "<:gem_{0}:{4}>`{0}`: Vente **{1}** | Achat **{2}** | Poids **{3}**\n".format(c.nom,c.vente,c.achat,c.poids,c.idmoji)
					elif c.type == "poisson":
						d_marketItemsPoisson += "<:gem_{0}:{4}>`{0}`: Vente **{1}** | Achat **{2}** | Poids **{3}**\n".format(c.nom,c.vente,c.achat,c.poids,c.idmoji)
					elif c.type == "plante":
						d_marketItemsPlante += "<:gem_{0}:{4}>`{0}`: Vente **{1}** | Achat **{2}** | Poids **{3}**\n".format(c.nom,c.vente,c.achat,c.poids,c.idmoji)
					elif c.type == "consommable":
						d_marketItemsConsommable += ":{0}:`{0}`: Vente **{1}** | Achat **{2}** | Poids **{3}**\n".format(c.nom,c.vente,c.achat,c.poids)
					else:
						d_marketItems += "<:gem_{0}:{4}>`{0}`: Vente **{1}** | Achat **{2}** | Poids **{3}**\n".format(c.nom,c.vente,c.achat,c.poids,c.idmoji)

				for c in GF.objetBox :
					d_marketBox += "<:gem_lootbox:630698430313922580>`{0}`: Achat **{1}** | Gain: `{2} ▶ {3}`:gem: \n".format(c.nom,c.achat,c.min,c.max)

				msg = discord.Embed(title = "Le marché",color= 2461129, description = d_market)
				msg.add_field(name="Outils", value=d_marketOutils, inline=False)
				if d_marketItems != "":
					msg.add_field(name="Items", value=d_marketItems, inline=False)
				msg.add_field(name="Minerais", value=d_marketItemsMinerai, inline=False)
				msg.add_field(name="Poissons", value=d_marketItemsPoisson, inline=False)
				msg.add_field(name="Plantes", value=d_marketItemsPlante, inline=False)
				msg.add_field(name="Consommables", value=d_marketItemsConsommable, inline=False)
				msg.add_field(name="Loot Box", value=d_marketBox, inline=False)
				DB.updateComTime(ID, "market")
				await ctx.channel.send(embed = msg)
				# Message de réussite dans la console
				print("Gems >> {} a afficher le marché".format(ctx.author.name))
			elif fct == "capability" or fct == "capabilities" or fct == "capacité" or fct == "capacités" or fct == "aptitude" or fct == "aptitudes":
				desc = ":tools: En travaux :pencil:"
				msg = discord.Embed(title = "Le marché | Aptitudes",color= 2461129, description = desc)
				DB.updateComTime(ID, "market")
				await ctx.channel.send(embed = msg)
				# Message de réussite dans la console
				print("Gems >> {} a afficher le marché".format(ctx.author.name))
			else:
				msg = "Ce marché n'existe pas"
				await ctx.channel.send(msg)
		else:
			msg = "Il faut attendre "+str(GF.couldown_c)+" secondes entre chaque commande !"
			await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def bourse(self, ctx):
		"""Affiche la bourse de Bastion"""
		ID = ctx.author.id
		if DB.spam(ID,GF.couldown_c, "bourse"):
			time = 120 - GF.globalvar
			timeM = time // 2
			timeS = time % 2
			d_bourse="Bienvenue sur la bourse de Bastion!\nActualisation de la bourse dans **{} minutes".format(timeM)
			if timeS == 1:
				d_bourse += " 30**"
			else:
				d_bourse += "**"
			msg = discord.Embed(title = "La bourse",color= 2461129, description = d_bourse)
			d_bourse=""
			d_bourse+="<:gem_iron:{}>`iron: 9 ▶ 11`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmoji("iron"),GF.get_price("iron"))
			d_bourse+="<:gem_gold:{}>`gold: 45 ▶ 56`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmoji("gold"),GF.get_price("gold"))
			d_bourse+="<:gem_diamond:{}>`diamond: 98 ▶ 120`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmoji("diamond"),GF.get_price("diamond"))
			d_bourse+="<:gem_emerald:{}>`emerald: 148 ▶ 175`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmoji("emerald"),GF.get_price("emerald"))
			d_bourse+="<:gem_ruby:{}>`ruby: 1800 ▶ 2500`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmoji("ruby"),GF.get_price("ruby"))
			d_bourse+="<:gem_tropicalfish:{}>`tropicalfish: 25 ▶ 36`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmoji("tropicalfish"),GF.get_price("tropicalfish"))
			d_bourse+="<:gem_blowfish:{}>`blowfish: 25 ▶ 36`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmoji("blowfish"),GF.get_price("blowfish"))
			d_bourse+="<:gem_octopus:{}>`octopus: 40 ▶ 65`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmoji("octopus"),GF.get_price("octopus"))
			msg.add_field(name="Item", value=d_bourse, inline=False)
			DB.updateComTime(ID, "bourse")
			await ctx.channel.send(embed = msg)
			# Message de réussite dans la console
			print("Gems >> {} a afficher le marché".format(ctx.author.name))
		else:
			msg = "Il faut attendre "+str(GF.couldown_c)+" secondes entre chaque commande !"
			await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def pay (self, ctx, nom, gain):
		"""**[nom] [gain]** | Donner de l'argent à vos amis !"""
		ID = ctx.author.id
		if DB.spam(ID,GF.couldown_c, "pay"):
			try:
				if int(gain) > 0:
					gain = int(gain)
					don = -gain
					ID_recu = DB.nom_ID(nom)
					if int(DB.valueAt(ID, "gems")) >= 0:
						# print(ID_recu)
						DB.addGems(ID_recu, gain)
						DB.addGems(ID,don)
						msg = "<@{0}> donne {1}:gem: à <@{2}> !".format(ID,gain,ID_recu)
						# Message de réussite dans la console
						print("Gems >> {} a donné {} Gems à {}".format(ctx.author.name,gain,ctx.guild.get_member(ID_recu).name))
					else:
						msg = "<@{0}> n'a pas assez pour donner à <@{2}> !".format(ID,gain,ID_recu)

					DB.updateComTime(ID, "pay")
				else :
					msg = "Tu ne peux pas donner une somme négative ! N'importe quoi enfin !"
			except ValueError:
				msg = "La commande est mal formulée"
				pass
		else:
			msg = "Il faut attendre "+str(GF.couldown_c)+" secondes entre chaque commande !"
		await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def forge(self, ctx, item = None, nb = 1):
		"""**[item] [nombre]** | Permet de concevoir des items spécifiques"""
		ID = ctx.author.id
		if DB.spam(ID,GF.couldown_c, "forge"):
			if GF.testInvTaille(ID):
				#-------------------------------------
				# Affichage des recettes disponible
				if item == None:
					msg = GF.recette(ctx)
					await ctx.channel.send(embed = msg)
					# Message de réussite dans la console
					print("Gems >> {} a afficher les recettes".format(ctx.author.name))
					return
				#-------------------------------------
				else:
					for c in GF.objetRecette:
						if item == c.nom:
							nb = int(nb)
							nb1 = nb*c.nb1
							nb2 = nb*c.nb2
							nb3 = nb*c.nb3
							nb4 = nb*c.nb4
							if c.item1 != "" and c.item2 != "" and c.item3 != "" and c.item4 != "":
								if DB.nbElements(ID, "inventory", c.item1) >= nb1 and DB.nbElements(ID, "inventory", c.item2) >= nb2 and DB.nbElements(ID, "inventory", c.item3) >= nb3 and DB.nbElements(ID, "inventory", c.item4) >= nb4:
									DB.add(ID, "inventory", c.nom, nb)
									DB.add(ID, "inventory", c.item1, -1*nb1)
									DB.add(ID, "inventory", c.item2, -1*nb2)
									DB.add(ID, "inventory", c.item3, -1*nb3)
									DB.add(ID, "inventory", c.item4, -1*nb4)
									msg = "Bravo, tu as réussi à forger {0} <:gem_{1}:{2}>`{1}` !".format(nb, c.nom, GF.get_idmoji(c.nom))
									print("Gems >> {0} a forgé {1} {2}".format(ctx.author.name, nb, c.nom))
								else:
									msg = ""
									if DB.nbElements(ID, "inventory", c.item1) < nb1:
										nbmissing = (DB.nbElements(ID, "inventory", c.item1) - nb1)*-1
										msg += "Il te manque {0} <:gem_{1}:{2}>`{1}`\n".format(nbmissing, c.item1, GF.get_idmoji(c.item1))
									if DB.nbElements(ID, "inventory", c.item2) < nb2:
										nbmissing = (DB.nbElements(ID, "inventory", c.item2) - nb2)*-1
										msg += "Il te manque {0} <:gem_{1}:{2}>`{1}`\n".format(nbmissing, c.item2, GF.get_idmoji(c.item2))
									if DB.nbElements(ID, "inventory", c.item3) < nb3:
										nbmissing = (DB.nbElements(ID, "inventory", c.item3) - nb3)*-1
										msg += "Il te manque {0} <:gem_{1}:{2}>`{1}`\n".format(nbmissing, c.item3, GF.get_idmoji(c.item3))
									if DB.nbElements(ID, "inventory", c.item4) < nb4:
										nbmissing = (DB.nbElements(ID, "inventory", c.item4) - nb4)*-1
										msg += "Il te manque {0} <:gem_{1}:{2}>`{1}`\n".format(nbmissing, c.item4, GF.get_idmoji(c.item4))

							elif c.item1 != "" and c.item2 != "" and c.item3 != "":
								if DB.nbElements(ID, "inventory", c.item1) >= nb1 and DB.nbElements(ID, "inventory", c.item2) >= nb2 and DB.nbElements(ID, "inventory", c.item3) >= nb3:
									DB.add(ID, "inventory", c.nom, nb)
									DB.add(ID, "inventory", c.item1, -1*nb1)
									DB.add(ID, "inventory", c.item2, -1*nb2)
									DB.add(ID, "inventory", c.item3, -1*nb3)
									msg = "Bravo, tu as réussi à forger {0} <:gem_{1}:{2}>`{1}` !".format(nb, c.nom, GF.get_idmoji(c.nom))
									print("Gems >> {0} a forgé {1} {2}".format(ctx.author.name, nb, c.nom))
								else:
									msg = ""
									if DB.nbElements(ID, "inventory", c.item1) < nb1:
										nbmissing = (DB.nbElements(ID, "inventory", c.item1) - nb1)*-1
										msg += "Il te manque {0} <:gem_{1}:{2}>`{1}`\n".format(nbmissing, c.item1, GF.get_idmoji(c.item1))
									if DB.nbElements(ID, "inventory", c.item2) < nb2:
										nbmissing = (DB.nbElements(ID, "inventory", c.item2) - nb2)*-1
										msg += "Il te manque {0} <:gem_{1}:{2}>`{1}`\n".format(nbmissing, c.item2, GF.get_idmoji(c.item2))
									if DB.nbElements(ID, "inventory", c.item3) < nb3:
										nbmissing = (DB.nbElements(ID, "inventory", c.item3) - nb3)*-1
										msg += "Il te manque {0} <:gem_{1}:{2}>`{1}`\n".format(nbmissing, c.item3, GF.get_idmoji(c.item3))

							elif c.item1 != "" and c.item2 != "":
								if DB.nbElements(ID, "inventory", c.item1) >= nb1 and DB.nbElements(ID, "inventory", c.item2) >= nb2:
									DB.add(ID, "inventory", c.nom, nb)
									DB.add(ID, "inventory", c.item1, -1*nb1)
									DB.add(ID, "inventory", c.item2, -1*nb2)
									msg = "Bravo, tu as réussi à forger {0} <:gem_{1}:{2}>`{1}` !".format(nb, c.nom, GF.get_idmoji(c.nom))
									print("Gems >> {0} a forgé {1} {2}".format(ctx.author.name, nb, c.nom))
								else:
									msg = ""
									if DB.nbElements(ID, "inventory", c.item1) < nb1:
										nbmissing = (DB.nbElements(ID, "inventory", c.item1) - nb1)*-1
										msg += "Il te manque {0} <:gem_{1}:{2}>`{1}`\n".format(nbmissing, c.item1, GF.get_idmoji(c.item1))
									if DB.nbElements(ID, "inventory", c.item2) < nb2:
										nbmissing = (DB.nbElements(ID, "inventory", c.item2) - nb2)*-1
										msg += "Il te manque {0} <:gem_{1}:{2}>`{1}`\n".format(nbmissing, c.item2, GF.get_idmoji(c.item2))

							elif c.item1 != "":
								if DB.nbElements(ID, "inventory", c.item1) >= nb1:
									DB.add(ID, "inventory", c.nom, nb)
									DB.add(ID, "inventory", c.item1, -1*nb1)
									msg = "Bravo, tu as réussi à forger {0} <:gem_{1}:{2}>`{1}` !".format(nb, c.nom, GF.get_idmoji(c.nom))
									print("Gems >> {0} a forgé {1} {2}".format(ctx.author.name, nb, c.nom))
								else:
									nbmissing = (DB.nbElements(ID, "inventory", c.item1) - nb1)*-1
									msg = "Il te manque {0} <:gem_{1}:{2}>`{1}`".format(nbmissing, c.item1, GF.get_idmoji(c.item1))
							await ctx.channel.send(msg)
							return True
						else:
							msg = "Aucun recette disponible pour forger cette item !"
				DB.updateComTime(ID, "forge")
			else:
				msg = "Ton inventaire est plein"
		else:
			msg = "Il faut attendre "+str(GF.couldown_c)+" secondes entre chaque commande !"
		await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def trophy(self, ctx, nom = None):
		"""**[nom]** | Liste de vos trophées !"""
		ID = ctx.author.id
		if DB.spam(ID,GF.couldown_c, "trophy"):
			if nom != None:
				ID = DB.nom_ID(nom)
				nom = ctx.guild.get_member(ID)
				nom = nom.name
			else:
				nom = ctx.author.name
			d_trophy = ":trophy:Trophées de {}\n\n".format(nom)
			#-------------------------------------
			# Récupération de la liste des trophées de ID
			# et attribution de nouveau trophée si les conditions sont rempli
			trophy = DB.valueAt(ID, "trophy")
			for c in GF.objetTrophy:
				GF.testTrophy(ID, c.nom)

			#-------------------------------------
			# Affichage des trophées possédés par ID
			trophy = DB.valueAt(ID, "trophy")
			for c in GF.objetTrophy:
				for x in trophy:
					if c.nom == str(x):
						if trophy[x] > 0:
							d_trophy += "•**{}**\n".format(c.nom)

			DB.updateComTime(ID, "trophy")
			msg = discord.Embed(title = "Trophées",color= 6824352, description = d_trophy)
			# Message de réussite dans la console
			print("Gems >> {} a affiché les trophées de {}".format(ctx.author.name,nom))
			await ctx.channel.send(embed = msg)
		else:
			msg = "Il faut attendre "+str(GF.couldown_c)+" secondes entre chaque commande !"
			await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def trophylist(self, ctx):
		"""Liste de tout les trophées disponibles !"""
		ID = ctx.author.id
		d_trophy = "Liste des :trophy:Trophées\n\n"
		if DB.spam(ID,GF.couldown_c, "trophylist"):
			#-------------------------------------
			# Affichage des trophées standard
			for c in GF.objetTrophy:
				if c.type != "unique" and c.type != "special":
					d_trophy += "**{}**: {}\n".format(c.nom, c.desc)
			d_trophy += "▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
			#-------------------------------------
			# Affichage des trophées spéciaux
			for c in GF.objetTrophy:
				if c.type != "unique" and c.type == "special":
					d_trophy += "**{}**: {}\n".format(c.nom, c.desc)
			d_trophy += "▬▬▬▬▬▬▬▬▬▬▬▬▬\n"
			#-------------------------------------
			# Affichage des trophées uniques
			for c in GF.objetTrophy:
				if c.type == "unique" and c.type != "special":
					d_trophy += "**{}**: {}\n".format(c.nom, c.desc)

			DB.updateComTime(ID, "trophylist")
			msg = discord.Embed(title = "Trophées",color= 6824352, description = d_trophy)
			# Message de réussite dans la console
			print("Gems >> {} a affiché la liste des trophées".format(ctx.author.name))
			await ctx.channel.send(embed = msg)
		else:
			msg = "Il faut attendre "+str(GF.couldown_c)+" secondes entre chaque commande !"
			await ctx.channel.send(msg)



def setup(bot):
	bot.add_cog(GemsBase(bot))
	open("help/cogs.txt","a").write("GemsBase\n")
