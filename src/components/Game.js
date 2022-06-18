import { Component, createRef } from "react";
import Tile from "./Tile.js"
import { Row, Button } from 'react-bootstrap';

class Game extends Component {
  width = 3;
  height = 3;
  tilesRefs = [];
  id = Math.random().toString(36).substring(2);

  constructor(props) {
    super(props);
    this.state = { socketCreated: false, myTurn: false, playfield: [], started: false, winner: null, ended: null, mark: ''};

    let pf = this.state.playfield;
    for (var i = 0; i < this.width*this.height; i++) {
      let newRef = createRef();
      this.tilesRefs.push(newRef);
      pf.push(''); 
    }
    this.setState({ 'playfield': pf });
  }

  componentDidMount = () => {
    if (this.state.socketCreated === true) return;
    this.state.socketCreated = true;

    this.sock = new WebSocket("ws://localhost:8080");

    this.sock.onmessage = evt => { 
      let data = JSON.parse(evt.data);
      this.setState(data);
    };

    this.sock.onopen = () => {
      var msg = {
        type: 'regPlayer',
        id: this.id,
      };
      this.sock.send(JSON.stringify(msg));
    }
  }

  updateGame = (tile_id) => {
    let jmsg = {
      'id': this.id,
      'type': 'setTile',
      'tileId': tile_id,
    };

    this.sock.send(JSON.stringify(jmsg));
  }

  render = () => {
    let tiles = [];

    for (var j = 0; j < this.width; j++) {
      let partTiles = []
      for (var i = 0; i < this.height; i++) {
        partTiles.push(<Tile ref={this.tilesRefs[j*3+i]} id={(j * this.width) + i} updateGame={this.updateGame} tileValue={this.state.playfield[j*3+i]}>i</Tile>)
      }

      tiles.push(<Row> {partTiles} </Row>);
    }

    let state_msg = <h1>Waiting for oponent</h1>;
    if (this.state.started) {
      state_msg = <h1>Game started it is : { this.state.myTurn ? "your turn" : "oponent's turn" }.</h1>
    }

    if (this.state.ended === true) {
      state_msg = <h1>Game ended, {this.id === this.state.winner ? 'you won!' : this.state.winner == '' ? 'it\'s tie!' : 'you lost!'}</h1>
    }

    let playingAs = <h1>Playing as {this.state.mark}</h1>
    
    return (
      <div>
        {tiles}
        {state_msg}
        {playingAs}
      </div>
    );
  }
}

export default Game;