import { useId, useRef } from 'react'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { readFileAsBase64 } from '@/lib/file-utils'

// Voice's "message" fields (MessageToPeople, MessageToAnswerPhones, the CallRouteMessage* fields,
// EndCallMessage) are all wire-typed as plain strings, but unlike TTS's identically-named fields
// they hold base64 audio content, not literal spoken text — Voice has no text-to-speech synthesis
// step. This picker reads one file and reports its base64 content as that string value directly.
type SingleFileFieldProps = {
  label: string
  fileName: string | null
  value: string
  onChange: (fileName: string | null, base64Content: string) => void
}

export function SingleFileField({ label, fileName, value, onChange }: SingleFileFieldProps) {
  const inputRef = useRef<HTMLInputElement>(null)
  const inputId = useId()

  async function handleFileSelected(file: File | null) {
    if (!file) return
    onChange(file.name, await readFileAsBase64(file))
  }

  function clear() {
    onChange(null, '')
    if (inputRef.current) inputRef.current.value = ''
  }

  return (
    <div className="space-y-1">
      <Label htmlFor={inputId}>{label}</Label>
      {value ? (
        <div className="flex items-center justify-between rounded-md border border-input px-2.5 py-1 text-sm">
          <span className="truncate">{fileName ?? 'File selected'}</span>
          <Button type="button" variant="ghost" size="sm" onClick={clear}>
            Remove
          </Button>
        </div>
      ) : (
        <input
          id={inputId}
          ref={inputRef}
          type="file"
          onChange={(e) => void handleFileSelected(e.target.files?.[0] ?? null)}
          className="block w-full text-sm text-muted-foreground file:mr-3 file:rounded-md file:border-0 file:bg-secondary file:px-3 file:py-1.5 file:text-sm file:font-medium file:text-secondary-foreground"
        />
      )}
    </div>
  )
}