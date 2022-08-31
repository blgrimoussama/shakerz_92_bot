from math import *
import os
import json

DIRNAME = '//'.join(os.path.dirname(__file__).split("/"))

env = {}
env["locals"]   = None
env["globals"]  = None
env["__name__"] = None
env["__file__"] = None
env["__builtins__"] = {
    'pi': pi,
    'e': e,
    'ceil': ceil,
    'floor': floor,
    'cos': cos,
    'sin': sin,
    'tan': tan,
    'sqrt': sqrt,
    'pow': pow,
    'exp': exp,
    'log': log
}
with open(os.path.join(f'{DIRNAME}/json', 'invalid_characters.json'), "r") as data:
    invalid_calc = json.load(data)


async def calculate(channel, mention, message):
    output = ''
    try:
        expression = ''.join(message[1:])
        for ele in expression:
            if ele in invalid_calc.keys():
                expression = expression.replace(ele, invalid_calc[ele])
        expression = expression.replace("mod", invalid_calc["mod"])
        value = str(round(eval(expression, env), 3))
        value = value[:-2] if value.endswith('.0') else value
        output = value
    except (SyntaxError, TypeError, NameError):
        output = f'{mention}, check your input and try again'
    except ZeroDivisionError:
        output = f"{mention}, can't devide by zero!"
    return await channel.send(output)