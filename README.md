# teeko_ai_player

### Details
This is a project from Introduction to Artificial Intelligence, which I took in the fall of my senior year (2024). Teeko is a tile game with two players. Each player takes turns dropping one of their 4 tiles on a 5x5 grid, aiming to line their tiles up in a straight or horizontal line, or a 2x2 box. If neither player achieves this goal by the end of the drop phase, they take turns moving a tile to an adjacent space, until someone has reached the win condition. My code uses a static evaluation function to efficiently implement a minimax algorithm. The professor provided the UI and flow of execution, while I determined the heuristic and applied it to the current game state with an iterative deepening search so that the AI makes intelligent moves within a specified time constraint.

### How to run this code
Clone this repository. Assuming the environment has been properly configured, run ```python game.py``` to begin playing against the AI.
