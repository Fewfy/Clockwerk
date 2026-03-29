#pragma once

#include "clockwerk/core/enums.hpp"

namespace clockwerk {

struct DecisionInputs {
    bool has_navigation_target{false};
    bool fall_detected{false};
    bool obstacle_too_close{false};
    bool recovery_completed{false};
    bool emergency_stop_cleared{false};
};

struct DecisionResult {
    HighLevelState previous_state{HighLevelState::kIdle};
    HighLevelState next_state{HighLevelState::kIdle};
    TransitionReason reason{TransitionReason::kNoChange};

    [[nodiscard]] bool state_changed() const noexcept {
        return previous_state != next_state;
    }
};

class RuleBasedStateMachine {
public:
    RuleBasedStateMachine() = default;

    [[nodiscard]] HighLevelState current_state() const noexcept;
    [[nodiscard]] DecisionResult Tick(const DecisionInputs& inputs) noexcept;

private:
    HighLevelState current_state_{HighLevelState::kIdle};
};

}  // namespace clockwerk
