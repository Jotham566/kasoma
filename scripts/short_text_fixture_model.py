"""Deterministic reviewed-label fixture; never imported by normal runtime entry points."""

import json

from services.providers import FakeModelProvider, ModelResult, ModelTask


class SyntheticRubricModel(FakeModelProvider):
    def execute(self, task: ModelTask) -> ModelResult:
        super().execute(task)
        context = task.structured_input["rubric"]
        if (
            not isinstance(context, dict)
            or str(task.structured_input["response"]).strip() != "Alpha"
        ):
            return ModelResult(status="LOW_CONFIDENCE", provider="fake", model="fixture-v1")
        next_actions = context.get("next_actions")
        if not isinstance(next_actions, list) or not next_actions:
            raise ValueError("Synthetic reviewed next action missing")
        return ModelResult(
            status="CANDIDATE",
            provider="fake",
            model="fixture-v1",
            input_tokens=100,
            output_tokens=100,
            raw_output=json.dumps(
                {
                    "criterion_results": [
                        {
                            "criterion_id": "R1",
                            "points_awarded": 1,
                            "evidence_excerpt": "Alpha",
                            "justification_code": "SUPPORTED",
                        }
                    ],
                    "total_points": 1,
                    "confidence": 0.97,
                    "detected_misconception_ids": [],
                    "feedback": {
                        "correct_elements": context["correct_elements"],
                        "missing_elements": [],
                        "next_action": next_actions[0],
                    },
                }
            ),
        )
