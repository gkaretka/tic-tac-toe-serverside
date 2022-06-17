import './App.css';
import Game from './components/Game.js'
import Container from 'react-bootstrap/Container'

function App() {
  return (
    <div className="App">
      <body>
        <Container>
          <main className='text-center'>
            <h1>Tic-tac-toe</h1>
            <Game key="game">
            </Game>
          </main>
        </Container>
      </body>
    </div>
  );
}

export default App;
