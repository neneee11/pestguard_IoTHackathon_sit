import { create } from 'zustand';
import type { Student, Locker, Reservation } from '@/types/locker';

type AppStore = {
  // Step management
  currentStep: 'register' | 'booking' | 'confirm' | 'success';
  setCurrentStep: (step: 'register' | 'booking' | 'confirm' | 'success') => void;
  
  // Student management
  registeredStudents: Student[];
  currentStudent: Student | null;
  setCurrentStudent: (student: Student | null) => void;
  addRegisteredStudent: (student: Student) => void;
  
  // Locker management
  lockers: Locker[];
  selectedLocker: Locker | null;
  setSelectedLocker: (locker: Locker | null) => void;
  updateLockerStatus: (lockerId: string, status: 'available' | 'occupied' | 'reserved') => void;
  
  // Reservation management
  reservations: Reservation[];
  selectedDuration: number;
  setSelectedDuration: (duration: number) => void;
  addReservation: (reservation: Reservation) => void;
  
  // Reset function
  reset: () => void;
};

// Initialize lockers (20 lockers numbered 1-20)
const initialLockers: Locker[] = Array.from({ length: 20 }, (_, i) => ({
  id: `locker-${i + 1}`,
  number: i + 1,
  status: 'available' as const,
}));

export const useAppStore = create<AppStore>((set) => ({
  // Step management
  currentStep: 'register',
  setCurrentStep: (step) => set({ currentStep: step }),
  
  // Student management
  registeredStudents: [],
  currentStudent: null,
  setCurrentStudent: (student) => set({ currentStudent: student }),
  addRegisteredStudent: (student) => 
    set((state) => ({ 
      registeredStudents: [...state.registeredStudents, student] 
    })),
  
  // Locker management
  lockers: initialLockers,
  selectedLocker: null,
  setSelectedLocker: (locker) => set({ selectedLocker: locker }),
  updateLockerStatus: (lockerId, status) =>
    set((state) => ({
      lockers: state.lockers.map((locker) =>
        locker.id === lockerId ? { ...locker, status } : locker
      ),
    })),
  
  // Reservation management
  reservations: [],
  selectedDuration: 1,
  setSelectedDuration: (duration) => set({ selectedDuration: duration }),
  addReservation: (reservation) =>
    set((state) => ({
      reservations: [...state.reservations, reservation],
    })),
  
  // Reset function
  reset: () =>
    set({
      currentStep: 'register',
      currentStudent: null,
      selectedLocker: null,
      selectedDuration: 1,
      lockers: initialLockers.map((locker) => ({
        ...locker,
        status: 'available' as const,
      })),
    }),
}));
