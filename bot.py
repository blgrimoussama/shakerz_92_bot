from twitchio.ext import commands, routines, pubsub
from helpers import pathing, to_time, last_senders, get_uptime
from datetime import timedelta, datetime
from func import change_reward_status
from credentials import *
import os
import json
import time
import helpers
import inspect
import requests
import twitchio

headers = {
    'Authorization': f"Bearer {API_ACCESS_TOKEN}",
    'Client-Id': CLIENT_ID
}

channels = ['shakerz_92']
users_oauth_tokens = {}
users_channel_ids = {}
day_jsons = {}
lasts = {}
last_jsons = {}
nexts = {}
todays = {}
currents = {}
current_jsons = {}

for channel in channels:
    users_oauth_tokens[channel] = globals()[f"{channel}_CHANNEL_TOKEN"]
    users_channel_ids[channel] = int(
        requests.get(f"https://api.twitch.tv/helix/users?login={channel}",
                     headers=headers).json()['data'][0]['id'])
    day_jsons[channel] = pathing(f"static/{channel}", 'day.json')
    lasts[channel] = pathing(f"static/{channel}", 'last.txt')
    last_jsons[channel] = pathing(f"static/{channel}", 'last.json')
    with open(day_jsons[channel], "r") as data:
        day = json.load(data)
    nexts[channel] = day['today']
    todays[channel] = datetime.strptime(nexts[channel],
                                        '%d/%m/%Y').strftime("%d_%m_%Y")

    currents[channel] = pathing(f"static/{channel}",
                                     f"spin_{todays[channel]}.txt")
    current_jsons[channel] = pathing(f"static/{channel}",
                                          f"spin_{todays[channel]}.json")


