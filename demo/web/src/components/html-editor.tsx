import { useEffect } from 'react'
import { useEditor, EditorContent } from '@tiptap/react'
import StarterKit from '@tiptap/starter-kit'
import Link from '@tiptap/extension-link'
import { Label } from '@/components/ui/label'
import { cn } from '@/lib/utils'

type HtmlEditorProps = {
  label: string
  value: string
  onChange: (html: string) => void
}

function ToolbarButton({
  active,
  onClick,
  children,
}: {
  active: boolean
  onClick: () => void
  children: React.ReactNode
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={cn(
        'rounded px-2 py-1 text-xs font-medium hover:bg-muted',
        active && 'bg-primary text-primary-foreground hover:bg-primary/80',
      )}
    >
      {children}
    </button>
  )
}

// A minimal WYSIWYG editor (TipTap) whose output is the HTML sent as messageHTML — deliberately
// only the small set of formatting TNZ's email rendering realistically needs for a demo, not a
// full document editor.
export function HtmlEditor({ label, value, onChange }: HtmlEditorProps) {
  const editor = useEditor({
    extensions: [StarterKit, Link.configure({ openOnClick: false })],
    content: value,
    onUpdate: ({ editor }) => onChange(editor.getHTML()),
    editorProps: {
      attributes: {
        class: 'prose prose-sm max-w-none min-h-32 px-2.5 py-2 focus:outline-none',
      },
    },
  })

  // TipTap's `content` option only seeds the editor at mount — it doesn't react to prop changes on
  // its own. Without this, a caller that resets `value` externally (e.g. loading a template, or
  // clearing the form after submit) leaves the editor showing stale content. Compare against the
  // editor's own HTML (not a ref of the last-set value) so this doesn't fight typing: onUpdate's
  // getHTML() round-trips through TipTap's serializer, so echoing that same value back in is a
  // no-op, but an external reset always differs from what the editor currently holds. The `false`
  // second argument suppresses setContent's own onUpdate emission — without it, every external
  // reset would re-invoke onChange with a value the parent just gave us, which could confuse
  // equality-guarded onChange logic (dirty-state tracking, debounced saves) in a future caller.
  useEffect(() => {
    if (!editor) return
    if (value !== editor.getHTML()) {
      editor.commands.setContent(value, false)
    }
  }, [editor, value])

  if (!editor) return null

  return (
    <div className="space-y-1">
      <Label>{label}</Label>
      <div className="rounded-lg border border-input">
        <div className="flex flex-wrap items-center gap-1 border-b border-input p-1">
          <ToolbarButton
            active={editor.isActive('bold')}
            onClick={() => editor.chain().focus().toggleBold().run()}
          >
            Bold
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('italic')}
            onClick={() => editor.chain().focus().toggleItalic().run()}
          >
            Italic
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('strike')}
            onClick={() => editor.chain().focus().toggleStrike().run()}
          >
            Strike
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('heading', { level: 2 })}
            onClick={() => editor.chain().focus().toggleHeading({ level: 2 }).run()}
          >
            H2
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('bulletList')}
            onClick={() => editor.chain().focus().toggleBulletList().run()}
          >
            • List
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('orderedList')}
            onClick={() => editor.chain().focus().toggleOrderedList().run()}
          >
            1. List
          </ToolbarButton>
          <ToolbarButton
            active={editor.isActive('link')}
            onClick={() => {
              const url = window.prompt('URL')
              if (url) editor.chain().focus().setLink({ href: url }).run()
            }}
          >
            Link
          </ToolbarButton>
        </div>
        <EditorContent editor={editor} />
      </div>
    </div>
  )
}