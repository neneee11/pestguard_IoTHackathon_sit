import { useState } from 'react';
import { ScanFace, CheckCircle, Loader2 } from 'lucide-react';
import { Button } from '@/component/ui/button';
import { CameraCapture } from '@/component/CameraCapture';
import { useAppStore } from '@/stores/appStore';
import { toast } from 'sonner';

export const ConfirmationPage = () => {
  const [verificationImage, setVerificationImage] = useState<string | null>(null);
  const [isVerifying, setIsVerifying] = useState(false);
  
  const { 
    currentStudent, 
    selectedLocker, 
    selectedDuration,
    addReservation,
    updateLockerStatus,
    setCurrentStep 
  } = useAppStore();

  const handleVerify = async () => {
    if (!verificationImage) {
      toast.error('กรุณาสแกนใบหน้าเพื่อยืนยัน');
      return;
    }

    setIsVerifying(true);
    
    // Simulate face verification
    await new Promise(resolve => setTimeout(resolve, 2000));

    // Create reservation
    const now = new Date();
    const endTime = new Date(now.getTime() + selectedDuration * 60 * 60 * 1000);

    const reservation = {
      id: crypto.randomUUID(),
      lockerId: selectedLocker!.id,
      lockerNumber: selectedLocker!.number,
      studentId: currentStudent!.studentId,
      startTime: now,
      endTime,
      status: 'active' as const,
    };

    addReservation(reservation);
    updateLockerStatus(selectedLocker!.id, 'reserved');
    
    toast.success('จองล็อคเกอร์สำเร็จ!');
    setCurrentStep('success');
    setIsVerifying(false);
  };

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-2 tracking-tight">
            ยืนยันตัวตน
          </h1>
          <p className="text-muted-foreground font-mono">
            สแกนใบหน้าเพื่อยืนยันการจอง
          </p>
        </div>

        {/* Reservation Summary */}
        <div className="border-4 border-foreground p-4 md:p-6 bg-card shadow-lg mb-8">
          <h2 className="text-xl font-bold mb-4">ข้อมูลการจอง</h2>
          <div className="grid grid-cols-2 gap-4 font-mono">
            <div>
              <p className="text-muted-foreground text-sm">ชื่อผู้จอง</p>
              <p className="text-lg font-bold">{currentStudent?.fullName}</p>
            </div>
            <div>
              <p className="text-muted-foreground text-sm">รหัสนักศึกษา</p>
              <p className="text-lg font-bold">{currentStudent?.studentId}</p>
            </div>
            <div>
              <p className="text-muted-foreground text-sm">ล็อคเกอร์</p>
              <p className="text-2xl font-bold text-chart-2">#{selectedLocker?.number}</p>
            </div>
            <div>
              <p className="text-muted-foreground text-sm">ระยะเวลา</p>
              <p className="text-2xl font-bold">{selectedDuration} ชม.</p>
            </div>
          </div>
        </div>

        {/* Face Scan */}
        <div className="border-4 border-foreground p-4 md:p-6 bg-card shadow-lg mb-8">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <ScanFace className="w-6 h-6" />
            สแกนใบหน้า
          </h2>
          <CameraCapture 
            onCapture={setVerificationImage} 
            capturedImage={verificationImage}
            isVerification
          />
        </div>

        <Button 
          onClick={handleVerify}
          size="lg"
          className="w-full h-16 text-xl font-bold shadow-md hover:shadow-lg transition-shadow gap-2"
          disabled={!verificationImage || isVerifying}
        >
          {isVerifying ? (
            <>
              <Loader2 className="w-6 h-6 animate-spin" />
              กำลังตรวจสอบ...
            </>
          ) : (
            <>
              <CheckCircle className="w-6 h-6" />
              ยืนยันการจอง
            </>
          )}
        </Button>
      </div>
    </div>
  );
};
