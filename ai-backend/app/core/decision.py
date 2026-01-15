from datetime import datetime
from app.models.schemas import DecisionResult

class DecisionEngine:

    def check_access(
        self,
        user_id: str,
        locker_id: str,
        policy: dict
    ) -> DecisionResult:

        if not policy.get("enabled", True):
            return DecisionResult(
                allow=False,
                reason="locker_disabled"
            )

        if user_id not in policy.get("allowed_users", []):
            return DecisionResult(
                allow=False,
                reason="user_not_allowed"
            )

        now = datetime.now().time()

        start = policy.get("start_time")
        end = policy.get("end_time")

        if start and end:
            if not (start <= now <= end):
                return DecisionResult(
                    allow=False,
                    reason="outside_allowed_time"
                )

        return DecisionResult(
            allow=True,
            reason="access_granted"
        )
