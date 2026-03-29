#pragma once

namespace clockwerk {

enum class HighLevelState {
    kIdle,
    kNavigate,
    kRecover,
    kEmergencyStop,
};

enum class TransitionReason {
    kNoChange,
    kMissionRequested,
    kFallDetected,
    kObstacleTooClose,
    kEmergencyCleared,
    kRecoveryCompleted,
};

}  // namespace clockwerk
