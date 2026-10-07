import asyncio

from strands import Agent
from strands_evals import Experiment, eval_task
from strands_evals.evaluators import OutputEvaluator
from strands_evals.generators import ExperimentGenerator

from .openrouter import openrouter_model
from .progress import ProgressTaskHandler, with_judge_progress
from .tools import calculator, current_time

TASK_DESCRIPTION = "Math and time assistant"
CONTEXT = """
Available tools:
- calculator(expression: str) -> float: Evaluate mathematical expressions
- current_time() -> str: Get current date and time
"""


async def _generate_experiment() -> Experiment:
    generator = ExperimentGenerator[str, str](
        input_type=str,
        output_type=str,
        include_expected_output=True,
        model=openrouter_model(),
    )

    print("Generating test cases...")
    cases = await generator.generate_cases_async(
        f"Create test cases with the following context: {CONTEXT}. Ensure that the questions can "
        f"be answered using the provided context for this task: {TASK_DESCRIPTION} ",
        num_cases=5,
    )

    print(f"\nGenerated {len(cases)} test cases:\n")
    for i, case in enumerate(cases, start=1):
        print(f"[{i}/{len(cases)}] {case.name}")
        print(f"    input:           {case.input}")
        print(f"    expected_output: {case.expected_output}\n")

    print("Generating rubric...")
    evaluator = await generator.construct_evaluator_async(
        prompt=f"Create a rubric with the following context: {CONTEXT} for this task: {TASK_DESCRIPTION} ",
        evaluator=OutputEvaluator,
    )
    # construct_evaluator_async only sets `rubric`; point the judge at OpenRouter too,
    # otherwise OutputEvaluator falls back to its Bedrock default.
    evaluator.model = openrouter_model()
    print(f"Rubric:\n{evaluator.rubric}\n")

    return Experiment(cases=cases, evaluators=[evaluator])


def run() -> None:
    experiment = asyncio.run(_generate_experiment())

    task_handler = ProgressTaskHandler(total=len(experiment.cases))

    @eval_task(task_handler)
    def get_response():
        return Agent(
            model=openrouter_model(),
            system_prompt=f"You are a {TASK_DESCRIPTION.lower()}.",
            tools=[calculator, current_time],
            callback_handler=None,
        )

    with_judge_progress(experiment.evaluators[0], total=len(experiment.cases))

    print("Running evaluations...\n")
    report = experiment.run_evaluations(get_response)

    print("\n=== Generated Experiment Evaluation Results ===")
    report.run_display()

    experiment.to_file("generated_experiment")
    print("\nExperiment saved to ./generated_experiment.json")
