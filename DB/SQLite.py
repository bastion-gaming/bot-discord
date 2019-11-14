import discord
import sqlite3 as sql
import datetime as dt
import time as t
import json
from core import welcome as wel
from gems import gemsFonctions as GF


DB_NOM = 'bastionDB'

def nom_ID(nom):
	"""Convertis un nom en ID discord """
	if len(nom) == 21 :
		ID = int(nom[2:20])
	elif len(nom) == 22 :
		ID = int(nom[3:21])
	else :
		print("DB >> mauvais nom")
		ID = -1
	return(ID)

#===============================================================================
# Ouverture du fichier DB
#===============================================================================
conn = sql.connect('DB/{}.db'.format(DB_NOM))

#===============================================================================
# Initialisation et vérification de la DB
#===============================================================================
def init():
	# Liste des tables
	with open("DB/DBlist.json", "r") as f:
		l = json.load(f)
	for one in l:
		# Ouverture du template de la table en cours
		with open("DB/Templates/{}Template.json".format(one), "r") as f:
			t = json.load(f)
		cursor = conn.cursor()
		script = "CREATE TABLE IF NOT EXISTS {}(".format(one)
		i = 0
		PRIMARYKEY = ""
		PRIMARYKEYlink = ""
		link = ""
		for x in t:
			if i != 0:
				script += ", "
			y = t[x].split("_")
			if len(y) > 1:
				if y[0] == "ID":
					script += "{0} {1} NOT NULL".format(x, y[1])
					link = "FOREIGN KEY(ID) REFERENCES IDs(ID)"
				elif y[0] == "PRIMARYKEY":
					script += "{0} {1} NOT NULL".format(x, y[1])
					PRIMARYKEY = "{}".format(x)
				elif y[0] == "link":
					script += "{0} INTEGER NOT NULL".format(x)
					PRIMARYKEYlink = "{}".format(x)
					link = "FOREIGN KEY({1}) REFERENCES {0}({1})".format(y[1], x)
			else:
				script += "{0} {1}".format(x, t[x])
			i += 1
		# Configuration des clés primaires
		if PRIMARYKEY != "" and PRIMARYKEYlink != "":
			script += ", PRIMARY KEY ({}, {})".format(PRIMARYKEY, PRIMARYKEYlink)
		elif PRIMARYKEY != "" and PRIMARYKEYlink == "":
			script += ", PRIMARY KEY ({})".format(PRIMARYKEY)
		elif PRIMARYKEY == "" and PRIMARYKEYlink != "":
			script += ", PRIMARY KEY ({})".format(PRIMARYKEYlink)
		if link != "":
			script += ", {}".format(link)
		script += ")"
		# éxécution du script pour la table en cours
		cursor.execute(script)
		conn.commit()
	# Quand toute les tables ont été créée (si elles n'existait pas), envoie un message de fin
	return "SQL >> DB initialisée"

