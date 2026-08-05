import { useId, useRef } from 'react'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { readFileAsBase64 } from '@/lib/file-utils'

// Matches the wire shape the backend forwards straight into Attachment(fileName, fileContent) —
// FileContent is base64 with no "data:...;base64," prefix. PascalCase to match MessageAttachment
// (api-client.ts) so pages can assign this directly as the request body's Attachments field.
export interface AttachmentValue {
  FileName: string
  FileContent: string
}

type AttachmentPickerProps = {
  label: string
  value: AttachmentValue[]
  onChange: (files: AttachmentValue[]) => void
  disabled?: boolean
}

export function AttachmentPicker({ label, value, onChange, disabled }: AttachmentPickerProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const inputId = useId()

  async function handleFilesSelected(fileList: FileList | null) {
    if (!fileList || fileList.length === 0) return
    const added = await Promise.all(
      Array.from(fileList).map(async (file) => ({
        FileName: file.name,
        FileContent: await readFileAsBase64(file),
      })),
    )
    onChange([...value, ...added])
    if (inputRef.current) inputRef.current.value = ''
  }

  function removeAt(index: number) {
    onChange(value.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-1">
      <Label htmlFor={inputId}>{label}</Label>
      <input
        id={inputId}
        ref={inputRef}
        type="file"
        multiple
        disabled={disabled}
        onChange={(e) => void handleFilesSelected(e.target.files)}
        className="block w-full text-sm text-muted-foreground file:mr-3 file:rounded-md file:border-0 file:bg-secondary file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-secondary-foreground disabled:cursor-not-allowed disabled:opacity-50"
      />
      {value.length > 0 && (
        <ul className="space-y-1">
          {value.map((f, i) => (
            <li
              key={`${f.FileName}-${i}`}
              className="flex items-center justify-between rounded-md border border-input px-2.5 py-1 text-sm"
            >
              <span className="truncate">{f.FileName}</span>
              <Button type="button" variant="ghost" size="sm" onClick={() => removeAt(i)} disabled={disabled}>
                Remove
              </Button>
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}