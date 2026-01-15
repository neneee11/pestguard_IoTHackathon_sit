import { Lock, LockOpen, Clock } from 'lucide-react';
import { cn } from '@/lib/utils';
import type { Locker } from '@/types/locker';

interface LockerGridProps {
  lockers: Locker[];
  selectedLocker: Locker | null;
  onSelect: (locker: Locker) => void;
}

export const LockerGrid = ({ lockers, selectedLocker, onSelect }: LockerGridProps) => {
  return (
    <div className="grid grid-cols-3 md:grid-cols-4 gap-4">
      {lockers.map((locker) => {
        const isSelected = selectedLocker?.id === locker.id;
        const isAvailable = locker.status === 'available';
        const isOccupied = locker.status === 'occupied';
        const isReserved = locker.status === 'reserved';

        return (
          <button
            key={locker.id}
            onClick={() => isAvailable && onSelect(locker)}
            disabled={!isAvailable}
            className={cn(
              "aspect-square border-4 border-foreground p-4 flex flex-col items-center justify-center gap-2 transition-all",
              isAvailable && "bg-card hover:bg-accent cursor-pointer hover:shadow-md",
              isOccupied && "bg-destructive/20 cursor-not-allowed opacity-60",
              isReserved && "bg-chart-4/20 cursor-not-allowed opacity-60",
              isSelected && "bg-chart-2/30 shadow-lg ring-4 ring-chart-2"
            )}
          >
            {isAvailable ? (
              <LockOpen className={cn(
                "w-8 h-8 md:w-10 md:h-10",
                isSelected ? "text-chart-2" : "text-foreground"
              )} />
            ) : isOccupied ? (
              <Lock className="w-8 h-8 md:w-10 md:h-10 text-destructive" />
            ) : (
              <Clock className="w-8 h-8 md:w-10 md:h-10 text-chart-4" />
            )}
            <span className={cn(
              "font-mono text-lg md:text-xl font-bold",
              isSelected && "text-chart-2"
            )}>
              #{locker.number}
            </span>
            <span className="text-xs font-mono text-muted-foreground">
              {isAvailable ? 'ว่าง' : isOccupied ? 'ไม่ว่าง' : 'จองแล้ว'}
            </span>
          </button>
        );
      })}
    </div>
  );
};