class Bot(commands.Bot):
    def __init__(self, channels):
        self.channels = channels
        self.time = None
        self.ready = False
        self.last_senders = [None] * 8
        # Initialise our Bot with our access token, prefix and a list of channels to join on boot...
        # prefix can be a callable, which returns a list of strings or a string...
        # initial_channels can also be a callable which returns a list of strings...
        # new_channel = input("New channel : ")
        super().__init__(
            token=CHAT_ACCESS_TOKEN,
            prefix=']',
            initial_channels=list(set().union(
                             self.channels, ['0us5ama'])))  # new_channel

    async def event_ready(self):
        # Notify us when everything is ready!
        # We are logged in and ready to chat and use commands...
        self.uptime.start()
        self.display_uptime.start()
        time.sleep(0.5)
        await self.get_channel('0us5ama').send(f'connected at {datetime.now()}')
        print(f'Logged in to {self.channels} as | {self.nick}')

    async def event_message(self, message):
        global nexts, todays, currents, current_jsons
        
        channel_name = message.channel.name
        senders = self.last_senders
        
        try:
            author = message.author.name
        except AttributeError:
            author = 'bot'
                
        if channel_name == 'shakerz_92':
            self.last_senders = last_senders(author, senders)
        if message.echo:
            return
        msg = message.content.lower()
        msg_raw = message.content
        s = msg.split()
        s_raw = msg_raw.split()
        mention = message.tags['display-name']
        channel_name = channel_name if channel_name != '0us5ama' else 'shakerz_92'
        is_mod = message.author.is_mod
        is_vip = 'vip' in message.author.badges.keys()
        user_id = message.author.id
        
        with open(pathing('json', 'timer.json'), "r") as data:
            live = json.load(data)

        if author != 'wizebot' and channel_name == 'shakerz_92':
            messages = live['messages']
            messages += 1
            live['messages'] = messages
            with open(pathing('json', 'timer.json'), "w") as data:
                json.dump(live, data, indent=4)
        
        with open(pathing('json', 'commands.json'), "r") as data:
            cmds = json.load(data)

        cmd_names = cmds[channel_name].keys()

        aliases = {
            cmd: cmds[channel_name][cmd]['aliases']
            for cmd in cmd_names
        }

        arguments = {
            'channel': message.channel,
            'user_id': user_id,
            'mention': mention,
            'channel_name': channel_name,
            'raw_message': msg,
            'message': s,
            'queries': s[1:],
            'short': False
        }
        for comm in aliases.keys():
            built_in = cmds[channel_name][comm]['built-in']
            users = cmds[channel_name][comm]['users']
            levels = users['level']
            excpt = users['except']
            eligible = ((('mods' in levels and is_mod) or
                         ('vips' in levels and is_vip) or 'everyone' in levels)
                        and not user_id in excpt) or ('none' in levels
                                                      and user_id in excpt)
            if eligible:
                if built_in:
                    if s[0] in [f'!{comm}'] + aliases[comm]:
                        command = getattr(helpers, comm)
                        required_args = (arguments[name]
                                         for name in inspect.signature(
                                             command).parameters.keys())
                        return await command(*required_args)
                elif s[0] == comm or s[0] in aliases[comm]:
                    return await message.channel.send(
                        cmds[channel_name][s[0]]['content'])

        if s[0] == '!switch' and author in [channel_name, '0us5ama']:
            day_json = day_jsons[channel_name]
            last = lasts[channel_name]
            last_json = last_jsons[channel_name]
            current = currents[channel_name]
            current_json = current_jsons[channel_name]
            today = todays[channel_name]
            print('yes')
            with open(day_json, "r") as data:
                day = json.load(data)
            day['today'] = (datetime.strptime(day['today'], '%d/%m/%Y') +
                            timedelta(days=1)).strftime("%d/%m/%Y")
            next = nexts[channel_name] = day['today']
            today = todays[channel_name] = datetime.strptime(
                next, '%d/%m/%Y').strftime("%d_%m_%Y")
            current = currents[channel_name] = pathing(f"static/{channel_name}", f"spin_{today}.txt")
            current_json = current_jsons[channel_name] = pathing(f"static/{channel_name}", f"spin_{today}.json")

            with open(day_json, "w") as data:
                json.dump(day, data)

            with open(last, "w") as f:
                pass
            with open(current, "a") as f:
                pass
            with open(current_json, "w") as f:
                f.write(json.dumps({}))

            await message.channel.send('switched to tomorrow')

            with open(pathing(f"static/{channel_name}", 'reward.json'), "r") as data:
                data = json.load(data)
            reward_id = data['reward_id']

            with open(last_json, "r") as data:
                rewards = json.load(data)
            with open(last_json, "w") as f:
                f.write(json.dumps({}))
            rewards = rewards.values()
            # ids = [ reward['reward_id'] for reward in rewards if reward['reward_id']]
            users_oauth_token = users_oauth_tokens[channel_name]
            users_channel_id = users_channel_ids[channel_name]
            for reward in rewards:
                id = reward['reward_id']
                user = reward['user']
                change_reward_status(CLIENT_ID, users_oauth_token,
                                        users_channel_id, reward_id, id,
                                        "FULFILLED")
        elif s[0] in ['واسطة؟', 'واسطه؟'] and len(s) > 1 and author in [channel_name, '0us5ama']:
            user = s_raw[1].replace('@', '')
            try:
                resp = requests.get(
                    f"https://api.twitch.tv/helix/users?login={user}",
                    headers=headers).json()['data'][0]
                user_id = resp['id']
                user = resp['display_name']
            except (AttributeError, IndexError):
                return await message.channel.send('مين ذا؟')
            last = lasts[channel_name]
            last_json = last_jsons[channel_name]
            current = currents[channel_name]
            current_json = current_jsons[channel_name]
            with open(last_json, "r") as participants:
                users = json.load(participants)
            if not user_id in users.keys():
                with open(last, "a") as f:
                    f.write(user + '\n')
                with open(current, "a") as f:
                    f.write(user + '\n')
                participant = {
                    "user": user,
                    "reward_id": 0,
                    "time": 0,
                    "mode": 'cheat'
                }
                with open(current_json, 'r+') as data:
                    # First we load existing data into a dict.
                    try:
                        file_data = json.load(data)
                    except ValueError:
                        file_data = {}
                    # Join new_data with file_data inside emp_details
                    file_data[user_id] = participant
                    # Sets file's current position at offset.
                    data.seek(0)
                    # convert back to json.
                    json.dump(file_data, data, indent=4)
                with open(last_json, "w") as data:
                    json.dump(file_data, data, indent=4)
                await message.channel.send(f"{user} entered wastah!")
            else:
                await message.channel.send(f"{user} is already in, mayhtaj!")
        elif s[0] in ['!win'] and len(s) > 1 and author in [channel_name, '0us5ama']:
            user = s_raw[1].replace('@', '')
            try:
                resp = requests.get(
                    f"https://api.twitch.tv/helix/users?login={user}",
                    headers=headers).json()['data'][0]
                user_id = int(resp['id'])
                user = resp['display_name']
            except (AttributeError, IndexError, KeyError):
                return await message.channel.send('مين ذا؟')
            with open(
                    pathing(f"static/{channel_name}", 'black_list.json'),
                    "r") as data:
                black_list = json.load(data)
            if not user_id in black_list.values():
                black_list[user] = user_id
                with open(
                        pathing(f"static/{channel_name}",
                                    'black_list.json'), "w") as data:
                    json.dump(black_list, data, indent=4)
                await message.channel.send(f"{user} added to the winners' list"
                                        )
            else:
                await message.channel.send(f"{user} is already in the list")
        elif s[0] in ['براع؟'] and len(s) > 1 and author in [channel_name, '0us5ama']:
            user = s_raw[1].replace('@', '')
            try:
                resp = requests.get(
                    f"https://api.twitch.tv/helix/users?login={user}",
                    headers=headers).json()['data'][0]
                user_id = resp['id']
                user = resp['display_name']
            except (AttributeError, IndexError, KeyError):
                return await message.channel.send('مين ذا؟')
            last = lasts[channel_name]
            last_json = last_jsons[channel_name]
            current = currents[channel_name]
            current_json = current_jsons[channel_name]
            with open(last_json, "r") as participants:
                users = json.load(participants)
            if user_id in users.keys():
                if users[user_id]['mode'] == 'cheat':
                    file = open(last, "r")
                    data = file.read().strip().split('\n')
                    data.remove(users[user_id]['user'])
                    with open(current, "w") as f:
                        f.write('\n'.join(data) + '\n')
                    with open(last, "w") as f:
                        f.write('\n'.join(data) + '\n')
                    with open(current_json, "r") as data:
                        file_data = json.load(data)
                    with open(current_json, "w") as data:
                        del file_data[user_id]
                        json.dump(file_data, data, indent=4)
                    with open(last_json, "w") as data:
                        json.dump(file_data, data, indent=4)
                    await message.channel.send(f"{user} براااااااااااااع")
                else:
                    await message.channel.send(f"ما يمديك {user} دافع فلووس")
            else:
                await message.channel.send(f"{user} مو موجود أصلا Kappa")
        elif s[0] == 'add?' and author != 'creeper_r77':
            try:
                if s[2] == 'bits' or s[2] == 'bit' or s[2] == 'cheers' or s[
                        2] == 'cheer':
                    await message.channel.send(
                        to_time(mention, s, 140 / 100, 'bits value'))
                elif s[2] == 'dono' or s[2] == 'donation' or s[
                        2] == 'dollar' or s[2] == 'dollars':
                    await message.channel.send(
                        to_time(mention, s, 120, 'dono value'))
                elif s[2] == 'subs' or s[2] == 'sub' or s[2] == 'gifts' or s[
                        2] == 'gift':
                    await message.channel.send(
                        to_time(mention, s, 250, 'number of gift subs'))
            except IndexError:
                await message.channel.send(
                    f'{mention}, add? amount (bit-cheer/dono-dollar/sub-gift)')
        elif s[0] == 'ضيف؟' and author != 'creeper_r77':
            try:
                if s[2] == 'بيتس' or s[2] == 'بيت' or s[2] == 'بت' or s[
                        2] == 'بتس':
                    await message.channel.send(
                        to_time(mention, s, 140 / 100, 'bits value'))
                elif s[2] == 'دونو' or s[2] == 'دونيشن' or s[2] == 'دولار':
                    await message.channel.send(
                        to_time(mention, s, 120, 'dono value'))
                elif s[2] == 'سابز' or s[2] == 'ساب' or s[2] == 'قيفتس' or s[
                        2] == 'قيفت':
                    await message.channel.send(
                        to_time(mention, s, 250, 'number of gift subs'))
            except IndexError:
                await message.channel.send(
                    f'{mention}, ضيف؟ كمية (بيت-بيتس-بت-بتس/دونو-دونيشن/ساب-سابز-قيفت-قيفتس)'
                )
        elif s[0] == '!time-diff':
            s1 = s[1]
            s2 = s[2]
            FMT = '%H:%M'
            await message.channel.send(
                str(datetime.strptime(s2, FMT) - datetime.strptime(s1, FMT)))
        await self.handle_commands(message)
    
    # @routines.routine(seconds=3653, wait_first=True)
    @routines.routine(seconds=1817, wait_first=True)
    async def uptime(self):
        self.ready = True
        # await self.get_channel('shakerz_92').send(uptime)
    
    @routines.routine(seconds=1)
    async def display_uptime(self):
        self.time = await get_uptime(channel=None,
                                     short=True,
                                     channel_name='shakerz_92')
        ready = self.ready
        senders = self.last_senders
        if ready and 'bot' not in senders:
            await self.get_channel('shakerz_92').send(self.time)
            self.ready = False

