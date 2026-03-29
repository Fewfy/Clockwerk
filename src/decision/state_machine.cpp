#include "clockwerk/decision/state_machine.hpp"

namespace clockwerk {

namespace {

DecisionResult make_result(
    const HighLevelState previous_state,
    const HighLevelState next_state,
    const TransitionReason reason) noexcept {
    return DecisionResult{
        .previous_state = previous_state,
        .next_state = next_state,
        .reason = reason,
    };
}

}  // namespace

HighLevelState RuleBasedStateMachine::current_state() const noexcept {
    return current_state_;
}

DecisionResult RuleBasedStateMachine::Tick(const DecisionInputs& inputs) noexcept {
    const auto previous_state = current_state_;

    switch (current_state_) {
    case HighLevelState::kIdle:
        if (inputs.has_navigation_target) {
            current_state_ = HighLevelState::kNavigate;
            return make_result(previous_state, current_state_, TransitionReason::kMissionRequested);
        }
        break;

    case HighLevelState::kNavigate:
        if (inputs.obstacle_too_close) {
            current_state_ = HighLevelState::kEmergencyStop;
            return make_result(previous_state, current_state_, TransitionReason::kObstacleTooClose);
        }

        if (inputs.fall_detected) {
            current_state_ = HighLevelState::kRecover;
            return make_result(previous_state, current_state_, TransitionReason::kFallDetected);
        }
        break;

    case HighLevelState::kRecover:
        if (inputs.recovery_completed) {
            current_state_ = HighLevelState::kIdle;
            return make_result(previous_state, current_state_, TransitionReason::kRecoveryCompleted);
        }
        break;

    case HighLevelState::kEmergencyStop:
        if (inputs.emergency_stop_cleared) {
            current_state_ = HighLevelState::kIdle;
            return make_result(previous_state, current_state_, TransitionReason::kEmergencyCleared);
        }
        break;
    }

    return make_result(previous_state, current_state_, TransitionReason::kNoChange);
}

}  // namespace clockwerk
