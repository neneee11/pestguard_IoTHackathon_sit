import { useState } from 'react';
import { Clock, ArrowRight, Grid3X3 } from 'lucide-react';
import { Button } from '@/component/ui/button';
import { Label } from '@/component/ui/label';
import { LockerGrid } from '@/component/LockerGrid';
import { useAppStore } from '@/stores/appStore';
import { toast } from 'sonner';

const DURATION_OPTIONS = [
  { value: 1, label: '1 ชั่วโมง' },
  { value: 2, label: '2 ชั่วโมง' },
  { value: 3, label: '3 ชั่วโมง' },
  { value: 4, label: '4 ชั่วโมง' },
];

export const BookingPage = () => {
  const { 
    currentStudent, 
    lockers, 
    selectedLocker, 
    selectedDuration,
    setSelectedLocker, 
    setSelectedDuration,
    setCurrentStep 
  } = useAppStore();
  
  const handleContinue = () => {
    if (!selectedLocker) {
      toast.error('กรุณาเลือกล็อคเกอร์');
      return;
    }
    setCurrentStep('confirm');
  };

  const availableCount = lockers.filter(l => l.status === 'available').length;

  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-2 tracking-tight">
            จองล็อคเกอร์
          </h1>
          <p className="text-muted-foreground font-mono">
            สวัสดี, {currentStudent?.fullName}
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-2 gap-4 mb-8">
          <div className="border-4 border-foreground p-4 bg-card shadow-md">
            <div className="flex items-center gap-2 mb-2">
              <Grid3X3 className="w-5 h-5" />
              <span className="font-mono text-sm">ล็อคเกอร์ทั้งหมด</span>
            </div>
            <p className="text-3xl font-bold">{lockers.length}</p>
          </div>
          <div className="border-4 border-foreground p-4 bg-chart-2/10 shadow-md">
            <div className="flex items-center gap-2 mb-2">
              <Clock className="w-5 h-5 text-chart-2" />
              <span className="font-mono text-sm">ว่างพร้อมใช้</span>
            </div>
            <p className="text-3xl font-bold text-chart-2">{availableCount}</p>
          </div>
        </div>

        {/* Locker Grid */}
        <div className="border-4 border-foreground p-4 md:p-6 bg-card shadow-lg mb-8">
          <h2 className="text-xl font-bold mb-4">เลือกล็อคเกอร์</h2>
          <LockerGrid 
            lockers={lockers}
            selectedLocker={selectedLocker}
            onSelect={setSelectedLocker}
          />
        </div>

        {/* Duration Selection */}
        <div className="border-4 border-foreground p-4 md:p-6 bg-card shadow-lg mb-8">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Clock className="w-6 h-6" />
            เลือกระยะเวลา
          </h2>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {DURATION_OPTIONS.map((option) => (
              <button
                key={option.value}
                onClick={() => setSelectedDuration(option.value)}
                className={`p-4 border-4 border-foreground font-mono text-lg font-bold transition-all ${
                  selectedDuration === option.value
                    ? 'bg-foreground text-background shadow-md'
                    : 'bg-card hover:bg-accent'
                }`}
              >
                {option.label}
              </button>
            ))}
          </div>
        </div>

        {/* Summary & Continue */}
        {selectedLocker && (
          <div className="border-4 border-chart-2 p-4 md:p-6 bg-chart-2/10 shadow-lg mb-8">
            <h2 className="text-xl font-bold mb-4">สรุปการจอง</h2>
            <div className="grid grid-cols-2 gap-4 font-mono">
              <div>
                <p className="text-muted-foreground text-sm">ล็อคเกอร์</p>
                <p className="text-2xl font-bold">#{selectedLocker.number}</p>
              </div>
              <div>
                <p className="text-muted-foreground text-sm">ระยะเวลา</p>
                <p className="text-2xl font-bold">{selectedDuration} ชม.</p>
              </div>
            </div>
          </div>
        )}

        <Button 
          onClick={handleContinue}
          size="lg"
          className="w-full h-16 text-xl font-bold shadow-md hover:shadow-lg transition-shadow gap-2"
          disabled={!selectedLocker}
        >
          ดำเนินการต่อ
          <ArrowRight className="w-6 h-6" />
        </Button>
      </div>
    </div>
  );
};
