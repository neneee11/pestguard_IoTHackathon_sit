import { useEffect, useState } from 'react';
import { CheckCircle, Clock, Bell, Home, AlertCircle } from 'lucide-react';
import { Button } from '@/component/ui/button';
import { useAppStore } from '@/stores/appStore';
import { toast } from 'sonner';

export const SuccessPage = () => {
  const { currentStudent, selectedLocker, selectedDuration, reservations, reset } = useAppStore();
  const [timeRemaining, setTimeRemaining] = useState<string>('');
  const [notificationSent, setNotificationSent] = useState(false);

  const latestReservation = reservations[reservations.length - 1];
  
  useEffect(() => {
    if (!latestReservation) return;

    const updateTimer = () => {
      const now = new Date();
      const endTime = new Date(latestReservation.endTime);
      const diff = endTime.getTime() - now.getTime();

      if (diff <= 0) {
        setTimeRemaining('หมดเวลา');
        return;
      }

      const hours = Math.floor(diff / (1000 * 60 * 60));
      const minutes = Math.floor((diff % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((diff % (1000 * 60)) / 1000);

      setTimeRemaining(
        `${hours.toString().padStart(2, '0')}:${minutes.toString().padStart(2, '0')}:${seconds.toString().padStart(2, '0')}`
      );

      // Show notification when 5 minutes remaining (for demo, we'll use 10 seconds)
      if (diff <= 10000 && !notificationSent) {
        toast.warning('⚠️ เหลือเวลาอีก 10 วินาที!', {
          description: 'กรุณาเตรียมคืนล็อคเกอร์',
          duration: 5000,
        });
        setNotificationSent(true);
      }
    };

    updateTimer();
    const interval = setInterval(updateTimer, 1000);

    return () => clearInterval(interval);
  }, [latestReservation, notificationSent]);

  const handleNewBooking = () => {
    reset();
  };

  const endTime = latestReservation 
    ? new Date(latestReservation.endTime).toLocaleTimeString('th-TH', { 
        hour: '2-digit', 
        minute: '2-digit' 
      })
    : '';

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="max-w-2xl mx-auto">
        {/* Success Animation */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-24 h-24 border-4 border-chart-2 bg-chart-2/20 mb-4">
            <CheckCircle className="w-12 h-12 text-chart-2" />
          </div>
          <h1 className="text-4xl md:text-5xl font-bold mb-2 tracking-tight text-chart-2">
            จองสำเร็จ!
          </h1>
          <p className="text-muted-foreground font-mono">
            การจองล็อคเกอร์ของคุณเสร็จสมบูรณ์
          </p>
        </div>

        {/* Booking Details */}
        <div className="border-4 border-chart-2 p-4 md:p-6 bg-card shadow-lg mb-8">
          <div className="text-center mb-6">
            <p className="text-muted-foreground font-mono text-sm mb-1">ล็อคเกอร์หมายเลข</p>
            <p className="text-6xl font-bold text-chart-2">#{selectedLocker?.number}</p>
          </div>
          
          <div className="grid grid-cols-2 gap-4 font-mono border-t-2 border-foreground pt-4">
            <div>
              <p className="text-muted-foreground text-sm">ผู้จอง</p>
              <p className="font-bold">{currentStudent?.fullName}</p>
            </div>
            <div>
              <p className="text-muted-foreground text-sm">รหัสนักศึกษา</p>
              <p className="font-bold">{currentStudent?.studentId}</p>
            </div>
            <div>
              <p className="text-muted-foreground text-sm">ระยะเวลา</p>
              <p className="font-bold">{selectedDuration} ชั่วโมง</p>
            </div>
            <div>
              <p className="text-muted-foreground text-sm">หมดเวลา</p>
              <p className="font-bold">{endTime}</p>
            </div>
          </div>
        </div>

        {/* Countdown Timer */}
        <div className="border-4 border-foreground p-4 md:p-6 bg-secondary shadow-lg mb-8">
          <div className="flex items-center justify-center gap-2 mb-4">
            <Clock className="w-6 h-6" />
            <h2 className="text-xl font-bold">เวลาที่เหลือ</h2>
          </div>
          <p className="text-5xl md:text-6xl font-mono font-bold text-center tracking-wider">
            {timeRemaining}
          </p>
        </div>

        {/* Notification Info */}
        <div className="border-4 border-chart-4 p-4 bg-chart-4/10 shadow-md mb-8">
          <div className="flex items-start gap-3">
            <Bell className="w-6 h-6 text-chart-4 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="font-bold mb-1">ระบบแจ้งเตือน</h3>
              <p className="text-sm text-muted-foreground font-mono">
                ระบบจะแจ้งเตือนคุณเมื่อใกล้หมดเวลาการใช้งาน กรุณาคืนล็อคเกอร์ก่อนเวลาหมด
              </p>
            </div>
          </div>
        </div>

        <Button 
          onClick={handleNewBooking}
          variant="outline"
          size="lg"
          className="w-full h-16 text-xl font-bold shadow-md hover:shadow-lg transition-shadow gap-2"
        >
          <Home className="w-6 h-6" />
          กลับหน้าหลัก
        </Button>
      </div>
    </div>
  );
};
