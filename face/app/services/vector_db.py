import logging
from typing import Optional, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance, PointStruct
from app.config import settings

# Setup Logger
logger = logging.getLogger(__name__)

class QdrantService:
    def __init__(self):
        # สร้าง Client เชื่อมต่อ (ยังไม่ได้ต่อจริงจนกว่าจะยิง Request)
        self.client = QdrantClient(
            host=settings.QDRANT_HOST, 
            port=settings.QDRANT_PORT
        )
        self.collection_name = settings.COLLECTION_NAME

    def init_collection(self):
        """
        สร้าง Collection ถ้ายังไม่มี
        function นี้จะถูกเรียกจาก main.py ตอนเริ่ม Server
        """
        try:
            # ตรวจสอบว่ามี collection นี้หรือยัง
            if not self.client.collection_exists(self.collection_name):
                logger.info(f"Creating collection '{self.collection_name}'...")
                
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=512,  # InsightFace (buffalo_l) ให้ output 512 dimension
                        distance=Distance.COSINE # ใช้ Cosine Similarity เหมาะกับ Face Recognition
                    )
                )
                logger.info(f"✅ Collection '{self.collection_name}' created successfully.")
            else:
                logger.info(f"✅ Collection '{self.collection_name}' already exists.")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Qdrant collection: {e}")
            raise e

    def register_new_user(self, user_id: int, embedding: list) -> bool:
        """
        1. ลงทะเบียนผู้ใช้ใหม่ (เก็บแค่หน้าและ ID ยังไม่มีตู้)
        """
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=user_id,
                        vector=embedding,
                        payload={
                            "locker_id": None, # ยังไม่มีการจอง
                            "active": True
                        }
                    )
                ]
            )
            logger.info(f"Registered new User ID: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Registration failed: {e}")
            return False

    def update_booking(self, user_id: int, locker_id: str) -> bool:
        """
        2. อัปเดตการจอง (ไม่ต้องใช้รูป ใช้แค่ ID)
        """
        try:
            # ใช้คำสั่ง set_payload ของ Qdrant เพื่อแก้ข้อมูลเฉพาะจุด
            self.client.set_payload(
                collection_name=self.collection_name,
                points=[user_id],
                payload={
                    "locker_id": locker_id
                }
            )
            logger.info(f"Updated booking for User {user_id} -> Locker {locker_id}")
            return True
        except Exception as e:
            logger.error(f"Booking update failed: {e}")
            return False

    #00000    
    def upsert_face(self, user_id: int, locker_id: str, embedding: list) -> bool:
        """
        บันทึกหรืออัปเดตข้อมูลใบหน้า
        """
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[
                    PointStruct(
                        id=user_id, # ใช้ User ID เป็น Primary Key (ถ้าซ้ำจะทับของเดิม)
                        vector=embedding,
                        payload={
                            "locker_id": locker_id,
                            "active": True # เผื่ออนาคตอยากทำระบบระงับสิทธิ์ชั่วคราว
                        }
                    )
                ]
            )
            logger.info(f"Upserted face for User ID: {user_id}, Locker: {locker_id}")
            return True
        except Exception as e:
            logger.error(f"❌ Error upserting face: {e}")
            return False

    def search_face(self, embedding: list) -> Optional[Any]:
        """
        ค้นหาใบหน้าที่ใกล้เคียงที่สุด
        Return: PointStruct (Object ของ Qdrant) หรือ None
        """
        try:
            # ใช้ threshold จาก Config
            threshold = settings.FACE_SIMILARITY_THRESHOLD

            results = self.client.query_points(
                collection_name=self.collection_name,
                query=embedding,
                limit=1, # เอาแค่คนเดียวที่เหมือนที่สุด
                score_threshold=threshold,
                with_payload=True
            ).points

            if not results:
                logger.info("Search completed: No match found.")
                return None

            hit = results[0]
            logger.info(f"Match found! User ID: {hit.id}, Score: {hit.score:.4f}")
            return hit

        except Exception as e:
            logger.error(f"❌ Error searching face: {e}")
            return None

    def delete_face(self, user_id: str):
        """ลบข้อมูลใบหน้า (เผื่อต้องใช้)"""
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[user_id]
            )
            logger.info(f"Deleted User ID: {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            return False

# Singleton Instance
qdrant_service = QdrantService()