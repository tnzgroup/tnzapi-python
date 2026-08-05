import { useState } from 'react'
import { Label } from '@/components/ui/label'
import { Input } from '@/components/ui/input'
import { Button } from '@/components/ui/button'
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select'

// Matches KeypadModel (api-client.ts's MessageKeypad) — PascalCase so pages can assign this
// directly as the request body's Keypads field. PlayFile/File are Voice-only (file-based keypad
// playback) — they have no effect on a TTS message, so TtsPage passes showVoiceFields={false} (the
// default) to hide them.
export interface KeypadValue {
  Tone: number
  Play: string
  RouteNumber: string
  PlaySection: string
  PlayFile?: string
  File?: string
}

const PLAY_SECTIONS = ['Main', 'AnswerPhone', 'WrongKey']

type KeypadEditorProps = {
  label: string
  value: KeypadValue[]
  onChange: (keypads: KeypadValue[]) => void
  showVoiceFields?: boolean
}

function emptyKeypad(): KeypadValue {
  return { Tone: 1, Play: '', RouteNumber: '', PlaySection: '', PlayFile: '', File: '' }
}

export function KeypadEditor({ label, value, onChange, showVoiceFields = false }: KeypadEditorProps) {
  // KeypadValue is sent verbatim as the request body's Keypads field (see the comment above), so a
  // stable identity for React's list reconciliation can't live on KeypadValue itself. Track ids in
  // parallel state instead of using the array index — index-as-key would misassign focus to the
  // wrong row when a keypad is removed from the middle of the list. ids stays sorted ascending
  // (append-only growth, arbitrary-index removal preserves order), so its last element is always
  // the current max — no ref/counter needed to generate the next one.
  const [ids, setIds] = useState<number[]>(() => value.map((_, i) => i))

  function addKeypad() {
    onChange([...value, emptyKeypad()])
    setIds((prev) => [...prev, (prev.at(-1) ?? -1) + 1])
  }

  function updateKeypad(index: number, patch: Partial<KeypadValue>) {
    onChange(value.map((k, i) => (i === index ? { ...k, ...patch } : k)))
  }

  function removeKeypad(index: number) {
    onChange(value.filter((_, i) => i !== index))
    setIds((prev) => prev.filter((_, i) => i !== index))
  }

  return (
    <div className="space-y-2">
      <div className="flex items-center justify-between">
        <Label>{label}</Label>
        <Button type="button" variant="outline" size="sm" onClick={addKeypad}>
          Add Keypad
        </Button>
      </div>
      {value.length > 0 && (
        <div className="space-y-2">
          {value.map((k, i) => {
            const rowId = ids[i] ?? i
            return (
            <div key={rowId} className="space-y-2 rounded-md border border-input p-2">
              <div className="grid grid-cols-[5rem_1fr_1fr_10rem_auto] items-end gap-2">
                <div className="space-y-1">
                  <Label htmlFor={`keypad-${rowId}-tone`} className="text-xs">Tone</Label>
                  <Input
                    id={`keypad-${rowId}-tone`}
                    type="number"
                    value={k.Tone}
                    onChange={(e) => updateKeypad(i, { Tone: Number(e.target.value) })}
                  />
                </div>
                <div className="space-y-1">
                  <Label htmlFor={`keypad-${rowId}-play`} className="text-xs">Play</Label>
                  <Input id={`keypad-${rowId}-play`} value={k.Play} onChange={(e) => updateKeypad(i, { Play: e.target.value })} />
                </div>
                <div className="space-y-1">
                  <Label htmlFor={`keypad-${rowId}-route-number`} className="text-xs">Route Number</Label>
                  <Input id={`keypad-${rowId}-route-number`} value={k.RouteNumber} onChange={(e) => updateKeypad(i, { RouteNumber: e.target.value })} />
                </div>
                <div className="space-y-1">
                  <Label htmlFor={`keypad-${rowId}-play-section`} className="text-xs">Play Section</Label>
                  <Select
                    value={k.PlaySection}
                    onValueChange={(v) => v !== null && updateKeypad(i, { PlaySection: v })}
                  >
                    <SelectTrigger id={`keypad-${rowId}-play-section`}>
                      <SelectValue placeholder="(none)" />
                    </SelectTrigger>
                    <SelectContent>
                      {PLAY_SECTIONS.map((section) => (
                        <SelectItem key={section} value={section}>
                          {section}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
                <Button type="button" variant="ghost" size="sm" onClick={() => removeKeypad(i)}>
                  Remove
                </Button>
              </div>
              {showVoiceFields && (
                <div className="grid grid-cols-2 gap-2">
                  <div className="space-y-1">
                    <Label htmlFor={`keypad-${rowId}-play-file`} className="text-xs">Play File</Label>
                    <Input id={`keypad-${rowId}-play-file`} value={k.PlayFile ?? ''} onChange={(e) => updateKeypad(i, { PlayFile: e.target.value })} />
                  </div>
                  <div className="space-y-1">
                    <Label htmlFor={`keypad-${rowId}-file`} className="text-xs">File</Label>
                    <Input id={`keypad-${rowId}-file`} value={k.File ?? ''} onChange={(e) => updateKeypad(i, { File: e.target.value })} />
                  </div>
                </div>
              )}
            </div>
            )
          })}
        </div>
      )}
    </div>
  )
}