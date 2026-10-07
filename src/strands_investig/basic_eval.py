from strands import Agent
from strands_evals import Case, Experiment, eval_task
from strands_evals.evaluators import OutputEvaluator

from .openrouter import openrouter_model
from .progress import ProgressTaskHandler, with_judge_progress


def run() -> None:
    test_cases = [
        Case[str, str](
            name="knowledge-1",
            input="What is the capital of France?",
            expected_output="The capital of France is Paris.",
            metadata={"category": "knowledge"}
        ),
        Case[str, str](
            name="knowledge-2",
            input="What is 2 + 2?",
            expected_output="4",
            metadata={"category": "math"}
        ),
        Case[str, str](
            name="reasoning-1",
            input="If it takes 5 machines 5 minutes to make 5 widgets, how long does it take 100 machines to make 100 widgets?",
            expected_output="5 minutes",
            metadata={"category": "reasoning"}
        )
    ]

    task_handler = ProgressTaskHandler(total=len(test_cases))

    @eval_task(task_handler)
    def get_response():
        return Agent(
            model=openrouter_model(),
            system_prompt="You are a helpful assistant that provides accurate information.",
            callback_handler=None,
        )

    evaluator = with_judge_progress(
        OutputEvaluator(
            rubric="""
            Evaluate the response based on:
            1. Accuracy - Is the information factually correct?
            2. Completeness - Does it fully answer the question?
            3. Clarity - Is it easy to understand?

            Score 1.0 if all criteria are met excellently.
            Score 0.5 if some criteria are partially met.
            Score 0.0 if the response is inadequate or incorrect.
            """,
            model=openrouter_model(),
            include_inputs=True
        ),
        total=len(test_cases),
    )

    experiment = Experiment[str, str](cases=test_cases, evaluators=[evaluator])

    print("Running evaluations...\n")
    report = experiment.run_evaluations(get_response)

    print("\n=== Basic Output Evaluation Results ===")
    report.run_display()

    experiment.to_file("basic_evaluation")
    print("\nExperiment saved to ./basic_evaluation.json")
