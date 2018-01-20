# The command file for every external command not specifically for running
# the bot. Even more relevant commands like broadcast options are treated as such.
##
# True: Allows that the command in question can, if gotten from a room,
#       be returned to the same room rather than a PM.
# False: This will ALWAYS return the reply as a PM, no matter where it came from
#
# Information passed from the chat-parser:
#   self: The program object itself.
#
#   cmd: Contains what command was used.
#
#   params: This hold everything else that was passed with the command, such as
#        optional parameters.
#
#   room: What room the command was used in. If the command was sent in a pm,
#         room will contain: 'Pm'. See room.py for more details.
#
#   user: A user object like the one described in the app.py file

from random import randint, choice
import re
import json
import io
import string
import os.path
import math # For funsies

from invoker import ReplyObject, Command

#String is too large for python to handle without seriously slowing.
from largefile import cmap

from data.tiers import tiers, formats
from data.links import Links, YoutubeLinks
from data.pokedex import Pokedex
from data.types import Types
from data.replies import Lines

from user import User
import time

appdList = ['acir']
squadOwners = [['A', 'none'],['B', 'none'],['C', 'none']]
factionList = ['oasis', 'haven', 'aquan', 'sylvan', 'fortress', 'dungeon', 'inferno', 'necropolis']
hostedList = []
usageLink = r'http://www.smogon.com/stat≠s/2017-08/'

def mergeDict(x, y):
    #am lazy
    z = x.copy()
    z.update(y)
    return z

def removePunctuation(params):
    for char in string.punctuation:
        params = params.replace(char, '')
    return params.strip(' ')

def upload(filename, data):
    try:
        to_unicode = unicode
    except NameError:
        to_unicode = str
    with io.open(filename, 'w', encoding='utf8') as outfile:
        str_ = json.dumps(data,
                          indent=4, sort_keys=True,
                          separators=(',', ': '), ensure_ascii=False)
        outfile.write(to_unicode(str_))
    with open(filename) as data_file:
        data_loaded = json.load(data_file)

def download(filename):
    with open(filename) as data_file:
        data_loaded = json.load(data_file)
    return data_loaded

def URL(): return 'https://github.com/QuiteQuiet/PokemonShowdownBot/'

def roomInfo(robot, cmd, params, user, room):
    return ReplyObject(room.users, False)

def c(robot, cmd, params, user):
    if user.id == '4mat':
        return ReplyObject('smh 4-mat')
    return ReplyObject(params, True)

def roll(robot,cmd,params,user):
    if user.id in appdList or user.id in hostedList or user.isOwner:
        partone = params.split('d')
        parttwo = partone[1].split('+')
        partthree = list(partone.pop(0))
        partthree.extend(parttwo)
        values = []
        for i in range(int(partthree[0])):
            values.append(randint(1,int(partthree[1])))
        if partthree[-1] == partthree[1]:
            final = sum(values)
        else:
            final = sum(values)+int(partthree[2])
        output = '**Rolls:** ' + str(values)[1:-1] + ' | **Total:** ' + str(final)
    return ReplyObject(output, True)

def host(robot, cmd, params, user, room):
    if room.isPM == True:
        if user.id in appdList and params not in hostedList:
            hostedList.append(params)
            for x in [0,1,2]:
                if 'none' in squadOwners[x]:
                    squadOwners[x][1] = params
                    whichSquad = squadOwners[x][0]
                    break
            return ReplyObject("Player **" + params + "** hosted. (Squad " + whichSquad + ")", True)
        elif user.id in hostedList:
            return ReplyObject(params + " is already hosted!", True)
        
def currenthost(robot, cmd, params, user, room):
    if room.isPM != True:
        hoststring = ''
        for i in hostedList:
            hoststring = hoststring + i + ', '
        hosts = hoststring[:-1]
        return ReplyObject('Current hosts: ' + hosts + '.', True)

