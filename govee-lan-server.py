from flask import Flask, json, request
from govee_lan_api import GoveeClient
import asyncio
import logging

initial_config = { "port": 3666,
                   "device_map": {} } # default, can be overridden in config
VALID_ACTIONS = ['on', 'off', 'brightness', 'color'];
DEBUG_MODE=False

if DEBUG_MODE:
    logging.basicConfig(level=logging.DEBUG)

# Read config
f = open('config.json')
config_override = json.load(f)
config = initial_config | config_override
print(config)
devices = config['device_map']
f.close()

def parse_color_tuple(value):
  val = value.lstrip('#')
  return tuple(int(val[i:i+2], 16) for i in (0, 2, 4))
 

async def handler(client, target_device, action, value):
    match action:
      case 'on': return await client.turn_on(target_device)
      case 'off': return await client.turn_off(target_device)
      case 'brightness': 
          brightness = 100
          if value != "":
              brightness = value
          return await client.set_brightness(target_device, int(brightness))
      case 'color': 
          color = (255, 255, 255)
          if value != "":
              color = parse_color_tuple(args['value'])
          return await client.set_color_by_rgb(target_device, color)
      case 'scan':
          return await client.scan_devices()

# Setup client
client = GoveeClient()
asyncio.run(client.scan_devices())

# Setup API ... we don't really do fancy routing, but let query params drive it
api = Flask(__name__)
@api.route('/', defaults={'path': ''}, methods=['GET'])
def catch_all(path):
  args = request.args
  target_device = ''
  if 'device' in args:
      if args['device'] in devices:
         target_device = devices[args['device']]
      else:
         target_device = args['device']
  
      if 'action' in args and args['action'] in VALID_ACTIONS:
         val = ''
         if 'value' in args:
           val = args['value']
         asyncio.run(handler(client, target_device, args['action'], val))
         return json.dumps({ "request": args['action'] + " " + args['device'] + " " + val}), 200
      else:
         return json.dumps({ "message": "query must specify an action (on, off, brightness, color)"}), 400
  else:
      return json.dumps({ "message": "query must specify a device by ID (or nickname from the config map)" }), 400

if __name__ == '__main__':
    api.run(port = config['port'])