#-------------------------------------------------------------------------------
def checkField():
	# Init de la variable flag
	flag = 0
	FctCheck = False
	while not FctCheck:
		try:
			FctCheck = True
			# Liste des tables
			with open("DB/DBlist.json", "r") as f:
				l = json.load(f)
			for one in l:
				# Ouverture du template de la table en cours
				with open("DB/Templates/{}Template.json".format(one), "r") as f:
					t = json.load(f)
				cursor = conn.cursor()
				# Récupération du nom des colonnes de la table en cours
				cursor.execute("PRAGMA table_info({0});".format(one))
				rows = cursor.fetchall()

				#Suppression
				for x in rows:
					if x[1] not in t:
						script = "ALTER TABLE {0} RENAME TO {0}_old".format(one)
						cursor.execute(script)
						init()
						cursor.execute("PRAGMA table_info({0}_old);".format(one))
						temp = ""
						for z in cursor.fetchall():
							if temp == "":
								temp += "{}".format(z[1])
							else:
								temp += ", {}".format(z[1])
						script = "INSERT INTO {0} ({1})\n	SELECT {1}\n	FROM {0}_old".format(one, temp)
						cursor.execute(script)
						cursor.execute("DROP TABLE {}_old".format(one))
						conn.commit()
						flag = "sup"+str(flag)

				#Type & add
				for x in t:
					check = False
					NotCheck = False
					y = t[x].split("_")
					for row in rows:
						if row[1] == x:
							if len(y) > 1:
								if row[2] == y[1]:
									check = True
								elif y[0] == "link":
									if row[2] == "INTEGER":
										check = True
									else:
										NotCheck = True
								else:
									NotCheck = True
							else:
								if row[2] == t[x]:
									check = True
								else:
									NotCheck = True
					if NotCheck:
						script = "ALTER TABLE {0} RENAME TO {0}_old".format(one)
						cursor.execute(script)
						init()
						cursor.execute("PRAGMA table_info({0}_old);".format(one))
						temp = ""
						for z in cursor.fetchall():
							if temp == "":
								temp += "{}".format(z[1])
							else:
								temp += ", {}".format(z[1])
						script = "INSERT INTO {0} ({1})\n	SELECT {1}\n	FROM {0}_old".format(one, temp)
						cursor.execute(script)
						cursor.execute("DROP TABLE {}_old".format(one))
						conn.commit()
						flag = "type"+str(flag)
					elif not check:
						if len(y) > 1:
							temp = y[1]
						else:
							temp = y[0]
						script = "ALTER TABLE {0} ADD COLUMN {1} {2}".format(one, x, temp)
						cursor.execute(script)
						flag = "add"+str(flag)
		except:
			FctCheck = False
	return flag


#===============================================================================
# Gestion des utilisateurs
#===============================================================================

def get_PlayerID(ID):
	script = "SELECT * FROM IDs WHERE ID_discord = {}".format(ID)
	cursor = conn.cursor()
	cursor.execute(script)
	rows = cursor.fetchall()
	if rows == []:
		return "Error 404"
	else:
		for x in rows:
			return "{}".format(x[0])

#-------------------------------------------------------------------------------
def newPlayer(ID, nameDB = None):
	"""
	Permet d'ajouter un nouveau joueur à la base de donnée en fonction de son ID.

	ID: int de l'ID du joueur
	"""
	if nameDB == None:
		nameDB = "bastion"

	with open("DB/Templates/{}Template.json".format(nameDB), "r") as f:
		t = json.load(f)

	PlayerID = get_PlayerID(ID)
	if PlayerID == "Error 404":
		#Init du joueur avec les champs de base
		script = "INSERT INTO IDs (ID_discord) VALUES ({})".format(ID)
		cursor.execute(script)
		conn.commit()
		PlayerID = get_PlayerID(ID)
		data = "ID"
		values = PlayerID
		for x in t:
			if x == "arrival":
				data += ", {}".format(x)
				values += ", '{}'".format(str(dt.date.today()))
			elif x != "id{}".format(nameDB) and x != "ID":
				data += ", {}".format(x)
				if "INTEGER" in t[x]:
					values += ", 0"
				else:
					values += ", NULL"
		script = "INSERT INTO {0} ({1}) VALUES ({2})".format(nameDB, data, values)
		cursor.execute(script)
		conn.commit()
		return ("Le joueur a été ajouté !")
	else:
		script = "SELECT * FROM {0} WHERE ID = {1}".format(nameDB, PlayerID)
		cursor.execute(script)
		z = cursor.fetchall()
		if z == []:
			data = "ID"
			values = PlayerID
			for x in t:
				if x == "arrival":
					data += ", {}".format(x)
					values += ", '{}'".format(str(dt.date.today()))
				elif x != "id{}".format(nameDB) and x != "ID":
					data += ", {}".format(x)
					if "INTEGER" in t[x]:
						values += ", 0"
					else:
						values += ", NULL"
			script = "INSERT INTO {0} ({1}) VALUES ({2})".format(nameDB, data, values)
			cursor.execute(script)
			conn.commit()
			return ("Le joueur a été ajouté !")
		else:
			return ("Le joueur existe déjà")


#===============================================================================
# Compteur
#===============================================================================
def countTotalMsg():
	#Init a
	script = "SELECT SUM(nbmsg) FROM bastion"
	cursor = conn.cursor()
	cursor.execute(script)
	for a in cursor.fetchall():
		return a[0]

