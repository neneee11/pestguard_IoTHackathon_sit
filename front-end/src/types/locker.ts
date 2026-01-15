export interface Student {
  id: string;
  studentId: string;
  fullName: string;
  faceImage: string;
  registeredAt: Date;
}

export interface Locker {
  id: string;
  number: number;
  status: 'available' | 'occupied' | 'reserved';
  reservedBy?: string;
  reservedUntil?: Date;
}

export interface Reservation {
  id: string;
  lockerId: string;
  lockerNumber: number;
  studentId: string;
  startTime: Date;
  endTime: Date;
  status: 'active' | 'completed' | 'expired';
}