def dehost(robot, cmd, params, user, room):
    if room.isPM == (True or False):
        if params == '':
            if user.id in hostedList:
                hostedList.remove(user.id)
                for x in [0,1,2]:
                    if user.id in squadOwners[x]:
                        squadOwners[x][1] = 'none'
                        break
                return ReplyObject('User ' + user.id + ' dehosted.', True)
            else:
                return ReplyObject('You are not hosted!', False)
        elif params in hostedList and user.id in appdList:
            hostedList.remove(params)
            for x in [0,1,2]:
                if params in squadOwners[x]:
                    squadOwners[x][1] = 'none'
                    break
            return ReplyObject('User ' + params + ' dehosted.', True)
        elif user.id in appdList:
            return ReplyObject('User ' + params + ' is not hosted!.', True)

def register(robot, cmd, params, user, room):
    paramsList = params.split(',')
    if user.id in appdList:
        if paramsList[1].strip(' ').lower() in factionList:
            data = {'Name': paramsList[0].strip(' '),
                    'Current Faction': paramsList[1].strip(' ').lower(),
                    'oasis': 1,
                    'aquan': 1,
                    'haven': 1,
                    'sylvan': 1,
                    'fortress': 1,
                    'inferno': 1,
                    'dungeon': 1,
                    'necropolis': 1,
                    'XP': 0}
            filename = str('playerlist/' + paramsList[0] + '.json')
            if os.path.isfile(filename) == True:
                return ReplyObject(paramsList[0] + ' is already a registered user!')
            upload(filename, data)
            return ReplyObject('Player ' + paramsList[0] + ' registered.', True)
        else:
            return ReplyObject(paramsList[1] + ' is not a valid faction.', True)

def playerTable1v1(squadDict):
    return str('<table align="center" border="2" colour="blue"><tr style="background-color: #A4C4F7"><th></th><th>Name</th><th>Faction</th><th>Level</th><th>Gold</th></tr><tr style="background-color: #A4C4F7"><th>P1</th><th>'+squadDict['P1Name']+'</th><th>'+squadDict['P1Faction'].title()+'</th><th>'+str(squadDict['P1Level'])+'</th><th>'+str(squadDict['P1Gold'])+'</th></tr><tr style="background-color: #A4C4F7"><th>P2</th><th>'+squadDict['P2Name']+'</th><th>'+squadDict['P2Faction'].title()+'</th><th>'+str(squadDict['P2Level'])+'</th><th>'+str(squadDict['P2Gold'])+'</tr></table>')

def startgame(robot, cmd, params, user, room):
    paramsList = params.split(',')
    if paramsList[0] == '1v1':
        P1Filename = str('playerlist/' + paramsList[1] + '.json')
        P2Filename = str('playerlist/' + paramsList[2] + '.json')
        if os.path.isfile(P1Filename) == True and os.path.isfile(P2Filename) == True:
            P1json = download(P1Filename)
            P2json = download(P2Filename)
            playerInfoDict = {"P1Name": P1json["Name"],
                              "P2Name": P2json["Name"],
                              "P1Faction": P1json["Current Faction"],
                              "P2Faction": P2json["Current Faction"],
                              "P1Level": P1json[P1json["Current Faction"]],
                              "P2Level": P2json[P2json["Current Faction"]],
                              "P1Gold": 0,
                              "P2Gold": 0}
            for x in [0,1,2]:
                if user.id in squadOwners[x]:
                    whichSquad = squadOwners[x][0]
                    break
            basemap = download('squads/basemap.json')
            squadDict = mergeDict(playerInfoDict,basemap)
            filename = 'squads/squad' + whichSquad + '.json'
            upload(filename, squadDict)
            initGame(filename)
            print('!htmlbox <h3 align="center">Game successfully started.</h3>' + playerTable1v1(squadDict)+ cmap(squadDict))
            return ReplyObject('!htmlbox <h3 align="center">Game succesfully started.</h3>' + playerTable1v1(squadDict) + cmap(squadDict), True)
        return ReplyObject('One of those players does not exist!', True)
    return ReplyObject('Sorry, only 1v1 mode is supported right now', True)