#-------------------------------------------------------------------------------
def countTotalGems():
	#Init a
	script = "SELECT SUM(gems) FROM gems"
	cursor = conn.cursor()
	cursor.execute(script)
	for a in cursor.fetchall():
		return a[0]

#-------------------------------------------------------------------------------
def countTotalSpinelles():
	#Init a
	script = "SELECT SUM(spinelles) FROM gems"
	cursor = conn.cursor()
	cursor.execute(script)
	for a in cursor.fetchall():
		return a[0]

#-------------------------------------------------------------------------------
def taille(nameDB = None):
	"""Retourne la taille de la table selectionner"""
	if nameDB == None:
		nameDB = "bastion"
	cursor = conn.cursor()
	cursor.execute("PRAGMA table_info({0});".format(nameDB))
	rows = cursor.fetchall()
	script = "SELECT count({1}) FROM {0}".format(nameDB, rows[0][1])
	cursor.execute(script)
	for t in cursor.fetchall():
		return t[0]


#===============================================================================
# Fonctions
#===============================================================================
nameDBexcept = ["inventory", "durability", "hothouse", "cooking", "trophy", "statgems", "filleul", "bastion_com_time", "gems_com_time", "capability"]

#-------------------------------------------------------------------------------
def updateField(ID, fieldName, fieldValue, nameDB = None):
	"""
	Permet de mettre à jour la valeur fieldName par la fieldValue.

	ID: int de l'ID du joueur.
	fieldName: string du nom du champ à changer
	fieldValue: string qui va remplacer l'ancienne valeur
	"""
	PlayerID = get_PlayerID(ID)
	if PlayerID != "Error 404":
		if nameDB == None:
			nameDB = "bastion"
		cursor = conn.cursor()

		one = valueAt(ID, fieldName, nameDB)
		if one == 0:
			# print("DB >> Le champ n'existe pas")
			return "201"
		else:
			if nameDB == "bastion" or nameDB == "gems":
				IDname = "ID"
				script = "UPDATE {0} SET {1} = '{2}' WHERE {4} = '{3}'".format(nameDB, fieldName, fieldValue, PlayerID, IDname)
			else:
				cursor.execute("PRAGMA table_info({0});".format(nameDB))
				rows = cursor.fetchall()
				for x in rows:
					if x[1] == "idbastion":
						IDname = "bastion"
					elif x[1] == "idgems":
						IDname = "gems"
				script = "SELECT id{0} FROM {0} WHERE ID = '{1}'".format(IDname, PlayerID)
				cursor.execute(script)
				for z in cursor.fetchall():
					PlayerID = z[0]
				script = "UPDATE {0} SET {1} = '{2}' WHERE id{4} = '{3}'".format(nameDB, fieldName, fieldValue, PlayerID, IDname)
			for x in nameDBexcept:
				if x == nameDB:
					if x == "inventory":
						script = "UPDATE {0} SET Stock = '{2}' WHERE Item = '{1}' and id{4} = '{3}'".format(nameDB, fieldName, fieldValue, PlayerID, IDname)
					elif x == "trophy" or x == "statgems":
						script = "UPDATE {0} SET Stock = '{2}' WHERE Nom = '{1}' and id{4} = '{3}'".format(nameDB, fieldName, fieldValue, PlayerID, IDname)
					elif x == "durability":
						script = "UPDATE {0} SET Durability = '{2}' WHERE Item = '{1}' and id{4} = '{3}'".format(nameDB, fieldName, fieldValue, PlayerID, IDname)
					elif x == "gems_com_time" or x == "bastion_com_time":
						script = "UPDATE {0} SET Com_time = '{2}' WHERE Commande = '{1}' and id{4} = '{3}'".format(nameDB, fieldName, fieldValue, PlayerID, IDname)
					elif x == "hothouse":
						script = "UPDATE {0} SET Time = '{2}', Plante = '{5}' WHERE idPlantation = '{1}' and id{4} = '{3}'".format(nameDB, fieldName, fieldValue[0], PlayerID, IDname, fieldValue[1])
					elif x == "cooking":
						script = "UPDATE {0} SET Time = '{2}', Plat = '{5}'  WHERE idFour = '{1}' and id{4} = '{3}'".format(nameDB, fieldName, fieldValue, PlayerID, IDname, fieldValue[1])
					else:
						return "202"
			cursor.execute(script)
			conn.commit()
			return "200"
	else:
		return "404"

