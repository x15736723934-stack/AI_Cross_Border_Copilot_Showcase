import unittest

from profit_calculator import ProfitInput, calculate
from workflow_demo import ProjectInput, STEPS, new_run, run_next


class ProfitTests(unittest.TestCase):
    def test_reference_formula(self):
        result = calculate(ProfitInput(29.99, 8.0, 2.5, 15.0, 3.5, 0.0, 0.0))
        self.assertAlmostEqual(result.profit, 11.4915, places=4)
        self.assertAlmostEqual(result.break_even_acos, 38.3178, places=4)


class WorkflowTests(unittest.TestCase):
    def test_all_steps_are_traceable(self):
        state = new_run(ProjectInput("demo", "grinder", "Amazon", "US", 29.99))
        for _ in STEPS:
            state = run_next(state)
        self.assertEqual(state["status"], "completed")
        self.assertEqual(state["progress"], 100)
        self.assertEqual(len(state["events"]), len(STEPS))
        self.assertEqual(set(state["completed_steps"]), {key for key, _ in STEPS})


if __name__ == "__main__":
    unittest.main()
