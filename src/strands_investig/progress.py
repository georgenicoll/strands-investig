from strands_evals import EvalTaskHandler


class ProgressTaskHandler(EvalTaskHandler):
    """EvalTaskHandler that prints a line as each case's task starts/finishes.

    Experiment.run_evaluations gives no built-in progress signal, so this
    taps the only hook it does call per case: the @eval_task handler.
    """

    def __init__(self, total: int):
        self._total = total
        self._done = 0

    def before(self, case) -> None:
        print(f"[{self._done}/{self._total}] running case: {case.name}")

    def after(self, case, result):
        self._done += 1
        print(f"[{self._done}/{self._total}] finished case: {case.name}")
        return super().after(case, result)


def with_judge_progress(evaluator, total: int):
    """Make an evaluator instance print progress around its judge calls.

    Experiment calls `evaluator.evaluate_async` directly with no progress hook.
    Assigning a wrapper straight onto the instance (`evaluator.evaluate_async = ...`)
    would work too, but `Evaluator.to_dict()` serializes every non-underscore
    attribute in `self.__dict__`, so that function would get serialized and crash
    `Experiment.to_file()`. Swapping in a one-off subclass instead overrides the
    method on the class, keeping `__dict__` (and `to_dict()`/`to_file()`) clean.
    """
    original_cls = type(evaluator)

    class _ProgressEvaluator(original_cls):
        async def evaluate_async(self, evaluation_case):
            print(f"  judging case: {evaluation_case.name}")
            result = await super().evaluate_async(evaluation_case)
            self._progress_done = getattr(self, "_progress_done", 0) + 1
            print(f"  [{self._progress_done}/{total}] judged case: {evaluation_case.name}")
            return result

    # get_type_name()/get_name() report cls.__name__; keep it matching the
    # original class so display, to_dict() and from_dict() registry lookups
    # still see "OutputEvaluator" rather than "_ProgressEvaluator".
    _ProgressEvaluator.__name__ = original_cls.__name__
    _ProgressEvaluator.__qualname__ = original_cls.__qualname__

    evaluator.__class__ = _ProgressEvaluator
    return evaluator
