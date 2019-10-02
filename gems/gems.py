import discord
import random as r
import time as t
import datetime as dt
from DB import DB
from gems import gemsFonctions as GF
from core import welcome as wel
from discord.ext import commands
from discord.ext.commands import bot
from discord.utils import get
from operator import itemgetter

class GemsBase(commands.Cog):

	def __init__(self,ctx):
		return(None)



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
							GF.addDurabilité(ID, item, -1)
						# Message de réussite dans la console
						print("Gems >> {} a vendu {} {}".format(ctx.author.name,nb,item))
						break

				DB.add(ID, "inventory", item, -nb)
				if test:
					msg = "Cette objet n'existe pas"
			else:
				#print("Pas assez d'élement")
				msg = "Tu n'as pas assez de `{0}`. Il vous en reste : {1}".format(str(item),str(DB.nbElements(ID, "inventory", item)))

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
			inv = DB.valueAt(ID, "inventory")
			tailletot = 0
			Titre = True
			for c in GF.objetOutil:
				if Titre:
					msg_inv += "**Outils**\n"
					Titre = False
				for x in inv:
					if c.nom == str(x):
						if inv[x] > 0:
							msg_inv = msg_inv+"<:gem_{0}:{2}>`{0}`: `x{1}` | Durabilité: `{3}/{4}`\n".format(str(x), str(inv[x]), c.idmoji, GF.get_durabilite(ID, c.nom), c.durabilite)
							tailletot += c.poids*int(inv[x])
			Titre = True
			for c in GF.objetItem:
				if Titre:
					msg_inv += "\n**Items**\n"
					Titre = False
				for x in inv:
					if c.nom == str(x):
						if inv[x] > 0:
							if c.type != "consommable":
								msg_inv = msg_inv+"<:gem_{0}:{2}>`{0}`: `x{1}`\n".format(str(x), str(inv[x]), c.idmoji)
							else:
								msg_inv = msg_inv+":{0}:`{0}`: `x{1}`\n".format(str(x), str(inv[x]))
							tailletot += c.poids*int(inv[x])

			msg_inv += "\nTaille: `{}/{}`".format(int(tailletot),GF.invMax)
			msg_titre = "Inventaire de {}\n\n".format(nom)
			msg = discord.Embed(title = msg_titre,color= 6466585, description = msg_inv)
			DB.updateComTime(ID, "inv")
			await ctx.channel.send(embed = msg)
		else:
			msg = "Il faut attendre "+str(GF.couldown_c)+" secondes entre chaque commande !"
			await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def market (self, ctx):
		"""Permet de voir tout les objets que l'on peux acheter ou vendre !"""
		ID = ctx.author.id
		if DB.spam(ID,GF.couldown_c, "market"):
			d_market="Permet de voir tout les objets que l'on peux acheter ou vendre !\n\n"
			Titre = True
			for c in GF.objetOutil:
				if Titre:
					d_market += "**Outils**\n"
					Titre = False
				d_market += "<:gem_{0}:{3}>`{0}`: Vente **{1}** | Achat **{2}** ".format(c.nom,c.vente,c.achat,c.idmoji)
				if c.durabilite != None:
					d_market += "| Durabilité: **{}** ".format(c.durabilite)
				d_market += "| Poids **{}**\n".format(c.poids)
			Titre = True
			for c in GF.objetItem :
				if Titre:
					d_market += "\n**Items**\n"
					Titre = False
				if c.type != "consommable":
					d_market += "<:gem_{0}:{4}>`{0}`: Vente **{1}** | Achat **{2}** | Poids **{3}**\n".format(c.nom,c.vente,c.achat,c.poids,c.idmoji)
				else:
					d_market += ":{0}:`{0}`: Vente **{1}** | Achat **{2}** | Poids **{3}**\n".format(c.nom,c.vente,c.achat,c.poids)

			msg = discord.Embed(title = "Le marché",color= 2461129, description = d_market)
			DB.updateComTime(ID, "market")
			await ctx.channel.send(embed = msg)
			# Message de réussite dans la console
			print("Gems >> {} a afficher le marché".format(ctx.author.name))
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
			d_bourse+="<:gem_iron:{}>`iron: 9 ▶ 11`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmogi("iron"),GF.get_price("iron"))
			d_bourse+="<:gem_gold:{}>`gold: 45 ▶ 56`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmogi("gold"),GF.get_price("gold"))
			d_bourse+="<:gem_diamond:{}>`diamond: 98 ▶ 120`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmogi("diamond"),GF.get_price("diamond"))
			d_bourse+="<:gem_emerald:{}>`emerald: 148 ▶ 175`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmogi("emerald"),GF.get_price("emerald"))
			d_bourse+="<:gem_ruby:{}>`ruby: 1800 ▶ 2500`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmogi("ruby"),GF.get_price("ruby"))
			d_bourse+="<:gem_tropicalfish:{}>`tropicalfish: 25 ▶ 36`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmogi("tropicalfish"),GF.get_price("tropicalfish"))
			d_bourse+="<:gem_blowfish:{}>`blowfish: 25 ▶ 36`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmogi("blowfish"),GF.get_price("blowfish"))
			d_bourse+="<:gem_octopus:{}>`octopus: 40 ▶ 65`:gem:` | Valeur actuel: {}`:gem:\n".format(GF.get_idmogi("octopus"),GF.get_price("octopus"))
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
				# Forgeage des items (pour l'instant uniquement la pioche en fer)
				elif item == "iron_pickaxe":
					nb = int(nb)
					nbIron = 4*nb
					nbPickaxe = 1*nb
					if DB.nbElements(ID, "inventory", "iron") >= nbIron and DB.nbElements(ID, "inventory", "pickaxe") >= nbPickaxe:
						DB.add(ID, "inventory", "iron_pickaxe", nb)
						DB.add(ID, "inventory", "pickaxe", -nbPickaxe)
						DB.add(ID, "inventory", "iron", -nbIron)
						msg = "Bravo, tu as réussi à forger {0} <:gem_iron_pickaxe:608748194775433256>`iron_pickaxe` !".format(nb)
						# Message de réussite dans la console
						print("Gems >> {} a forgé une pioche en fer".format(ctx.author.name))
					elif DB.nbElements(ID, "inventory", "iron") < nbIron and DB.nbElements(ID, "inventory", "pickaxe") < nbPickaxe:
						msg = "tu n'as pas assez de <:gem_iron:{1}>`lingots de fer` et de <:gem_pickaxe:{2}>`pickaxe` pour forger {0} <:gem_iron_pickaxe:{3}>`iron_pickaxe` !".format(nb,GF.get_idmogi("iron"), GF.get_idmogi("pickaxe"), GF.get_idmogi("iron_pickaxe"))
					elif DB.nbElements(ID, "inventory", "iron") < nbIron:
						nbmissing = (DB.nbElements(ID, "inventory", "iron") - nbIron)*-1
						msg = "Il te manque {0} <:gem_iron:{2}>`lingots de fer` pour forger {1} <:gem_iron_pickaxe:{3}>`iron_pickaxe` !".format(nbmissing, nb,GF.get_idmogi("iron"), GF.get_idmogi("iron_pickaxe"))
					else:
						nbmissing = (DB.nbElements(ID, "inventory", "pickaxe") - nbPickaxe)*-1
						msg = "Il te manque {0} <:gem_pickaxe:{2}>`pickaxe` pour forger {1} <:gem_iron_pickaxe:{3}>`iron_pickaxe` !".format(nbmissing, nb, GF.get_idmogi("pickaxe"), GF.get_idmogi("iron_pickaxe"))
				else:
					msg = "Impossible d'exécuter de forger cet item !"

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

