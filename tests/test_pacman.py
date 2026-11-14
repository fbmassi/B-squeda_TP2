"""Integracion con el motor, los laberintos y los agentes docentes originales."""

from contextlib import redirect_stdout
import io
import os
from pathlib import Path
import subprocess
import sys
import unittest

PACMAN_DIR = Path(__file__).resolve().parents[1] / 'pacman'
sys.path.insert(0, str(PACMAN_DIR))
import pacman
import layout
import search
import searchAgents


class PacmanTests(unittest.TestCase):
    def setUp(self):
        self.previous_dir = Path.cwd()
        os.chdir(PACMAN_DIR)
        self.addCleanup(os.chdir, self.previous_dir)

    def play(self, maze, agent='SearchAgent', arguments=None):
        command = ['-l', maze, '-p', agent, '-q', '-f']
        if arguments:
            command.extend(['-a', arguments])
        with redirect_stdout(io.StringIO()):
            options = pacman.readCommand(command)
            games = pacman.runGames(**options)
        self.assertEqual(len(games), 1)
        self.assertTrue(games[0].state.isWin())
        self.assertFalse(games[0].agentCrashed)
        return options['pacman'].actions

    def test_four_algorithms_in_three_mazes(self):
        for maze, optimum in [('tinyMaze', 8), ('mediumMaze', 68), ('bigMaze', 210)]:
            for algorithm in ['dfs', 'bfs', 'ucs', 'astar']:
                with self.subTest(maze=maze, algorithm=algorithm):
                    arguments = 'fn=' + algorithm
                    if algorithm == 'astar':
                        arguments += ',heuristic=manhattanHeuristic'
                    actions = self.play(maze, arguments=arguments)
                    if algorithm != 'dfs':
                        self.assertEqual(len(actions), optimum)

    def test_null_heuristic_in_three_mazes(self):
        for maze, optimum in [('tinyMaze', 8), ('mediumMaze', 68), ('bigMaze', 210)]:
            with self.subTest(maze=maze):
                actions = self.play(maze, arguments='fn=astar,heuristic=nullHeuristic')
                self.assertEqual(len(actions), optimum)

    def test_original_weighted_agents(self):
        for maze, agent in [('mediumDottedMaze', 'StayEastSearchAgent'),
                            ('mediumScaryMaze', 'StayWestSearchAgent')]:
            with self.subTest(maze=maze, agent=agent):
                actions = self.play(maze, agent=agent)
                initial = pacman.GameState()
                initial.initialize(layout.getLayout(maze), 0)
                original_agent = getattr(searchAgents, agent)()
                problem = original_agent.searchType(initial)
                bfs_actions = search.bfs(problem)
                self.assertGreater(len(actions), len(bfs_actions))
                self.assertLess(problem.getCostOfActions(actions),
                                problem.getCostOfActions(bfs_actions))

    def test_command_line_entrypoint(self):
        result = subprocess.run(
            [sys.executable, 'pacman.py', '-l', 'tinyMaze', '-p', 'SearchAgent',
             '-a', 'fn=bfs', '-q'], cwd=PACMAN_DIR,
            capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('Win Rate:      1/1', result.stdout)


if __name__ == '__main__':
    unittest.main()
