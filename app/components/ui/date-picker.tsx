import * as React from "react";
import { cn } from "@/lib/utils";
import { Input } from "./input";
import { Label } from "./label";

interface DatePickerProps extends React.InputHTMLAttributes<HTMLInputElement> {
  selected?: Date | null;
  onSelect?: (date: Date | null) => void;
  label?: string;
}

export function DatePicker({ 
  className,
  selected,
  onSelect,
  label,
  id,
  ...props 
}: DatePickerProps) {
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.value) {
      const date = new Date(e.target.value);
      onSelect?.(date);
    } else {
      onSelect?.(null);
    }
  };

  return (
    <div className={cn("space-y-2", className)}>
      {label && <Label htmlFor={id}>{label}</Label>}
      <Input
        type="date"
        value={selected ? selected.toISOString().split('T')[0] : ''}
        onChange={handleChange}
        id={id}
        {...props}
      />
    </div>
  );
} 