#-------------------------------------------------------------------------------
def valueAt(ID, fieldName, nameDB = None):
	"""
	Permet de récupérer la valeur contenue dans le champ fieldName de ID

	ID: int de l'ID du joueur
	fieldName: string du nom du champ à chercher
	"""
	if nameDB == None:
		nameDB = "bastion"

	PlayerID = get_PlayerID(ID)
	if PlayerID != "Error 404":
		cursor = conn.cursor()

		if not nameDB in nameDBexcept:
			try:
				script = "SELECT {1} FROM {0} WHERE ID = '{2}'".format(nameDB, fieldName, PlayerID)
				cursor.execute(script)
				value = cursor.fetchall()
			except:
				value = []
		else:
			fieldName2 = ""
			for x in nameDBexcept:
				if x == nameDB:
					if x == "bastion_com_time":
						fieldName2 = "Commande"
						fieldName3 = "Com_time, Commande"
						link = "bastion"
					else:
						if x == "inventory" or x == "durability":
							fieldName2 = "Item"
							fieldName3 = "Stock, Item"
						elif x == "trophy" or x == "statgems":
							fieldName2 = "Nom"
							fieldName3 = "Stock, Nom"
						elif x == "hothouse":
							fieldName2 = "idPlantation"
							fieldName3 = "Time, Plante, idPlantation"
						elif x == "cooking":
							fieldName2 = "idFour"
							fieldName3 = "Time, Plat, idFour"
						elif x == "gems_com_time":
							fieldName2 = "Commande"
							fieldName3 = "Com_time, Commande"
						link = "gems"
			try:
				script = "SELECT {5} FROM {0} JOIN {3} USING(id{3}) JOIN IDs USING(ID) WHERE ID = '{4}' and {2} = '{1}'".format(nameDB, fieldName, fieldName2, link, PlayerID, fieldName3)
				cursor.execute(script)
				value = cursor.fetchall()
			except:
				value = []

		if value == []:
			return 0
		else:
			return value[0]

#-------------------------------------------------------------------------------
def addGems(ID, nb):
	"""
	Permet d'ajouter un nombre de gems à quelqu'un. Il nous faut son ID et le nombre de gems.
	Si vous souhaitez en retirer mettez un nombre négatif.
	Si il n'y a pas assez d'argent sur le compte la fonction retourne un nombre
	strictement inférieur à 0.
	"""
	old_value = valueAt(ID, "gems", "gems")
	new_value = int(old_value[0]) + int(nb)
	if new_value >= 0:
		updateField(ID, "gems", new_value, "gems")
		print("DB >> Le compte de "+str(ID)+ " est maintenant de: "+str(new_value))
	else:
	 	print("DB >> Il n'y a pas assez sur ce compte !")
	return str(new_value)

#-------------------------------------------------------------------------------
def addSpinelles(ID, nb):
	"""
	Permet d'ajouter un nombre de gems à quelqu'un. Il nous faut son ID et le nombre de gems.
	Si vous souhaitez en retirer mettez un nombre négatif.
	Si il n'y a pas assez d'argent sur le compte la fonction retourne un nombre
	strictement inférieur à 0.
	"""
	old_value = valueAt(ID, "spinelles", "gems")
	new_value = int(old_value[0]) + int(nb)
	if new_value >= 0:
		updateField(ID, "spinelles", new_value, "gems")
		print("DB >> Le compte de "+str(ID)+ " est maintenant de: "+str(new_value))
	else:
	 	print("DB >> Il n'y a pas assez sur ce compte !")
	return str(new_value)

#-------------------------------------------------------------------------------
def spam(ID, couldown, nameElem, nameDB = None):
	"""Antispam """
	if nameDB == None:
		nameDB = "bastion_com_time"

	ComTime = valueAt(ID, "Com_time", nameDB)
	if ComTime != 0:
		time = ComTime[0]
	else:
		return True

	# on récupère la date de la dernière commande
	return(time < t.time()-couldown)
	
#-------------------------------------------------------------------------------
# def add(ID, stockeur, nameElem, nbElem, nameDB = None):
