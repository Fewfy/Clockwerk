#include <cstdlib>
#include <iostream>

#include "clockwerk/decision/state_machine.hpp"

namespace {

using clockwerk::DecisionInputs;
using clockwerk::HighLevelState;
using clockwerk::RuleBasedStateMachine;
using clockwerk::TransitionReason;

void Expect(bool condition, const char* message) {
    if (!condition) {
        std::cerr << "test failure: " << message << '\n';
        std::exit(1);
    }
}

void TestIdleToNavigate() {
    RuleBasedStateMachine machine;
    const auto result = machine.Tick(DecisionInputs{.has_navigation_target = true});

    Expect(result.previous_state == HighLevelState::kIdle, "idle transition should start from idle");
    Expect(result.next_state == HighLevelState::kNavigate, "idle should move to navigate");
    Expect(result.reason == TransitionReason::kMissionRequested, "idle transition reason mismatch");
}

void TestNavigateToRecover() {
    RuleBasedStateMachine machine;
    static_cast<void>(machine.Tick(DecisionInputs{.has_navigation_target = true}));
    const auto result = machine.Tick(DecisionInputs{.fall_detected = true});

    Expect(result.next_state == HighLevelState::kRecover, "navigate should move to recover");
    Expect(result.reason == TransitionReason::kFallDetected, "recover transition reason mismatch");
}

void TestNavigateToEmergencyStopHasHigherPriorityThanRecover() {
    RuleBasedStateMachine machine;
    static_cast<void>(machine.Tick(DecisionInputs{.has_navigation_target = true}));
    const auto result = machine.Tick(DecisionInputs{
        .fall_detected = true,
        .obstacle_too_close = true,
    });

    Expect(result.next_state == HighLevelState::kEmergencyStop, "emergency stop should override recover");
    Expect(result.reason == TransitionReason::kObstacleTooClose, "priority transition reason mismatch");
}

void TestRecoverToIdle() {
    RuleBasedStateMachine machine;
    static_cast<void>(machine.Tick(DecisionInputs{.has_navigation_target = true}));
    static_cast<void>(machine.Tick(DecisionInputs{.fall_detected = true}));
    const auto result = machine.Tick(DecisionInputs{.recovery_completed = true});

    Expect(result.next_state == HighLevelState::kIdle, "recover should move back to idle");
    Expect(result.reason == TransitionReason::kRecoveryCompleted, "recover completion reason mismatch");
}

void TestEmergencyStopToIdle() {
    RuleBasedStateMachine machine;
    static_cast<void>(machine.Tick(DecisionInputs{.has_navigation_target = true}));
    static_cast<void>(machine.Tick(DecisionInputs{.obstacle_too_close = true}));
    const auto result = machine.Tick(DecisionInputs{.emergency_stop_cleared = true});

    Expect(result.next_state == HighLevelState::kIdle, "emergency stop should move back to idle");
    Expect(result.reason == TransitionReason::kEmergencyCleared, "emergency clear reason mismatch");
}

void TestNoChangeKeepsState() {
    RuleBasedStateMachine machine;
    const auto result = machine.Tick(DecisionInputs{});

    Expect(!result.state_changed(), "empty input should keep current state");
    Expect(machine.current_state() == HighLevelState::kIdle, "state should remain idle");
}

}  // namespace

int main() {
    TestIdleToNavigate();
    TestNavigateToRecover();
    TestNavigateToEmergencyStopHasHigherPriorityThanRecover();
    TestRecoverToIdle();
    TestEmergencyStopToIdle();
    TestNoChangeKeepsState();

    std::cout << "all state machine tests passed\n";
    return 0;
}
