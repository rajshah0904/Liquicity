import * as React from "react"
import { cn } from "@/lib/utils"
import { ChevronDown } from "lucide-react"

const Select = React.forwardRef<
  HTMLSelectElement,
  React.SelectHTMLAttributes<HTMLSelectElement>
>(({ className, children, ...props }, ref) => {
  return (
    <div className="relative">
      <select
        className={cn(
          "w-full h-10 rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 appearance-none",
          className
        )}
        ref={ref}
        {...props}
      >
        {children}
      </select>
      <ChevronDown className="absolute right-3 top-3 h-4 w-4 opacity-50 pointer-events-none" />
    </div>
  )
})
Select.displayName = "Select"

// For compatibility with the existing component structure
const SelectTrigger = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("flex items-center justify-between", className)} {...props}>
    {children}
  </div>
)
SelectTrigger.displayName = "SelectTrigger"

const SelectValue = ({ className, children, ...props }: React.HTMLAttributes<HTMLSpanElement>) => (
  <span className={cn("block truncate", className)} {...props}>
    {children}
  </span>
)
SelectValue.displayName = "SelectValue"

const SelectContent = ({ className, children, ...props }: React.HTMLAttributes<HTMLDivElement>) => (
  <div className={cn("absolute mt-1 w-full z-50 bg-background border rounded-md shadow-lg", className)} {...props}>
    {children}
  </div>
)
SelectContent.displayName = "SelectContent"

const SelectItem = ({ className, children, value, ...props }: React.OptionHTMLAttributes<HTMLOptionElement>) => (
  <option className={cn("px-3 py-2 hover:bg-accent", className)} value={value} {...props}>
    {children}
  </option>
)
SelectItem.displayName = "SelectItem"

export { Select, SelectTrigger, SelectValue, SelectContent, SelectItem } 