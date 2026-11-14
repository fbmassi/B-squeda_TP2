"""Pruebas de los cuatro algoritmos con grafos pequenos y costos conocidos."""

from collections import Counter
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'pacman'))
import search


ALGORITHMS = (search.dfs, search.bfs, search.ucs, search.astar)


class GraphProblem(search.SearchProblem):
    def __init__(self, edges, start='S', goal='G'):
        self.edges = edges
        self.start = start
        self.goal = goal
        self.expanded = Counter()

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state == self.goal

    def getSuccessors(self, state):
        self.expanded[state] += 1
        # Fail early if a cycle causes repeated expansion indefinitely.
        if sum(self.expanded.values()) > 100:
            raise AssertionError('Demasiadas expansiones en un grafo pequeno')
        return self.edges.get(state, [])

    def follow(self, actions):
        state, cost = self.start, 0
        for action in actions:
            matches = [edge for edge in self.edges.get(state, [])
                       if edge[1] == action]
            if len(matches) != 1:
                raise AssertionError('Accion ilegal o ambigua: ' + str(action))
            state, _, step_cost = matches[0]
            cost += step_cost
        return state, cost

    def getCostOfActions(self, actions):
        return self.follow(actions)[1]


class SearchTests(unittest.TestCase):
    def assertSolution(self, problem, actions, cost=None):
        self.assertIsInstance(actions, list)
        end, actual_cost = problem.follow(actions)
        self.assertTrue(problem.isGoalState(end))
        if cost is not None:
            self.assertEqual(actual_cost, cost)

    def test_legal_paths_and_cycles(self):
        edges = {'S': [('A', 'sa', 1), ('B', 'sb', 1)],
                 'A': [('S', 'as', 1), ('B', 'ab', 1)],
                 'B': [('A', 'ba', 1), ('G', 'bg', 1)]}
        for algorithm in ALGORITHMS:
            with self.subTest(algorithm=algorithm.__name__):
                problem = GraphProblem(edges)
                self.assertSolution(problem, algorithm(problem))
                self.assertTrue(all(n == 1 for n in problem.expanded.values()))

    def test_initial_state_is_goal(self):
        for algorithm in ALGORITHMS:
            with self.subTest(algorithm=algorithm.__name__):
                problem = GraphProblem({'S': [('A', 'sa', 1)]}, goal='S')
                self.assertEqual(algorithm(problem), [])
                self.assertEqual(sum(problem.expanded.values()), 0)

    def test_unreachable_goal_with_cycle(self):
        for algorithm in ALGORITHMS:
            with self.subTest(algorithm=algorithm.__name__):
                problem = GraphProblem({'S': [('A', 'sa', 1)],
                                        'A': [('S', 'as', 1)]})
                self.assertEqual(algorithm(problem), [])
                self.assertEqual(dict(problem.expanded), {'S': 1, 'A': 1})

    def test_dead_end(self):
        for algorithm in ALGORITHMS:
            with self.subTest(algorithm=algorithm.__name__):
                self.assertEqual(algorithm(GraphProblem({})), [])

    def test_dfs_uses_lifo(self):
        problem = GraphProblem({'S': [('G', 'direct', 1), ('A', 'sa', 1)],
                                'A': [('G', 'ag', 1)]})
        self.assertEqual(search.dfs(problem), ['sa', 'ag'])

    def test_bfs_minimum_number_of_actions(self):
        problem = GraphProblem({'S': [('A', 'sa', 1), ('B', 'sb', 1)],
                                'A': [('C', 'ac', 1)],
                                'C': [('G', 'cg', 1)],
                                'B': [('G', 'bg', 1)]})
        self.assertEqual(search.bfs(problem), ['sb', 'bg'])

    def test_cost_optimum_differs_from_shortest_path(self):
        edges = {'S': [('G', 'direct', 10), ('A', 'sa', 1)],
                 'A': [('B', 'ab', 1)], 'B': [('G', 'bg', 1)]}
        problem = GraphProblem(edges)
        self.assertEqual(search.bfs(problem), ['direct'])
        for algorithm in (search.ucs, search.astar):
            with self.subTest(algorithm=algorithm.__name__):
                problem = GraphProblem(edges)
                self.assertSolution(problem, algorithm(problem), cost=3)

    def test_improved_cost_to_frontier_state(self):
        edges = {'S': [('A', 'expensive', 5), ('B', 'sb', 1)],
                 'B': [('A', 'ba', 1)], 'A': [('G', 'ag', 1)]}
        for algorithm in (search.ucs, search.astar):
            with self.subTest(algorithm=algorithm.__name__):
                problem = GraphProblem(edges)
                actions = algorithm(problem)
                self.assertEqual(actions, ['sb', 'ba', 'ag'])
                self.assertSolution(problem, actions, cost=3)

    def test_obsolete_entries_are_not_expanded(self):
        edges = {'S': [('A', 'expensive', 5), ('B', 'sb', 1)],
                 'B': [('A', 'ba', 1)], 'A': [('G', 'ag', 10)]}
        for algorithm in (search.ucs, search.astar):
            with self.subTest(algorithm=algorithm.__name__):
                problem = GraphProblem(edges)
                self.assertSolution(problem, algorithm(problem), cost=12)
                self.assertEqual(problem.expanded['A'], 1)

    def test_zero_cost_cycle(self):
        edges = {'S': [('A', 'sa', 0)],
                 'A': [('S', 'as', 0), ('G', 'ag', 2)]}
        for algorithm in (search.ucs, search.astar):
            with self.subTest(algorithm=algorithm.__name__):
                problem = GraphProblem(edges)
                self.assertSolution(problem, algorithm(problem), cost=2)
                self.assertEqual(problem.expanded['S'], 1)

    def test_astar_admissible_inconsistent_heuristic_reopens_state(self):
        edges = {'S': [('A', 'sa', 3), ('B', 'sb', 1)],
                 'B': [('A', 'ba', 1)], 'A': [('G', 'ag', 3)]}
        # h(B)=4 is exact but inconsistent: h(B) > cost(B,A)+h(A).
        h = {'S': 0, 'A': 0, 'B': 4, 'G': 0}
        problem = GraphProblem(edges)
        calls = []

        def heuristic(state, received_problem):
            self.assertIs(received_problem, problem)
            calls.append(state)
            return h[state]

        actions = search.astar(problem, heuristic)
        self.assertSolution(problem, actions, cost=5)
        self.assertEqual(actions, ['sb', 'ba', 'ag'])
        self.assertEqual(problem.expanded['A'], 2)
        self.assertIn('B', calls)

    def test_null_heuristic_matches_ucs(self):
        edges = {'S': [('A', 'sa', 8), ('B', 'sb', 2)],
                 'B': [('A', 'ba', 1), ('G', 'bg', 20)],
                 'A': [('G', 'ag', 4)]}
        ucs_problem, astar_problem = GraphProblem(edges), GraphProblem(edges)
        ucs_actions = search.ucs(ucs_problem)
        astar_actions = search.astar(astar_problem, search.nullHeuristic)
        self.assertSolution(ucs_problem, ucs_actions, cost=7)
        self.assertSolution(astar_problem, astar_actions, cost=7)
        self.assertEqual(ucs_problem.expanded, astar_problem.expanded)

    def test_aliases(self):
        for alias, function in [('dfs', 'depthFirstSearch'),
                                ('bfs', 'breadthFirstSearch'),
                                ('ucs', 'uniformCostSearch'),
                                ('astar', 'aStarSearch')]:
            self.assertIs(getattr(search, alias), getattr(search, function))


if __name__ == '__main__':
    unittest.main()
