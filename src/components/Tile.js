import { Component } from "react";
import Button from 'react-bootstrap/Button';
import "../App.css"

class Tile extends Component {
  constructor(props) {
    super(props);
  }

  render() {
    return (
      <Button className="tick-tack-toes" onClick={this.tick}>{this.props.tileValue.length > 0 ? this.props.tileValue : <>&nbsp;</>}</Button>
    );
  }

  reset = () => {
    this.setState({ ticked: false, owner: null });
  }

  tick = () => {
    this.props.updateGame(this.props.id);
  }
}

export default Tile;