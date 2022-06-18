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
    self.winner = None
    self.round = 0
    self.ended = False

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
      jstr = {'playfield': self.tiles, 'myTurn': player.my_turn, 'started': True, 'mark': player.mark}
      await player.socket.send(json.dumps(jstr))

  async def update_playfield(self):
    winner = ''
    if self.round == self.width*self.height:
      self.ended = True

    if self.winner != None:
      winner = self.winner.id

    player: Player
    for player in self.players:
      jstr = {'playfield': self.tiles, 'myTurn': player.my_turn, 'winner': winner, 'ended': self.ended}
      await player.socket.send(json.dumps(jstr))
      
    self.broadcast_update = False

  def check_board(self):
    field = self.tiles

    # check rows
    for i in range(0, self.width*self.height, 3):
      if field[i] == field[i+1] and field[i] == field[i+2] and len(field[i]) > 0:
        self.ended = True
        return field[i]
    
    # check cols
    for i in range(0, self.width):
      if field[i] == field[i+3] and field[i] == field[i+6] and len(field[i]) > 0:
        self.ended = True
        return field[i]

    # check diagonals
    if field[0] == field[4] and field[0] == field[8] and len(field[i]) > 0:
      self.ended = True
      return field[0]
    if field[2] == field[4] and field[2] == field[6] and len(field[i]) > 0:
      self.ended = True
      return field[2]

    return None


  def set_tile(self, player_id, tile_id):
    player: Player
    player = list(filter(lambda x: x.id == player_id, self.players))[0]
    if player.my_turn and self.started and not self.ended:
      self.tiles[tile_id] = player.mark
      player.my_turn = False
      player_2 = list(filter(lambda x: x.id != player_id, self.players))[0]
      player_2.my_turn = True
      
      self.broadcast_update = True
      self.round += 1

      winner = self.check_board()
      if winner != None:
        self.winner = player


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