client = twitchio.Client(token=my_token)

client.pubsub = pubsub.PubSubPool(client)

@client.event()
async def event_pubsub_bits(event: pubsub.PubSubBitsMessage):
    pass  # do stuff on bit redemptions


@client.event()
async def event_pubsub_channel_points(
        event: pubsub.PubSubChannelPointsMessage):
    user = event.user.name
    print(event.reward.title, user)
    reward_id = event.reward.id
    channel_name = requests.get(
        f"https://api.twitch.tv/helix/users?id={event.channel_id}",
        headers=headers).json()['data'][0]['login']
    with open(pathing(f"static/{channel_name}", 'reward.json'),
              "r") as data:
        reward = json.load(data)
    if event.reward.title == reward['title']:
        reward_id = event.reward.id
        id = event.id
        user_id = event.user.id
        with open(last_jsons[channel_name], "r") as participants:
            users = json.load(participants)
        # with open(pathing('static', 'black_list.json'), "r") as data:
        #     black_list = json.load(data)
        if not str(user_id) in users.keys():
            with open(lasts[channel_name], "a") as f:
                f.write(user + '\n')
            with open(currents[channel_name], "a") as g:
                g.write(user + '\n')
            participant = {
                "user": user,
                "reward_id": id,
                "time": str(event.timestamp),
                "mode": 'normal'
            }
            with open(current_jsons[channel_name], "r+") as data:
                try:
                    file_data = json.load(data)
                except ValueError:
                    file_data = {}
                file_data[user_id] = participant
                # Sets file's current position at offset.
                data.seek(0)
                # convert back to json.
                json.dump(file_data, data, indent=4)
            with open(last_jsons[channel_name], "w") as data:
                json.dump(file_data, data, indent=4)
        else:
            change_reward_status(CLIENT_ID, users_oauth_tokens[channel_name],
                                 users_channel_ids[channel_name], reward_id,
                                 id, "CANCELED")
    
async def main():
    topics = [
        pubsub.channel_points(
            users_oauth_tokens[channel])[users_channel_ids[channel]]
        for channel in channels
    ]
    print(topics)
    await client.pubsub.subscribe_topics(topics)
    await client.start()
    print(f"connected to {channels}")