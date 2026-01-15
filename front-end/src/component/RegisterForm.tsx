import { useState } from 'react';
import { User, IdCard, ArrowRight, UserCheck, ScanFace } from 'lucide-react';
import { Button } from '@/component/ui/button';
import { Input } from '@/component/ui/input';
import { Label } from '@/component/ui/label';
import { CameraCapture } from '@/component/CameraCapture';
import { useAppStore } from '@/stores/appStore';
import { toast } from 'sonner';

export const RegisterForm = () => {
  const [studentId, setStudentId] = useState('');
  const [fullName, setFullName] = useState('');
  const [faceImage, setFaceImage] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [mode, setMode] = useState<'choice' | 'register' | 'login'>('choice');
  const [loginImage, setLoginImage] = useState<string | null>(null);
  const [loginStudentId, setLoginStudentId] = useState('');
  
  const { setCurrentStudent, setCurrentStep, registeredStudents, addRegisteredStudent } = useAppStore();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!studentId.trim() || !fullName.trim() || !faceImage) {
      toast.error('กรุณากรอกข้อมูลให้ครบถ้วนและถ่ายภาพใบหน้า');
      return;
    }

    // Check if already registered
    const existing = registeredStudents.find(s => s.studentId === studentId.trim());
    if (existing) {
      toast.error('รหัสนักศึกษานี้ลงทะเบียนแล้ว กรุณาใช้การเข้าสู่ระบบ');
      return;
    }

    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 1500));

    const student = {
      id: crypto.randomUUID(),
      studentId: studentId.trim(),
      fullName: fullName.trim(),
      faceImage,
      registeredAt: new Date(),
    };

    addRegisteredStudent(student);
    setCurrentStudent(student);
    toast.success('ลงทะเบียนสำเร็จ!');
    setCurrentStep('booking');
    setIsLoading(false);
  };

  const handleLogin = async () => {
    if (!loginStudentId.trim()) {
      toast.error('กรุณากรอกรหัสนักศึกษา');
      return;
    }
    
    if (!loginImage) {
      toast.error('กรุณาสแกนใบหน้าเพื่อยืนยันตัวตน');
      return;
    }

    const student = registeredStudents.find(s => s.studentId === loginStudentId.trim());
    if (!student) {
      toast.error('ไม่พบรหัสนักศึกษานี้ในระบบ กรุณาลงทะเบียนก่อน');
      return;
    }

    setIsLoading(true);
    await new Promise(resolve => setTimeout(resolve, 2000));

    setCurrentStudent(student);
    toast.success(`ยินดีต้อนรับกลับ, ${student.fullName}!`);
    setCurrentStep('booking');
    setIsLoading(false);
  };

  // Choice Screen
  if (mode === 'choice') {
    return (
      <div className="min-h-screen bg-background p-4 md:p-8 flex items-center justify-center">
        <div className="max-w-xl w-full">
          <div className="mb-8 text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-2 tracking-tight">
              Smart Locker
            </h1>
            <p className="text-muted-foreground font-mono">
              ระบบจองล็อคเกอร์อัจฉริยะ
            </p>
          </div>

          <div className="space-y-4">
            <button
              onClick={() => setMode('login')}
              className="w-full border-4 border-foreground p-6 bg-card shadow-lg hover:shadow-xl transition-all hover:bg-accent flex items-center gap-4"
            >
              <div className="w-16 h-16 border-2 border-foreground flex items-center justify-center bg-chart-2/20">
                <ScanFace className="w-8 h-8 text-chart-2" />
              </div>
              <div className="text-left flex-1">
                <h2 className="text-xl font-bold">ลงทะเบียนแล้ว</h2>
                <p className="text-muted-foreground font-mono text-sm">
                  สแกนใบหน้าเพื่อเข้าสู่ระบบ
                </p>
              </div>
              <ArrowRight className="w-6 h-6" />
            </button>

            <button
              onClick={() => setMode('register')}
              className="w-full border-4 border-foreground p-6 bg-card shadow-lg hover:shadow-xl transition-all hover:bg-accent flex items-center gap-4"
            >
              <div className="w-16 h-16 border-2 border-foreground flex items-center justify-center bg-secondary">
                <UserCheck className="w-8 h-8" />
              </div>
              <div className="text-left flex-1">
                <h2 className="text-xl font-bold">ลงทะเบียนใหม่</h2>
                <p className="text-muted-foreground font-mono text-sm">
                  สำหรับผู้ใช้งานครั้งแรก
                </p>
              </div>
              <ArrowRight className="w-6 h-6" />
            </button>
          </div>

          {registeredStudents.length > 0 && (
            <p className="text-center text-muted-foreground font-mono text-sm mt-6">
              มีผู้ลงทะเบียนแล้ว {registeredStudents.length} คน
            </p>
          )}
        </div>
      </div>
    );
  }

  // Login Screen
  if (mode === 'login') {
    return (
      <div className="min-h-screen bg-background p-4 md:p-8">
        <div className="max-w-2xl mx-auto">
          <button 
            onClick={() => setMode('choice')}
            className="mb-4 text-muted-foreground font-mono hover:text-foreground transition-colors"
          >
            ← กลับ
          </button>

          <div className="mb-8 text-center">
            <h1 className="text-4xl md:text-5xl font-bold mb-2 tracking-tight">
              เข้าสู่ระบบ
            </h1>
            <p className="text-muted-foreground font-mono">
              กรอกรหัสนักศึกษาและสแกนใบหน้า
            </p>
          </div>

          {/* Student ID */}
          <div className="border-4 border-foreground p-4 md:p-6 bg-card shadow-lg mb-8">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <IdCard className="w-6 h-6" />
              รหัสนักศึกษา
            </h2>
            <Input
              type="text"
              placeholder="กรอกรหัสนักศึกษา"
              value={loginStudentId}
              onChange={(e) => setLoginStudentId(e.target.value)}
              className="h-14 text-lg border-2 border-foreground bg-background font-mono"
            />
          </div>

          {/* Face Scan */}
          <div className="border-4 border-foreground p-4 md:p-6 bg-card shadow-lg mb-8">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <ScanFace className="w-6 h-6" />
              สแกนใบหน้า
            </h2>
            <CameraCapture 
              onCapture={setLoginImage} 
              capturedImage={loginImage}
              isVerification
            />
          </div>

          <Button 
            onClick={handleLogin}
            size="lg"
            className="w-full h-16 text-xl font-bold shadow-md hover:shadow-lg transition-shadow gap-2"
            disabled={isLoading || !loginImage || !loginStudentId}
          >
            {isLoading ? (
              'กำลังตรวจสอบ...'
            ) : (
              <>
                เข้าสู่ระบบ
                <ArrowRight className="w-6 h-6" />
              </>
            )}
          </Button>
        </div>
      </div>
    );
  }

  // Register Screen
  return (
    <div className="min-h-screen bg-background p-4 md:p-8">
      <div className="max-w-2xl mx-auto">
        <button 
          onClick={() => setMode('choice')}
          className="mb-4 text-muted-foreground font-mono hover:text-foreground transition-colors"
        >
          ← กลับ
        </button>

        <div className="mb-8 text-center">
          <h1 className="text-4xl md:text-5xl font-bold mb-2 tracking-tight">
            ลงทะเบียนใหม่
          </h1>
          <p className="text-muted-foreground font-mono">
            ถ่ายภาพใบหน้าและกรอกข้อมูลเพื่อลงทะเบียน
          </p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Camera Section */}
          <div className="border-4 border-foreground p-4 md:p-6 bg-card shadow-lg">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <User className="w-6 h-6" />
              ถ่ายภาพใบหน้า
            </h2>
            <CameraCapture 
              onCapture={setFaceImage} 
              capturedImage={faceImage}
            />
          </div>

          {/* Form Fields */}
          <div className="border-4 border-foreground p-4 md:p-6 bg-card shadow-lg space-y-6">
            <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
              <IdCard className="w-6 h-6" />
              ข้อมูลนักศึกษา
            </h2>
            
            <div className="space-y-2">
              <Label htmlFor="studentId" className="text-lg font-semibold">
                รหัสนักศึกษา
              </Label>
              <Input
                id="studentId"
                type="text"
                placeholder="กรอกรหัสนักศึกษา"
                value={studentId}
                onChange={(e) => setStudentId(e.target.value)}
                className="h-14 text-lg border-2 border-foreground bg-background font-mono"
                required
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="fullName" className="text-lg font-semibold">
                ชื่อ-นามสกุล
              </Label>
              <Input
                id="fullName"
                type="text"
                placeholder="กรอกชื่อ-นามสกุล"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="h-14 text-lg border-2 border-foreground bg-background"
                required
              />
            </div>
          </div>

          <Button 
            type="submit" 
            size="lg"
            className="w-full h-16 text-xl font-bold shadow-md hover:shadow-lg transition-shadow gap-2"
            disabled={isLoading || !faceImage || !studentId || !fullName}
          >
            {isLoading ? (
              'กำลังลงทะเบียน...'
            ) : (
              <>
                ลงทะเบียน
                <ArrowRight className="w-6 h-6" />
              </>
            )}
          </Button>
        </form>
      </div>
    </div>
  );
};