def initGame(squadFileName):
    squadDict = download(squadFileName)
    # Initalising starting buildings for P1
    P1FactionInfo = download('factions/' + squadDict['P1Faction'] + '.json')
    squadDict['D']['2'] = P1FactionInfo['Building1A']
    # Initalising starting buildings for P2
    P2FactionInfo = download('factions/' + squadDict['P1Faction'] + '.json')
    squadDict['D']['12'] = P2FactionInfo['Building1A']
    upload(squadFileName,squadDict)
    
def switchfaction(robot, cmd, params, user):
    if params.lower() in factionList:
        filename = str('playerlist/' + user.id + '.json')
        if os.path.isfile(filename) == True:
            newDict = download(filename)
            newDict['Current Faction'] = params
            upload(filename, newDict)
            return ReplyObject('Faction succesfully changed to **' + params.title() + '**.', False)
        return ReplyObject('Sorry, you are not a registered player. PM any room auth (+, %, @, #) to get you signed up.', False)
    return ReplyObject(params + ' is not a valid faction.')

def xp(robot, cmd, params, user):
    if user.id in appdList:
        paramsList = params.split(',')
        for x in paramsList:
            if x.isdigit() == False and x.lower() != 'remove':
                removePunctuation(x)
                filename = str('playerlist/' + x + '.json')
                newDict = download(filename)
                if paramsList[0].lower() == 'remove':
                    newDict['XP'] = newDict['XP'] - int(paramsList[1])
                else:
                    newDict['XP'] = newDict['XP'] + int(paramsList[0])
                upload(filename, newDict)
        if paramsList[0].lower() == 'remove':
            return ReplyObject('Experience succesfully removed.', True)
        return ReplyObject('Experience succesfully awarded.', True)
    
def playerinfo(robot, cmd, params, user):
    if params == '':
        params = user.id
    params = removePunctuation(params)
    filename = str('playerlist/' + params + '.json')
    if os.path.isfile(filename) == False and params == user.id:
        return ReplyObject('Sorry, you are not a registered player. PM any room auth (+, %, @, #) to get you signed up.', False)
    elif os.path.isfile(filename) == False:
        return ReplyObject('That player does not exist!')
    with open(filename) as data_file:
        data_loaded = json.load(data_file)
    currentFact = data_loaded['Current Faction']
    return ReplyObject('**' + data_loaded['Name'].title() + '** - **' + data_loaded['Current Faction'].title() + '** ' + str(data_loaded[currentFact]) + ' - **' + str(data_loaded['XP']) + 'XP**', True)

def get(robot, cmd, params, user):
    if user.isOwner():
        res = str(eval(params))
        return ReplyObject(res if not res == None else '', True)
    return ReplyObject('You do not have permisson to use this command. (Only for owner)')

def forcerestart(robot, cmd, params, user):
    if user.hasRank('#'):
        # Figure out how to do this
        robot.closeConnection()
        return ReplyObject('')
    return ReplyObject('You do not have permisson to use this command. (Only for owner)')

def savedetails(robot, cmd, params, user):
    """ Save current robot.details to details.yaml (moves rooms to joinRooms)
     Please note that this command will remove every comment from details.yaml, if those exist."""
    if user.hasRank('#'):
        robot.saveDetails()
        return ReplyObject('Details saved.', True)
    return ReplyObject("You don't have permission to save settings. (Requires #)")

def newautojoin(robot, cmd, params, user):
    if user.hasRank('#'):
        # Join the room before adding it to list of autojoined rooms
        robot.joinRoom(params)
        robot.saveDetails(True)
        return ReplyObject("New autojoin ({room}) added.".format(room = params))
    return ReplyObject("You don't have permission to save settings. (Requires #)")

