from qdrant_client import QdrantClient
import sys

print(f"Python running at: {sys.executable}")

try:
    # ลองเชื่อมต่อ (ถ้าเชื่อมไม่ได้ มันจะ error ตั้งแต่ตรงนี้)
    client = QdrantClient(host="10.4.41.250", port=6333)
    
    # เช็คว่ามีคำสั่ง search ไหม
    if hasattr(client, 'search'):
        print("✅ SUCCESS: พบคำสั่ง .search() ใช้งานได้ปกติ!")
    else:
        print("❌ ERROR: ไม่พบคำสั่ง .search() (เป็นไปได้ยากมาก ถ้าเวอร์ชัน 1.16.2)")
        print("Methods ที่มี:", dir(client))

except Exception as e:
    print(f"❌ CONNECTION ERROR: {e}")