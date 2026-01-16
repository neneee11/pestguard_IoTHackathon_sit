from fastapi import APIRouter
from app.services.camera import CameraService
from app.services.face_detect import FaceDetector
from app.services.antispoof import AntiSpoofService
from app.core.audit import log_event
from app.core.decision import DecisionEngine
from app.core.policy_store import get_policy

decision_engine = DecisionEngine()

antispoof = AntiSpoofService()
router = APIRouter()

camera = CameraService(0)  # USB camera
detector = FaceDetector()

def liveness_check(frames):
    scores = []
    for face in frames:
        score = antispoof.check(face)
        scores.append(score)

    passed = sum(s >= 0.7 for s in scores)
    return passed >= 3, scores

@router.post("/scan")
def scan_face():
    frames = []

    for _ in range(5):
        frame = camera.get_frame()
        if frame is None:
            continue

        face = detector.detect(frame)
        if face is not None:
            frames.append(face)

    if len(frames) < 3:
        return {"status": "deny", "reason": "no_face"}

    passed, scores = liveness_check(frames)

    if not passed:
        log_event("LIVENESS_FAIL", detail={"scores": scores})
        return {
            "status": "deny",
            "reason": "spoof_detected",
            "liveness": scores
        }

    # ✅ ผ่าน liveness → ค่อยทำ embedding
    emb = recognizer.get_embedding(frames[-1])
    result = qdrant.search(emb)

    if not result or result[0].score < 0.35:
        return {"status": "deny", "reason": "unknown"}

    log_event("ACCESS_GRANTED", user=result[0].payload["user_id"])

    user_id = result[0].payload["user_id"]
    locker_id = "locker_01"  # ตอนนี้ fix ไว้ก่อน

    policy = get_policy(locker_id)

    if not policy:
        return {"status": "deny", "reason": "no_policy"}

    decision = decision_engine.check_access(
        user_id=user_id,
        locker_id=locker_id,
        policy=policy
    )

    if not decision.allow:
        log_event(
            "ACCESS_DENIED",
            user=user_id,
            detail={"reason": decision.reason}
        )
        return {
            "status": "deny",
            "reason": decision.reason
        }

    log_event(
        "ACCESS_GRANTED",
        user=user_id,
        detail={"locker": locker_id}
    )

    return {
        "status": "allow",
        "user_id": user_id,
        "locker": locker_id
    }