def setbroadcast(robot, cmd, params, user):
    params = robot.removeSpaces(params)
    if params in User.Groups or params in ['off', 'no', 'false']:
        if user.hasRank('#'):
            if params in ['off', 'no', 'false']: params = ' '
            if robot.details['broadcastrank'] == params:
                return ReplyObject('Broadcast rank is already {rank}'.format(rank = params if not params == ' ' else 'none'), True)
            robot.details['broadcastrank'] = params
            return ReplyObject('Broadcast rank set to {rank}. (This is not saved on reboot)'.format(rank = params if not params == ' ' else 'none'), True)
        return ReplyObject('You are not allowed to set broadcast rank. (Requires #)')
    return ReplyObject('{rank} is not a valid rank'.format(rank = params if not params == ' ' else 'none'))

def links(robot, cmd, params):
    params = params.lower()
    if params in Links[cmd]:
        return ReplyObject(Links[cmd][params], True)
    return ReplyObject('{tier} is not a supported format for {command}'.format(tier = params if params else "''", command = cmd), True)

def randpoke(robot, cmd):
    pick = list(tiers[cmd])[randint(0,len(tiers[cmd])-1)]
    pNoForm = re.sub('-(?:Mega(?:-(X|Y))?|Primal)','', pick).lower()
    return ReplyObject('{poke} was chosen: http://www.smogon.com/dex/sm/pokemon/{mon}/'.format(poke = pick, mon = pNoForm), True)

def randteam(robot, cmd):
    # Helper function that calculates if the team sucks against any specific type
    def acceptableWeakness(team):
        if not team: return False
        comp = {t:{'weak':0,'res':0} for t in Types}
        for poke in team:
            types = Pokedex[poke]['types']
            if len(types) > 1:
                for matchup in Types:
                    eff = Types[types[0]][matchup] * Types[types[1]][matchup]
                    if eff > 1:
                        comp[matchup]['weak'] += 1
                    elif eff < 1:
                        comp[matchup]['res'] += 1
            else:
                for matchup in Types:
                    if Types[types[0]][matchup] > 1:
                        comp[matchup]['weak'] += 1
                    elif Types[types[0]][matchup] < 1:
                        comp[matchup]['res'] += 1
        for t in comp:
            if comp[t]['weak'] >= 3:
                return False
            if comp[t]['weak'] >= 2 and comp[t]['res'] <= 1:
                return False
        return True

    cmd = cmd.replace('team','poke')
    team = set()
    hasMega = False
    attempts = 0
    while len(team) < 6 or not acceptableWeakness(team):
        poke = choice(list(tiers[cmd]))
        # Test if share dex number with anything in the team
        if [p for p in team if Pokedex[poke]['num'] == Pokedex[p]['num']]:
            continue
        if hasMega and '-Mega' in poke:
            continue
        team |= {poke}
        if not acceptableWeakness(team):
            team -= {poke}
        elif '-Mega' in poke:
            hasMega = True
        if len(team) >= 6:
            break
        attempts += 1
        if attempts >= 100:
            # Prevents locking up if a pokemon turns the team to an impossible genration
            # Since the team is probably bad anyway, just finish it and exit
            while len(team) < 6:
               team |= {choice(list(tiers[cmd]))}
            break
    return ReplyObject(' / '.join(list(team)), True)