#===============================================================

class Gems(commands.Cog):

	def __init__(self,ctx):
		return(None)



	@commands.command(pass_context=True)
	async def daily(self, ctx):
		"""Récupère ta récompense journalière!"""
		#=======================================================================
		# Initialisation des variables générales de la fonction
		#=======================================================================
		ID = ctx.author.id
		DailyTime = DB.daily_data(ID, "dailytime")
		DailyMult = DB.daily_data(ID, "dailymult")
		jour = dt.date.today()
		#=======================================================================
		# Détermination du daily
		#=======================================================================
		if DailyTime == str(jour - dt.timedelta(days=1)):
			DB.updateDaily(ID, "dailytime", jour)
			DB.updateDaily(ID, "dailymult", DailyMult + 1)
			bonus = 125
			gain = 100 + bonus*DailyMult
			DB.addGems(ID, gain)
			msg = "Récompense journalière! Tu as gagné 100:gem:"
			msg += "\nNouvelle série: `{}`, Bonus: {}:gem:".format(DailyMult, bonus*DailyMult)

		elif DailyTime == str(jour):
			msg = "Tu as déja reçu ta récompense journalière aujourd'hui. Reviens demain pour gagner plus de :gem:"
		else:
			DB.updateDaily(ID, "dailytime", jour)
			DB.updateDaily(ID, "dailymult", 1)
			msg = "Récompense journalière! Tu as gagné 100 :gem:"
		await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def bank(self, ctx, ARG = None, ARG2 = None):
		"""
		Compte épargne
		"""
		#=======================================================================
		# Initialistation des variables générales de la fonction
		#=======================================================================
		ID = ctx.author.id
		if ARG != None:
			mARG = ARG.lower()
		else:
			mARG = "bal"
		msg = ""
		for c in GF.objetOutil:
			if c.type == "bank":
				Taille = c.poids
		msg = ""
		#=======================================================================
		# Affiche le menu principal de la banque
		# !bank bal <nom d'un joueur> permet de visualiser l'état de la banque de ce joueur
		#=======================================================================
		if mARG == "bal":
			if DB.spam(ID,GF.couldown_c, "bank_bal"):
				if ARG2 != None:
					ID = DB.nom_ID(ARG2)
					nom = ctx.guild.get_member(ID)
					ARG2 = nom.name
					title = "Compte épargne de {}".format(ARG2)
				else:
					title = "Compte épargne de {}".format(ctx.author.name)
				solde = DB.nbElements(ID, "banque", "solde")
				soldeMax = DB.nbElements(ID, "banque", "soldeMax")
				if soldeMax == 0:
					soldeMax = Taille
				msg = discord.Embed(title = title,color= 13752280, description = "")
				desc = "{} / {} :gem:\n".format(solde, soldeMax)
				msg.add_field(name="Balance", value=desc, inline=False)

				desc = "bank **bal** *[name]* | Permet de connaitre la balance d'un utilisateur"
				desc += "\nbank **add** *[+/- nombre]* | Permet d'ajouter ou d'enlever des :gem: de son compte épargne"
				desc += "\nbank **saving** | Permet de calculer son épargne (utilisable toute les 4h)"
				desc += "\n\nLe prix de la <:gem_{0}:{1}>`{0}` dépend du plafond du compte".format("bank_upgrade", GF.get_idmogi("bank_upgrade"))

				msg.add_field(name="Commandes", value=desc, inline=False)
				await ctx.channel.send(embed = msg)
				DB.updateComTime(ID, "bank_bal")
				return
			else:
				msg = "Il faut attendre "+str(GF.couldown_c)+" secondes entre chaque commande !"
			await ctx.channel.send(msg)
			return
		#=======================================================================
		# Ajoute ou enlève des Gems sur le compte épargne
		# un nombre positif ajoute des Gems
		# un nombre négatif enlève des Gems
		#=======================================================================
		elif mARG == "add":
			if DB.spam(ID,GF.couldown_c, "bank_add"):
				if ARG2 != None:
					ARG2 = int(ARG2)
					gems = DB.valueAt(ID, "gems")
					solde = DB.nbElements(ID, "banque", "solde")
					soldeMax = DB.nbElements(ID, "banque", "soldeMax")
					if soldeMax == 0:
						soldeMax = Taille

					if ARG2 <= gems:
						soldeNew = solde + ARG2
						if soldeNew > soldeMax:
							ARG2 = ARG2 - (soldeNew - soldeMax)
							msg = "Plafond de {} :gem: du compte épargne atteint\n".format(soldeMax)
						elif soldeNew < 0:
							msg = "Le solde de ton compte épargne ne peux être négatif.\nSolde du compte: {} :gem:".format(solde)
							await ctx.channel.send(msg)
							return
						nbgm = -1*ARG2
						DB.addGems(ID, nbgm)
						DB.add(ID, "banque", "solde", ARG2)
						msg += "Ton compte épargne a été crédité de {} :gem:".format(ARG2)
						msg += "\nNouveau solde: {} :gem:".format(DB.nbElements(ID, "banque", "solde"))
						DB.updateComTime(ID, "bank_add")
					else:
						msg = "Tu n'as pas assez de :gem:`gems` pour épargner cette somme"
				else:
					msg = "Il manque le nombre de :gem: à ajouter sur votre compte épargne"
			else:
				msg = "Il faut attendre "+str(GF.couldown_c)+" secondes entre chaque commande !"
			await ctx.channel.send(msg)
			return
		#=======================================================================
		# Fonction d'épargne
		# L'intéret est de 20% avec un bonus de 1% pour chanque bank_upgrade possédée
		#=======================================================================
		elif mARG == "saving":
			if DB.spam(ID,GF.couldown_xxxl, "bank_saving"):
				if ARG2 != None:
					ID = DB.nom_ID(ARG2)
				else:
					solde = DB.nbElements(ID, "banque", "solde")
					soldeMax = DB.nbElements(ID, "banque", "soldeMax")
					if soldeMax == 0:
						soldeMax = Taille
					soldeMult = soldeMax/Taille
					pourcentage = 0.200 + soldeMult*0.002
					soldeAdd = pourcentage*solde
					soldeTaxe = GF.taxe(soldeAdd, 0.1)
					soldeAdd = soldeTaxe[1]
					DB.add(ID, "banque", "solde", int(soldeAdd))
					msg = "Tu as épargné {} :gem:\n".format(int(soldeAdd))
					soldeNew = solde + soldeAdd
					if soldeNew > soldeMax:
						soldeMove = soldeNew - soldeMax
						nbgm = -1 * soldeMove
						DB.addGems(ID, int(soldeMove))
						DB.add(ID, "banque", "solde", int(nbgm))
						msg += "Plafond de {} :gem: du compte épargne atteint\nTon épargne a été tranférée sur ton compte principal\n\n".format(soldeMax)

					msg += "Nouveau solde: {} :gem:".format(DB.nbElements(ID, "banque", "solde"))

					if ctx.guild.id != wel.idBASTION:
						DB.addGems(wel.idGetGems,int(soldeTaxe[0]))
					elif ctx.guild.id == wel.idBASTION:
						DB.addGems(wel.idBaBot,int(soldeTaxe[0]))

				DB.updateComTime(ID, "bank_saving")
			else:
				ComTime = DB.valueAt(ID, "com_time")
				if "bank_saving" in ComTime:
					time = ComTime["bank_saving"]
				time = time - (t.time()-GF.couldown_xxxl)
				timeH = int(time / 60 / 60)
				time = time - timeH * 3600
				timeM = int(time / 60)
				timeS = int(time - timeM * 60)
				msg = "Il te faut attendre `{}h {}m {}s` avant d'épargner à nouveau !".format(timeH,timeM,timeS)
			await ctx.channel.send(msg)
			return




	@commands.command(pass_context=True)
	async def crime(self, ctx):
		"""Commets un crime et gagne des :gem: Attention au DiscordCop!"""
		ID = ctx.author.id
		if DB.spam(ID,GF.couldown_l, "crime"):
			# si 10 sec c'est écoulé depuis alors on peut en  faire une nouvelle
			if r.randint(0,9) == 0:
				DB.add(ID, "StatGems", "DiscordCop Arrestation", 1)
				if int(DB.addGems(ID, -10)) >= 0:
					msg = "Vous avez été attrapés par un DiscordCop vous avez donc payé une amende de 10 :gem:"
				else:
					msg = "Vous avez été attrapés par un DiscordCop mais vous avez trop peu de :gem: pour payer une amende"
			else :
				gain = r.randint(2,8)
				msg = GF.message_crime[r.randint(0,3)]+" "+str(gain)+":gem:"
				DB.addGems(ID, gain)

			DB.updateComTime(ID, "crime")
		else:
			msg = "Il faut attendre "+str(GF.couldown_l)+" secondes entre chaque commande !"
		await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def gamble(self, ctx,valeur):
		"""**[valeur]** | Avez vous l'ame d'un parieur ?"""
		valeur = int(valeur)
		ID = ctx.author.id
		gems = DB.valueAt(ID, "gems")
		if valeur < 0:
			msg = "Je vous met un amende de 100 :gem: pour avoir essayé de tricher !"
			DB.add(ID, "StatGems", "DiscordCop Amende", 1)
			if gems > 100 :
				DB.addGems(ID, -100)
			else :
				DB.addGems(ID, 0-DB.valueAt(ID, "gems"))
			await ctx.channel.send(msg)
			return
		elif valeur > 0 and gems >= valeur:
			if DB.spam(ID,GF.couldown_xl, "gamble"):
				if r.randint(0,3) == 0:
					gain = valeur*3
					# l'espérence est de 0 sur la gamble
					msg = GF.message_gamble[r.randint(0,4)]+" "+str(gain)+":gem:"
					DB.add(ID, "StatGems", "Gamble Win", 1)
					for x in GF.objetTrophy:
						if x.nom == "Gamble Jackpot":
							jackpot = x.mingem
					if gain >= jackpot:
						DB.add(ID, "trophy", "Gamble Jackpot", 1)
						msg += "Félicitation! Tu as l'ame d'un parieur, nous t'offrons le prix :trophy:`Gamble Jackpot`."
					DB.addGems(ID, gain)
				else:
					val = 0-valeur
					DB.addGems(ID,val)
					msg = "Dommage tu as perdu "+str(valeur)+":gem:"

				DB.updateComTime(ID, "gamble")
			else:
				msg = "Il faut attendre "+str(GF.couldown_xl)+" secondes entre chaque commande !"
		elif gems < valeur:
			msg = "Tu n'as pas assez de :gem:`gems` en banque"
		else:
			msg = "La valeur rentré est incorrect"
		await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def mine(self, ctx):
		"""Minez compagnons !!"""
		ID = ctx.author.id
		if DB.spam(ID,GF.couldown_l, "mine"):
			if GF.testInvTaille(ID):
				#print(DB.nbElements(ID, "inventory", "pickaxe"))
				nbrand = r.randint(0,99)
				#----------------- Pioche en fer -----------------
				if DB.nbElements(ID, "inventory", "iron_pickaxe") >= 1:
					if GF.get_durabilite(ID, "iron_pickaxe") == 0:
						GF.addDurabilité(ID, "iron_pickaxe", -1)
						DB.add(ID, "inventory","iron_pickaxe", -1)
						if DB.nbElements(ID, "inventory", "iron_pickaxe") > 0:
							for c in GF.objetOutil:
								if c.nom == "iron_pickaxe":
									GF.addDurabilité(ID, c.nom, c.durabilite)
						msg = "Pas de chance tu as cassé ta <:gem_iron_pickaxe:{}>`pioche en fer` !".format(GF.get_idmogi("iron_pickaxe"))
					else :
						if GF.get_durabilite(ID,"iron_pickaxe") == None or GF.get_durabilite(ID,"iron_pickaxe") < 0:
							for c in GF.objetOutil:
								if c.nom == "iron_pickaxe":
									GF.addDurabilité(ID, c.nom, c.durabilite)
						GF.addDurabilité(ID, "iron_pickaxe", -1)
						if nbrand < 5:
							DB.add(ID, "inventory", "emerald", 1)
							msg = "Tu as obtenu 1 <:gem_emerald:{}>`émeraude`".format(GF.get_idmogi("emerald"))
						elif nbrand > 5 and nbrand < 15:
							DB.add(ID, "inventory", "diamond", 1)
							msg = "Tu as obtenu 1 <:gem_diamond:{}>`diamant brut`".format(GF.get_idmogi("diamond"))
							nbcobble = r.randint(0,5)
							if nbcobble != 0 :
								DB.add(ID, "inventory", "cobblestone", nbcobble)
								msg += "\nTu as obtenu {} bloc de <:gem_cobblestone:{}>`cobblestone`".format(nbcobble,GF.get_idmogi("cobblestone"))
						elif nbrand > 15 and nbrand < 30:
							DB.add(ID, "inventory", "gold", 1)
							msg = "Tu as obtenu 1 <:gem_gold:{}>`lingot d'or`".format(GF.get_idmogi("gold"))
							nbcobble = r.randint(0,5)
							if nbcobble != 0 :
								DB.add(ID, "inventory", "cobblestone", nbcobble)
								msg += "\nTu as obtenu {} bloc de <:gem_cobblestone:{}>`cobblestone`".format(nbcobble,GF.get_idmogi("cobblestone"))
						elif nbrand > 30 and nbrand < 60:
							DB.add(ID, "inventory", "iron", 1)
							msg = "Tu as obtenu 1 <:gem_iron:{}>`lingot de fer`".format(GF.get_idmogi("iron"))
							nbcobble = r.randint(0,5)
							if nbcobble != 0 :
								DB.add(ID, "inventory", "cobblestone", nbcobble)
								msg += "\nTu as obtenu {} bloc de <:gem_cobblestone:{}>`cobblestone`".format(nbcobble,GF.get_idmogi("cobblestone"))
						elif nbrand >= 95:
							if r.randint(0,10) == 10:
								DB.add(ID, "inventory", "ruby", 1)
								DB.add(ID, "StatGems", "Mineur de Merveilles", 1)
								DB.add(ID, "trophy", "Mineur de Merveilles", 1)
								msg = "En trouvant ce <:gem_ruby:{}>`ruby` tu deviens un Mineur de Merveilles".format(GF.get_idmogi("ruby"))
							else:
								msg = "La pioche n'est pas très efficace pour miner la `dirt`"
						else:
							nbcobble = r.randint(1,10)
							DB.add(ID, "inventory", "cobblestone", nbcobble)
							if nbcobble == 1 :
								msg = "Tu as obtenu 1 bloc de <:gem_cobblestone:{}>`cobblestone`".format(GF.get_idmogi("cobblestone"))
							else :
								msg = "Tu as obtenu {} blocs de <:gem_cobblestone:{}>`cobblestone`".format(nbcobble, GF.get_idmogi("cobblestone"))

				#----------------- Pioche normal -----------------
				elif DB.nbElements(ID, "inventory", "pickaxe") >= 1:
					if GF.get_durabilite(ID, "pickaxe") == 0:
						GF.addDurabilité(ID, "pickaxe", -1)
						DB.add(ID, "inventory", "pickaxe", -1)
						if DB.nbElements(ID, "inventory","pickaxe") > 0:
							for c in GF.objetOutil:
								if c.nom == "pickaxe":
									GF.addDurabilité(ID, c.nom, c.durabilite)
						msg = "Pas de chance tu as cassé ta <:gem_pickaxe:{}>`pioche` !".format(GF.get_idmogi("pickaxe"))
					else :
						if GF.get_durabilite(ID,"pickaxe") == None or GF.get_durabilite(ID,"pickaxe") < 0:
							for c in GF.objetOutil:
								if c.nom == "pickaxe":
									GF.addDurabilité(ID, c.nom, c.durabilite)
						GF.addDurabilité(ID, "pickaxe", -1)
						if nbrand < 20:
							DB.add(ID, "inventory", "iron", 1)
							msg = "Tu as obtenu 1 <:gem_iron:{}>`lingot de fer`".format(GF.get_idmogi("iron"))
							nbcobble = r.randint(0,5)
							if nbcobble != 0 :
								DB.add(ID, "inventory", "cobblestone", nbcobble)
								msg += "\nTu as obtenu {} bloc de <:gem_cobblestone:{}>`cobblestone`".format(nbcobble,GF.get_idmogi("cobblestone"))
						else:
							nbcobble = r.randint(1,10)
							DB.add(ID, "inventory", "cobblestone", nbcobble)
							if nbcobble == 1 :
								msg = "Tu as obtenu 1 bloc de <:gem_cobblestone:{}>`cobblestone`".format(GF.get_idmogi("cobblestone"))
							else :
								msg = "Tu as obtenu {} blocs de <:gem_cobblestone:{}>`cobblestone`".format(nbcobble, GF.get_idmogi("cobblestone"))
				else:
					msg = "Il faut acheter ou forger une pioche pour miner!"

				DB.updateComTime(ID, "mine")
			else:
				msg = "Ton inventaire est plein"
		else:
			msg = "Il faut attendre "+str(GF.couldown_l)+" secondes entre chaque commande !"
		await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def fish(self, ctx):
		"""Péchons compagnons !!"""
		ID = ctx.author.id
		if DB.spam(ID,GF.couldown_l, "fish"):
			if GF.testInvTaille(ID):
				nbrand = r.randint(0,99)
				#print(DB.nbElements(ID, "inventory", "fishingrod"))
				if DB.nbElements(ID, "inventory", "fishingrod") >= 1:
					if GF.get_durabilite(ID, "fishingrod") == 0:
						GF.addDurabilité(ID, "fishingrod", -1)
						DB.add(ID, "inventory", "fishingrod", -1)
						if DB.nbElements(ID, "inventory", "fishingrod") > 0:
							for c in GF.objetOutil:
								if c.nom == "fishingrod":
									GF.addDurabilité(ID, c.nom, c.durabilite)
						msg = "Pas de chance tu as cassé ta <:gem_fishingrod:{}>`canne à peche` !".format(GF.get_idmogi("fishingrod"))
					else :
						if GF.get_durabilite(ID,"fishingrod") == None or GF.get_durabilite(ID,"fishingrod") < 0:
							for c in GF.objetOutil:
								if c.nom == "fishingrod":
									GF.addDurabilité(ID, c.nom, c.durabilite)
						GF.addDurabilité(ID, "fishingrod", -1)

						if nbrand < 15:
							DB.add(ID, "inventory", "tropicalfish", 1)
							msg = "Tu as obtenu 1 <:gem_tropicalfish:{}>`tropicalfish`".format(GF.get_idmogi("tropicalfish"))
							nbfish = r.randint(0,3)
							if nbfish != 0:
								DB.add(ID, "inventory", "fish", nbfish)
								msg += "\nTu as obtenu {} <:gem_fish:{}>`fish`".format(nbfish, GF.get_idmogi("fish"))

						elif nbrand >= 15 and nbrand < 30:
							DB.add(ID, "inventory", "blowfish", 1)
							msg = "Tu as obtenu 1 <:gem_blowfish:{}>`blowfish`".format(GF.get_idmogi("blowfish"))
							nbfish = r.randint(0,3)
							if nbfish != 0:
								DB.add(ID, "inventory", "fish", nbfish)
								msg += "\nTu as obtenu {} <:gem_fish:{}>`fish`".format(nbfish, GF.get_idmogi("fish"))

						elif nbrand >= 30 and nbrand < 40:
							DB.add(ID, "inventory", "octopus", 1)
							msg = "Tu as obtenu 1 <:gem_octopus:{}>`octopus`".format(GF.get_idmogi("octopus"))

						elif nbrand >= 40 and nbrand < 95:
							nbfish = r.randint(1,7)
							DB.add(ID, "inventory", "fish", nbfish)
							msg = "Tu as obtenu {} <:gem_fish:{}>`fish`".format(nbfish, GF.get_idmogi("fish"))
						else:
							msg = "Pas de poisson pour toi aujourd'hui :cry: "
				else:
					msg = "Il te faut une <:gem_fishingrod:{}>`canne à pèche` pour pécher, tu en trouvera une au marché !".format(GF.get_idmogi("fishingrod"))

				DB.updateComTime(ID, "fish")
			else:
				msg = "Ton inventaire est plein"
		else:
			msg = "Il faut attendre "+str(GF.couldown_l)+" secondes entre chaque commande !"
		await ctx.channel.send(msg)



	@commands.command(pass_context=True)
	async def slots(self, ctx, imise = None):
		"""**[mise]** | La machine à sous, la mise minimum est de 10 :gem:"""
		ID = ctx.author.id

		if imise != None:
			if int(imise) < 0:
				msg = "Je vous met un amende de 100 :gem: pour avoir essayé de tricher !"
				DB.add(ID, "StatGems", "DiscordCop Amende", 1)
				if DB.valueAt(ID, "gems") > 100 :
					DB.addGems(ID, -100)
				else :
					DB.addGems(ID, 0-DB.valueAt(ID, "gems"))
				await ctx.channel.send(msg)
				return
			elif int(imise) < 10:
				mise = 10
			elif int(imise) > 100:
				mise = 100
			else:
				mise = int(imise)
		else:
			mise = 10

		if DB.spam(ID,GF.couldown_xl, "slots"):
			tab = []
			result = []
			msg = "Votre mise: {} :gem:\n\n".format(mise)
			val = 0-mise
			for i in range(0,9): #Creation de la machine à sous
				if i == 3:
					msg+="\n"
				elif i == 6:
					msg+=" :arrow_backward:\n"
				tab.append(r.randint(0,344))
				if tab[i] < 15 :
					result.append("zero")
				elif tab[i] >= 15 and tab[i] < 30:
					result.append("one")
				elif tab[i] >=  30 and tab[i] < 45:
					result.append("two")
				elif tab[i] >=  45 and tab[i] < 60:
					result.append("three")
				elif tab[i] >=  60 and tab[i] < 75:
					result.append("four")
				elif tab[i] >=  75 and tab[i] < 90:
					result.append("five")
				elif tab[i] >=  90 and tab[i] < 105:
					result.append("six")
				elif tab[i] >=  105 and tab[i] < 120:
					result.append("seven")
				elif tab[i] >=  120 and tab[i] < 135:
					result.append("eight")
				elif tab[i] >=  135 and tab[i] < 150:
					result.append("nine")
				elif tab[i] >=  150 and tab[i] < 170:
					result.append("gem")
				elif tab[i] >=  170 and tab[i] < 190:
					result.append("ticket")
				elif tab[i] >=  190 and tab[i] < 210:
					result.append("boom")
				elif tab[i] >=  210 and tab[i] < 220:
					result.append("apple")
				elif tab[i] >=  220 and tab[i] < 230:
					result.append("green_apple")
				elif tab[i] >=  230 and tab[i] < 240:
					result.append("cherries")
				elif tab[i] >=  240 and tab[i] < 250:
					result.append("tangerine")
				elif tab[i] >=  250 and tab[i] < 260:
					result.append("banana")
				elif tab[i] >=  260 and tab[i] < 280:
					result.append("grapes")
				elif tab[i] >=  280 and tab[i] < 310:
					result.append("cookie")
				elif tab[i] >=  310 and tab[i] < 340:
					result.append("beer")
				elif tab[i] >= 340 and tab[i] < 343:
					result.append("backpack")
				elif tab[i] >= 343:
					result.append("ruby")
				if tab[i] < 340:
					msg+=":{}:".format(result[i])
				else:
					msg+="<:gem_{}:{}>".format(result[i], GF.get_idmogi(result[i]))
			msg += "\n"

			#===================================================================
			# Attribution des prix
			#===================================================================
			#Ruby (hyper rare)
			if result[3] == "ruby" or result[4] == "ruby" or result[5] == "ruby":
				DB.add(ID, "inventory", "ruby", 1)
				DB.add(ID, "StatGems", "Mineur de Merveilles", 1)
				DB.add(ID, "trophy", "Mineur de Merveilles", 1)
				gain = 42
				msg += "\nEn trouvant ce <:gem_ruby:{}>`ruby` tu deviens un Mineur de Merveilles".format(GF.get_idmogi("ruby"))
			#===================================================================
			#Super gain, 3 chiffres identique
			elif result[3] == "seven" and result[4] == "seven" and result[5] == "seven":
				gain = 1000
				DB.add(ID, "StatGems", "Super Jackpot :seven::seven::seven:", 1)
				DB.add(ID, "trophy", "Super Jackpot :seven::seven::seven:", 1)
				botplayer = discord.utils.get(ctx.guild.roles, id=532943340392677436)
				msg += "\n{} Bravo <@{}>! Le Super Jackpot :seven::seven::seven: est tombé :tada: ".format(botplayer.mention,ID)
			elif result[3] == "one" and result[4] == "one" and result[5] == "one":
				gain = 100
			elif result[3] == "two" and result[4] == "two" and result[5] == "two":
				gain = 150
			elif result[3] == "three" and result[4] == "three" and result[5] == "three":
				gain = 200
			elif result[3] == "four" and result[4] == "four" and result[5] == "four":
				gain = 250
			elif result[3] == "five" and result[4] == "five" and result[5] == "five":
				gain = 300
			elif result[3] == "six" and result[4] == "six" and result[5] == "six":
				gain = 350
			elif result[3] == "eight" and result[4] == "eight" and result[5] == "eight":
				gain = 400
			elif result[3] == "nine" and result[4] == "nine" and result[5] == "nine":
				gain = 450
			elif result[3] == "zero" and result[4] == "zero" and result[5] == "zero":
				gain = 500
			#===================================================================
			#Beer
			elif (result[3] == "beer" and result[4] == "beer") or (result[4] == "beer" and result[5] == "beer") or (result[3] == "beer" and result[5] == "beer"):
				DB.add(ID, "StatGems", "La Squelatitude", 1)
				DB.add(ID, "trophy", "La Squelatitude", 1)
				gain = 4
				msg += "\n<@{}> paye sa tournée :beer:".format(ID)
			#===================================================================
			#Explosion de la machine
			elif result[3] == "boom" and result[4] == "boom" and result[5] == "boom":
				gain = -50
			elif (result[3] == "boom" and result[4] == "boom") or (result[4] == "boom" and result[5] == "boom") or (result[3] == "boom" and result[5] == "boom"):
				gain = -10
			elif result[3] == "boom" or result[4] == "boom" or result[5] == "boom":
				gain = -2
			#===================================================================
			#Gain de gem
			elif result[3] == "gem" and result[4] == "gem" and result[5] == "gem":
				gain = 50
			elif (result[3] == "gem" and result[4] == "gem") or (result[4] == "gem" and result[5] == "gem") or (result[3] == "gem" and result[5] == "gem"):
				gain = 15
			elif result[3] == "gem" or result[4] == "gem" or result[5] == "gem":
				gain = 5
			#===================================================================
			#Tichet gratuit
			elif result[3] == "ticket" and result[4] == "ticket" and result[5] == "ticket":
				gain = 10
			elif (result[3] == "ticket" and result[4] == "ticket") or (result[4] == "ticket" and result[5] == "ticket") or (result[3] == "ticket" and result[5] == "ticket"):
				gain = 5
			elif result[3] == "ticket" or result[4] == "ticket" or result[5] == "ticket":
				gain = 2
			else:
				gain = 0
			#===================================================================
			#Cookie
			nbCookie = 0
			if result[3] == "cookie" and result[4] == "cookie" and result[5] == "cookie":
				nbCookie = 3
			elif (result[3] == "cookie" and result[4] == "cookie") or (result[4] == "cookie" and result[5] == "cookie") or (result[3] == "cookie" and result[5] == "cookie"):
				nbCookie = 2
			elif result[3] == "cookie" or result[4] == "cookie" or result[5] == "cookie":
				nbCookie = 1
			if nbCookie != 0:
				if GF.testInvTaille(ID):
					msg += "\nTu a trouvé {} :cookie:`cookie`".format(nbCookie)
					DB.add(ID, "inventory", "cookie", nbCookie)
				else:
					msg += "\nTon inventaire est plein"
			#===================================================================
			#grappe
			nbGrapes = 0
			if result[3] == "grapes" and result[4] == "grapes" and result[5] == "grapes":
				nbGrapes = 3
			elif (result[3] == "grapes" and result[4] == "grapes") or (result[4] == "grapes" and result[5] == "grapes") or (result[3] == "grapes" and result[5] == "grapes"):
				nbGrapes = 2
			elif result[3] == "grapes" or result[4] == "grapes" or result[5] == "grapes":
				nbGrapes = 1
			if nbGrapes != 0:
				if GF.testInvTaille(ID):
					msg += "\nTu a trouvé {} :grapes:`grapes`".format(nbGrapes)
					DB.add(ID, "inventory", "grapes", nbGrapes)
				else:
					msg += "\nTon inventaire est plein"
			#===================================================================
			#Backpack (hyper rare)
			if result[3] == "backpack" or result[4] == "backpack" or result[5] == "backpack":
				DB.add(ID, "inventory", "backpack", 1)
				p = 0
				for c in GF.objetItem:
					if c.nom == "backpack":
						p = c.poids * (-1)
				msg += "\nEn trouvant ce <:gem_backpack:{0}>`backpack` tu gagne {1} points d'inventaire".format(GF.get_idmogi("backpack"),p)

			#Calcul du prix
			prix = gain * mise
			if gain != 0 and gain != 1:
				if prix > 0:
					msg += "\nJackpot, vous venez de gagner {} :gem:".format(prix)
				else:
					msg += "\nLa machine viens d'exploser :boom:\nTu as perdu {} :gem:".format(-1*prix)
				DB.addGems(ID, prix)
			elif gain == 1:
				msg += "\nBravo, voici un ticket gratuit pour relancer la machine à sous"
				DB.addGems(ID, prix)
			else:
				msg += "\nLa machine à sous ne paya rien ..."
				DB.addGems(ID, val)
			DB.updateComTime(ID, "slots")
		else:
			msg = "Il faut attendre "+str(GF.couldown_xl)+" secondes entre chaque commande !"
		await ctx.channel.send(msg)


class GemsTest(commands.Cog):

	def __init__(self,ctx):
		return(None)


	@commands.command(pass_context=True)
	async def gemstest(self, ctx):
		await ctx.channel.send(":regional_indicator_t::regional_indicator_e::regional_indicator_s::regional_indicator_t:")



def setup(bot):
	bot.add_cog(GemsBase(bot))
	bot.add_cog(Gems(bot))
	bot.add_cog(GemsTest(bot))
	open("help/cogs.txt","a").write("GemsBase\n")
	open("help/cogs.txt","a").write("Gems\n")
