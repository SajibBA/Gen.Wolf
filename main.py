from itertools import count
from unicodedata import name
import discord
import os
import random
import sqlite3
import re
from discord.ext import commands

con = sqlite3.connect("gen_wolf.db")
cur = con.cursor()

#client = discord.Client()
#bot = commands.Bot("$")
client = commands.Bot(command_prefix="$", help_command=None)

player1 =  ""
player2 = ""
player1_hp =  0
player2_hp = 0
turn = ""
gameOver = True

# weapons = ["ak","bow","grenade"]

class weapons:
  def __init__(self, name, min_dmg, max_dmg, hit_chance):
    self.name = name
    self.min_dmg = min_dmg
    self.max_dmg = max_dmg
    self.hit_chance = hit_chance

# creating list       
weapons_list = [] 
  
# appending instances to list 
weapons_list.append( weapons("ak", 6, 9, 100) )
weapons_list.append( weapons("bow", 12, 16, 60) )
weapons_list.append( weapons("grenade", 32, 43, 20) )

weapons_names = []
for weapon in weapons_list:
    weapons_names.append(weapon.name)

def update_encouragements(nickname):
    cur.execute('''SELECT * from nicknames''')
    rows = cur.fetchall()
    rows=[i[0] for i in rows]
    if nickname in rows:
        pass
    else:
        cur.execute('''INSERT INTO nicknames(nick_name)
        VALUES (?)''',(nickname,))
        con.commit()

@client.command()
async def test(ctx, arg):
    await ctx.send(arg)

@client.command()
async def help(ctx):
    await ctx.send('**$nicknames** = Gives a random nickname \n **$hownoob @mention** = Noob meter \n **$duel @mention @mention** = start a fight')



@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))


@client.command()
async def nickname(ctx):
    cur.execute('''SELECT * from nicknames''')
    rows = cur.fetchall()
    rows=[i[0] for i in rows]
    await ctx.send(' {} the **{}**'.format(ctx.author.name.strip('"'), str(random.choice(rows))))

@client.command()
async def new_nickname_create(ctx, *, args):
    new_nickname = args.split(',')[0]
    update_encouragements(new_nickname)
    await ctx.send('New nickname added **{}**'.format(new_nickname))



@client.command()
async def hownoob(ctx, p1 : discord.Member):
    p1name = p1.display_name
    noobnees = random.randint(0,100)
    await ctx.send(' **{}** is {}% noob !'.format(p1name, noobnees))

@hownoob.error
async def hownoob_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention someone for this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to mention/ping players (ie. <@>).")


@client.command()
async def hi(ctx):
    print("hi")
    await ctx.send("hi")

@client.command()
async def duel(ctx, p1 : discord.Member, p2 : discord.Member):
    global player1
    global player2
    global player1_hp
    global player2_hp
    global turn
    global gameOver
    global count
    global weapons_list
    global weapons_names

    if gameOver:
        gameOver = False
        
        player1 = p1
        player2 = p2 
        player1_hp = 100
        player2_hp = 100

        # determine who goes first
        num = random.randint(1, 2)
        await ctx.send(" Use $fire weapon name to attack. Be sure to choose an weapon from ="+ str(weapons_names)+ ". More damage dealer has less accuracy")
        if num == 1:
            turn = player1
            await ctx.send("It is <@" + str(player1.id) + ">'s turn.")
        elif num == 2:
            turn = player2
            await ctx.send("It is <@" + str(player2.id) + ">'s turn.")
    else:
        await ctx.send("A game is already in progress! Finish it before starting a new one.")

@client.command()
async def endduel(ctx):
    global gameOver
    await ctx.send("Duel ending")
    gameOver = True


@client.command()
async def fire(ctx, weapon: str):
    global turn
    global player1
    global player2
    global player1_hp
    global player2_hp
    global board
    global count
    global gameOver
    global weapons
    global weapons_list
    global weapons_names
    valid_weapon = False

    if not gameOver:
        if turn == ctx.author:
            valid_weapon = False
            for weapons in weapons_list:
                    if weapon == weapons.name:
                        valid_weapon = True
                        hit = random.randint(1,100)
                        if hit >= weapons.hit_chance:
                            damage = random.randint(weapons.min_dmg,weapons.max_dmg)
                        else:
                            damage = 0
                            await ctx.send("Shot missed")
                        # if weapon == "ak":
                        #     hit = random.randint(1,100)
                        #     if hit >= 20:
                        #         damage = random.randint(12,20)
                        #     else:
                        #         damage = 0
                        #         await ctx.send("Shot missed")
                        # if weapon == "bow":
                        #     hit = random.randint(1,100)
                        #     if hit >= 50:
                        #         damage = random.randint(18,30)
                        #     else:
                        #         damage = 0
                        #         await ctx.send("Shot missed")
                        # if weapon == "grenade":
                        #     hit = random.randint(1,100)
                        #     if hit >= 80:
                        #         damage = random.randint(28,45)
                        #     else:
                        #         damage = 0
                        #         await ctx.send("Shot missed")
                        
                        # Dealing dmg
                        if turn == player1:
                            player2_hp -= damage
                            if player2_hp > 0:
                                await ctx.send("damage dealt = "+ str(damage)+ ". <@" + str(player2.id) + ">'s remaining health = "+ str(player2_hp))
                            else:
                                await ctx.send(". <@" + str(player2.id) + "> have fallen ")
                        elif turn == player2:
                            player1_hp -= damage
                            if player1_hp > 0:
                                await ctx.send("damage dealt = "+ str(damage)+ ". <@" + str(player1.id) + ">'s remaining health = "+ str(player1_hp))
                            else:
                                await ctx.send(". <@" + str(player1.id) + "> have fallen ")
                        

                        # check hp
                        if player1_hp <= 0:
                            await ctx.send(" <@" + str(player2.id) + "> is the winner ")
                            gameOver = True 
                        elif player2_hp <= 0:
                            await ctx.send(" <@" + str(player1.id) + "> is the winner ")
                            gameOver = True  
                        # switch turns
                        if turn == player1:
                            turn = player2
                        elif turn == player2:
                            turn = player1
            if not valid_weapon:
                await ctx.send("Be sure to choose an weapon from ="+ str(weapons_names)+ ". More damage dealer has less accuracy")
        else:
            await ctx.send("It is not your turn.")

    else:
        await ctx.send("Please start a new game using the $duel command.")


async def checkWinner(ctx, player1_hp, player2_hp):
    global gameOver
    if player1_hp <= 0:
        await ctx.send(" <@" + str(player2.id) + "> is the winner ")
        gameOver = True 
    elif player2_hp <= 0:
        await ctx.send(" <@" + str(player1.id) + "> is the winner ")
        gameOver = True                


@duel.error
async def duel_error(ctx, error):
    print(error)
    if isinstance(error, commands.MissingRequiredArgument):
        await ctx.send("Please mention 2 players for this command.")
    elif isinstance(error, commands.BadArgument):
        await ctx.send("Please make sure to mention/ping players (ie. <@>).")


client.run("OTc4Njc0MjA1MTcwMjE3MDQx.GYYk99.Fi0TnSoPcCdFsJ0M-qNGcPK1GWet05aa5oHSCs")