def pokedex(robot, cmd, params, user, room):
    cmd = re.sub('-(?:mega(?:-(x|y))?|primal)','', cmd)
    substitutes = {'gourgeist-s':'gourgeist-small',  # This doesn't break Arceus-Steel like adding |S to the regex would
                   'gourgeist-l':'gourgeist-large',  # and gourgeist-s /pumpkaboo-s still get found, because it matches the
                   'gourgeist-xl':'gourgeist-super', # entry for gougeist/pumpkaboo-super
                   'pumpkaboo-s':'pumpkaboo-small',
                   'pumpkaboo-l':'pumpkaboo-large',
                   'pumpkaboo-xl':'pumpkaboo-super',
                   'giratina-o':'giratina-origin',
                   'mr.mime':'mr_mime',
                   'mimejr.':'mime_jr'
    }
    # Just in case do a double check before progressing...
    if cmd.lower() not in (robot.removeSpaces(p).lower() for p in Pokedex):
        return ReplyObject('{cmd} is not a valid command'.format(cmd = cmd), True)
    if cmd in substitutes:
        cmd = substitutes[cmd]
    if params not in ('rb', 'gs', 'rs', 'dp', 'bw', 'xy', 'sm'):
        params = 'sm'
    if robot.canHtml(room):
        return ReplyObject('/addhtmlbox <a href="http://www.smogon.com/dex/{gen}/pokemon/{mon}/">{capital} analysis</a>'.format(gen = params, mon = cmd, capital = cmd.title()), True, True)
    return ReplyObject('Analysis: http://www.smogon.com/dex/{gen}/pokemon/{mon}/'.format(gen = params, mon = cmd), reply = True, pmreply = True)


commands = [
    # The easy stuff that can be done with a single lambda expression
    Command(['source', 'git'], lambda: ReplyObject('Source code can be found at: {url}'.format(url = URL()), True)),
    Command(['credits'], lambda: ReplyObject('Credits can be found: {url}'.format(url = URL()), True)),
    Command(['owner'], lambda s: ReplyObject('Owned by: {owner}'.format(owner = s.owner), True)),
    Command(['commands', 'help'], lambda: ReplyObject('Read about commands here: {url}blob/master/COMMANDS.md'.format(url = URL()), reply = True, pmreply = True)),
    Command(['explain'], lambda: ReplyObject("BB-8 is the name of a robot in the seventh Star Wars movie :)", True)),
    Command(['ask'], lambda: ReplyObject(Lines[randint(0, len(Lines) - 1)], True)),
    Command(['squid'], lambda: ReplyObject('\u304f\u30b3\u003a\u5f61', True)),
    Command(['seen'], lambda: ReplyObject("This is not a command because I value other users privacy.", True)),
    Command(['broadcast'], lambda s: ReplyObject('Rank required to broadcast: {rank}'.format(rank = s.details['broadcastrank']), True)),
    Command(['usage'], lambda: ReplyObject(usageLink, reply = True, pmreply = True)),
    Command(['pick'], lambda s, c, p: ReplyObject(choice(p.split(',')), True)),

    # Generate the command list on load
    Command([link for link in YoutubeLinks], lambda s, c: ReplyObject(YoutubeLinks[c], True)),
    Command([f for f in formats], lambda s, c: ReplyObject('Format: http://www.smogon.com/dex/sm/formats/{tier}/'.format(tier = c), True)),

    # Commands with dedicated functions because of their complexity (need more than a single expression)
    Command(['c', 'command'], c),
    Command(['register', 'reg'], register),
    Command(['pi', 'playerinfo'], playerinfo),
    Command(['switchfaction', 'sf'], switchfaction),
    Command(['xp'], xp),
    Command(['startgame', 'sg'], startgame),
    Command(['dehost'], dehost),
    Command(['r', 'roll'], roll),
    Command(['ri'], roomInfo),
    Command(['get'], get),
    Command(['host'], host),
    Command(['currenthosts', 'hosts'], currenthost),
    Command(['forcerestart'], forcerestart),
    Command(['savedetails'], savedetails),
    Command(['newautojoin'], newautojoin),
    Command(['setbroadcast'], setbroadcast),
    Command([l for l in Links], links),
    Command([t for t in tiers], randpoke),
    Command([t.replace('poke','team') for t in tiers], randteam),

    # Hardcoding the extra parameters that the regex previously took care of
    Command([re.sub(r'[^a-zA-Z0-9]', '', p).lower() for p in Pokedex] + ['pumpkaboo-s', 'pumpkaboo-l', 'pumpkaboo-xl', 'gourgeist-s', 'gourgeist-l', 'gourgeist-xl', 'giratina-o'], pokedex)
]
