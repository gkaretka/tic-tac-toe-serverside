import asyncio
import json
import random
from websockets import serve


MAX_NUMBER_OF_PLAYERS = 2

playfields = []

class Player:
  def __init__(self, id, socket, mark) -> None:
    self.my_turn = False
    self.id = id
    self.socket = socket
    self.mark = mark

class Playfield:
  def __init__(self) -> None:
    self.name = format(random.getrandbits(128), 'x')
    self.tiles = []
    self.players = []
    self.free = True
    self.started = False
    self.broadcast_update = False

    self.width = 3
    self.height = 3

    for i in range(self.width*self.height):
      self.tiles.append('')

  def add_player(self, player_id, websocket):
    mark = random.choice(['O', 'X'])
    if len(self.players) > 0:
      mark = 'O' if self.players[0].mark == 'X' else 'X'
    
    player = Player(player_id, websocket, mark)
    if mark == 'X':
      player.my_turn = True

    self.players.append(player)

    if len(self.players) >= MAX_NUMBER_OF_PLAYERS:
      self.free = False

  async def start_game(self):    
    self.started = True
    player: Player
    for player in self.players:
      jstr = {'playfield': self.tiles, 'myTurn': player.my_turn}
      await player.socket.send(json.dumps(jstr))

  async def update_playfield(self):
    player: Player
    for player in self.players:
      jstr = {'playfield': self.tiles, 'myTurn': player.my_turn}
      print(self.tiles)
      await player.socket.send(json.dumps(jstr))
      
    self.broadcast_update = False

  def set_tile(self, player_id, tile_id):
    player: Player
    player = list(filter(lambda x: x.id == player_id, self.players))[0]
    if player.my_turn == True:
      self.tiles[tile_id] = player.mark
      player.my_turn = False
      player_2 = list(filter(lambda x: x.id != player_id, self.players))[0]
      player_2.my_turn = True
      self.broadcast_update = True

async def game(websocket):
    async for message in websocket:
      data = json.loads(message)

      if 'id' in data and 'type' in data:
        id = data['id']
        type = data['type']

        if type == 'regPlayer':
          if len(playfields) == 0:
            pf = Playfield()
            pf.add_player(id, websocket)
            print("Adding to ", pf.name)
            playfields.append(pf)
          else:
            pf: Playfield

            added = False
            for pf in playfields:
              if pf.free:
                print("Adding to ", pf.name)
                pf.add_player(id, websocket)
                added = True
                break

            if not added:
              pf = Playfield()
              pf.add_player(id, websocket)
              print("Adding to ", pf.name)
              playfields.append(pf)

        elif type == 'setTile':
          for i in range(len(playfields)):
            for pl in playfields[i].players:
              if id in pl.id:
                playfields[i].set_tile(id, data['tileId'])

      for i in range(len(playfields)):
        if not playfields[i].free and not playfields[i].started:
          await playfields[i].start_game()
        if playfields[i].broadcast_update:
          print("updating", playfields[i].name)
          await playfields[i].update_playfield()


async def main():
    async with serve(game, "localhost", 8080):
        await asyncio.Future()  # run forever

asyncio.run(main())