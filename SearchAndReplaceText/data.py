# Some will have to be done manually

# REMEBER: We need a special case for option dialogues T__T
# If not possible, just not make them bigger than the byte count
# They either have 2 or 3 options and return a value. We better not touch them
# They extend up to a _nop instruction

# Dialogues
# Always have [] metadata before, so they are easy to identify
# We can modify these ones as we like
# MC calls another function exclusive for him
normal_dialogues = {
	'line_size': 28,
	'n_lines': 3,
	'example':"""{
		"offset": 0x244f22,
		"type":0,
		"isMC": false
		"size": 55,
        "original": "おいコラ　おっさん！\nひとんちの前　ウロチョロしてんな…",
        "metadata": "[face:伸恵:真剣]",
        "en": "Hey you!\nWhat are you doing there!?",
        "es": "¡Oye tú!\n¿¡Qué estás haciendo ahí!?"
	}"""
}

# Black dialogues
# We can modify them as we like but no easy way of identifying them
# Function for this one
black_dialogues = {
	'line_size': 24,
	'n_lines': 2,
	'example':"""{
		"offset": 0x244ddf,
		"type":1,
		"size": 73,
        "original": "暑い夏がやってきた…高校を卒業したあと\n東京に住んでからもう２年になるけど",
        "en": "",
        "es": ""
	}"""
}

# Options
# No meta data
# 1 line, Length: 18 (not more)
# we can modify the byte length easily
# Function takes up to 3 parameters
option_dialogues = {
	'line_size': 18,
	'n_lines': 1,
	'example':"""{
		"type":2,
		"data": [{
			"offset":0,
			"size": 73,
	        "original": "",
	        "en": "",
	        "es": ""
		},{
			"offset":1,
			"size": 73,
	        "original": "",
	        "en": "",
	        "es": ""
		}]
	}"""
}

# Items descriptions
# No metada
# Has a table starting at 0x20c950
# We just have to modify such values if neccesary
# Just modify the pointer
# 2 lines, length: 21
# Couldn't make them thinner

item_descriptions = {
	'line_size': 21,
	'n_lines': 2,
	'table_idx': 2148688,
	'example':"""{
		"offset": 0x22b1be,
		"type":3,
		"size": 55,
        "original": "なかなかタバコがやめられない\nそんなあなたにオススメの一冊",
        "en": "",
        "es": ""
	}"""
}

# Letters
# Have a table at 0x2099dc
# We just have to modify the values if necceary
# Rember not exceed the original count of lines (we don't know what could happen)
# Length: 20
letters_text = {
	'line_size': 20, #Hopefully chnage in the future
	'n_lines': 18,
	'table_idx': 2136540,
	'example':"""{
		"offset": 0x22b1be,
		"type":4,
		"size": 55,
        "original": "お兄ちゃんへ\n\n元気ですか？　…っていっても\nあれからまだ　そんなにたってないよねИ\n夏休みの間は毎日のように会ってたから\nお兄ちゃんがいなくなって\nちょっとさみしい気がするよ\n\nあ　そうそう\nおかしの本　完成したんだよ\nしかも先生に見せたら\nすごくほめてもらっちゃったЖ\nお兄ちゃんのおかげだよ\nお兄ちゃん　ホントにありがとねЖ\n\nまた浜松に帰ってきたら\nいっしょに遊ぼうね\n　　　　　　　　　　　　　　　　千佳より\n",
        "en": "\n\n",
        "es": "Para Onii-chan\n\nTe preguntaría cómo estás\npero apenas nos vimos. И\nComo te vi todas las vaca-\nciones, ahora que no estás\nse siente vacío.\n\nAh, cierto. Terminé todas\nlas recetas y se las enseñé\na mi profesora. Me felicitó\nmucho. Todo fue gracias a ti\nEn serio, muchas graciasЖ\n\nCuando vuelvas, vamos a\njugar de nuevo, ¿va?\n　　　　　　　　　　　　　　Chika"
	}"""
}

# Telephone calls
# We better not mess with them.
# No references, no nothing. We should only overwrite them
# Find them , we currently have no examples
phone_calls = {
	'line_size': 28, #Unknown
	'n_lines': 3, # Unknown
	'example':"""{
		"offset": 0x22b1be,
		"type":5,
		"size": 55,
        "original": "お兄ちゃんへ\n\n元気ですか？　…っていっても\nあれからまだ　そんなにたってないよねИ\n夏休みの間は毎日のように会ってたから\nお兄ちゃんがいなくなって\nちょっとさみしい気がするよ\n\nあ　そうそう\nおかしの本　完成したんだよ\nしかも先生に見せたら\nすごくほめてもらっちゃったЖ\nお兄ちゃんのおかげだよ\nお兄ちゃん　ホントにありがとねЖ\n\nまた浜松に帰ってきたら\nいっしょに遊ぼうね\n　　　　　　　　　　　　　　　　千佳より\n",
        "en": "\n\n",
        "es": "Para Onii-chan\n\nTe preguntaría cómo estás\npero apenas nos vimos. И\nComo te vi todas las vaca-\nciones, ahora que no estás\nse siente vacío.\n\nAh, cierto. Terminé todas\nlas recetas y se las enseñé\na mi profesora. Me felicitó\nmucho. Todo fue gracias a ti\nEn serio, muchas graciasЖ\n\nCuando vuelvas, vamos a\njugar de nuevo, ¿va?\n　　　　　　　　　　　　　　Chika"
	}"""
}

# - 0x2bc7d0 a 0x3bc7a8 será para instrucciones  
# Virtual start: 0x15001d0

# - 0x3bc7a8 a 0x4bc7a8 será para diálogos
# Virtual start: 0x16001a8



'''
Assumptions:
	- Each dialogue is in some file contains exactly where it starts (with "metadata")
	- We save also the max of lines for the dialogue
TODO:
	- Go trough each dialogue
	- If it fits over the original, overwrite it and that's it
	- Find the function pointing to such file using ghidra
	- Check, does it have more than allowed lines?
		- No:
			- Save the text to the next aviable space in TEXT SPACE
			- Change the pointer in the original function, easy
		- Yes:
			- Copy the original function (from parameters that has the 0x3c to the nop)
			- Overwrite it with a jal instruction to the next avaible section in FUNCTION SPACE
			- Divide the text in n = total_lines//MAX_Lines + 1 sections (divide using \n)
			- Then paste them continguous in the TEXT SPACE using the same metadata in all. Save the position
			- In function space create a function and paste the og n times, each one pointing to the new text sections


'''

