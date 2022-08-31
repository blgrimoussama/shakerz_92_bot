from quart import render_template
import requests, json

async def apology(message, code=400):
    """Render message as an apology to user."""
    def escape(s):
        """
        Escape special characters.
        https://github.com/jacebrowning/memegen#special-characters
        """
        for old, new in [("-", "--"), (" ", "-"), ("_", "__"), ("?", "~q"),
                         ("%", "~p"), ("#", "~h"), ("/", "~s"), ("\"", "''")]:
            s = s.replace(old, new)
        return s
    return await render_template("apology.html", top=escape(message), bottom=code), code

def change_reward_status(client_id, channel_token, broadcaster_id, reward_id, id,status):
    headers = {'Client-Id': client_id, 
           'Authorization': 'Bearer ' + channel_token, 
           'Content-type': 'application/json'}
    params = {'broadcaster_id': broadcaster_id, 
              'reward_id': reward_id, 
              'id': id}
    raw_data = json.dumps({"status": status})
    r = requests.patch(                'https://api.twitch.tv/helix/channel_points/custom_rewards/redemptions', headers=headers, params=params, data=raw_data)
    return r.status_code
    