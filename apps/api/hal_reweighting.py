from __future__ import annotations

from dataclasses import asdict, dataclass

from .hal_complexity import build_hal_complexity_decision
from .hal_feedback import build_hal_feedback_summary


@dataclass(frozen=True)
class HALDecisionReweighting:
    current_path: str
    path_confidence: float | None
    decision: str
    reason: str
    should_escalate: bool
    should_hold_current_path: bool
    recommended_action: str


def build_hal_decision_reweighting() -> HALDecisionReweighting:
    complexity = build_hal_complexity_decision()
    feedback = build_hal_feedback_summary(limit=200)
    current_path = complexity.selected_path

    matching_path = None
    for item in feedback.get('paths', []):
        if item.get('selected_path') == current_path:
            matching_path = item
            break

    if not matching_path:
        return HALDecisionReweighting(
            current_path=current_path,
            path_confidence=None,
            decision='collect-more-evidence',
            reason='No feedback observations exist for the current path yet.',
            should_escalate=False,
            should_hold_current_path=True,
            recommended_action='Continue running the current path and record outcomes.',
        )

    confidence = float(matching_path.get('confidence', 0.0))
    observations = int(matching_path.get('observations', 0))
    success_rate = float(matching_path.get('success_rate', 0.0))

    if observations < 3:
        return HALDecisionReweighting(
            current_path=current_path,
            path_confidence=confidence,
            decision='insufficient-data',
            reason='Fewer than three outcome records exist for this path.',
            should_escalate=False,
            should_hold_current_path=True,
            recommended_action='Keep the current path while collecting more evidence.',
        )

    if confidence >= 0.85 and success_rate >= 0.9:
        return HALDecisionReweighting(
            current_path=current_path,
            path_confidence=confidence,
            decision='stabilize-current-path',
            reason='The current path has high confidence and high success rate.',
            should_escalate=False,
            should_hold_current_path=True,
            recommended_action='Prefer the current path and suppress unnecessary infrastructure escalation.',
        )

    if confidence < 0.5 or success_rate < 0.6:
        return HALDecisionReweighting(
            current_path=current_path,
            path_confidence=confidence,
            decision='consider-escalation',
            reason='The current path has low confidence or low success rate.',
            should_escalate=True,
            should_hold_current_path=False,
            recommended_action='Escalate to a more managed runtime path or require missing services.',
        )

    return HALDecisionReweighting(
        current_path=current_path,
        path_confidence=confidence,
        decision='monitor-current-path',
        reason='The current path is usable but does not yet have strong confidence.',
        should_escalate=False,
        should_hold_current_path=True,
        recommended_action='Continue monitoring and avoid automatic escalation for now.',
    )


def hal_decision_reweighting_dict() -> dict:
    return asdict(build_hal_decision_reweighting())
