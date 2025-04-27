import * as React from "react"
import { cn } from "@/lib/utils"
import { Button } from "./button"
import { Upload } from "lucide-react"

interface UploadButtonProps {
  accept?: string
  onChange: (file: File | null) => void
  className?: string
}

export function UploadButton({ accept = "image/*", onChange, className }: UploadButtonProps) {
  const inputRef = React.useRef<HTMLInputElement>(null)
  const [fileName, setFileName] = React.useState<string | null>(null)
  
  const handleClick = () => {
    inputRef.current?.click()
  }
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0] || null
    if (file) {
      setFileName(file.name)
      onChange(file)
    }
  }
  
  return (
    <div className={cn("flex flex-col items-start gap-2", className)}>
      <Button 
        type="button" 
        variant="outline" 
        onClick={handleClick}
        className="w-full flex items-center justify-center gap-2"
      >
        <Upload className="h-4 w-4" />
        <span>{fileName ? "Change file" : "Upload file"}</span>
      </Button>
      
      <input 
        type="file"
        ref={inputRef}
        accept={accept}
        onChange={handleChange}
        className="hidden"
      />
      
      {fileName && (
        <p className="text-sm text-muted-foreground truncate w-full">
          {fileName}
        </p>
      )}
    </div>
  )
} 