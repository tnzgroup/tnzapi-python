import { useEffect, useState, type FormEvent } from 'react'
import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Label } from '@/components/ui/label'
import { TextField, type FieldValues } from '@/components/form-fields'
import { ResponseViewer } from '@/components/response-viewer'
import { apiRequest } from '@/lib/api-client'
import {
  isRemembering,
  setRemembering,
  loadStoredSettings,
  saveSettings,
  type StoredConnectionSettings,
} from '@/lib/settings-storage'

type ConnectionSettingKey = keyof StoredConnectionSettings

// Single source of truth for the three process-wide settings' endpoints and request/response
// shapes — used by the initial load, the "remember settings" reapply-on-mount, and Save, so
// adding/renaming a setting only means editing this array plus its own JSX section, not three
// separately-hand-maintained code paths.
const CONNECTION_SETTINGS: {
  key: ConnectionSettingKey
  url: string
  toRequestBody: (value: StoredConnectionSettings[ConnectionSettingKey]) => unknown
  fromGetResponse: (data: Record<string, unknown>) => StoredConnectionSettings[ConnectionSettingKey]
}[] = [
  {
    key: 'apiUrl',
    url: '/api/settings/api-url',
    toRequestBody: (value) => ({ ApiUrl: value }),
    fromGetResponse: (data) => data.ApiUrl as string,
  },
  {
    key: 'sslVerificationEnabled',
    url: '/api/settings/ssl-verification',
    toRequestBody: (value) => ({ Enabled: value }),
    fromGetResponse: (data) => data.Enabled as boolean,
  },
  {
    key: 'allowInsecureHttp',
    url: '/api/settings/allow-insecure-http',
    toRequestBody: (value) => ({ Enabled: value }),
    fromGetResponse: (data) => data.Enabled as boolean,
  },
]

type ResultKey = ConnectionSettingKey | 'token'
type ApiResult = { status: number; data: unknown }

export default function SettingsPage() {
  const [tokenFields, setTokenFields] = useState<FieldValues>({ Token: '' })
  const [connectionSettings, setConnectionSettings] = useState<StoredConnectionSettings>({
    apiUrl: '',
    sslVerificationEnabled: true,
    allowInsecureHttp: false,
  })
  const [remember, setRemember] = useState(false)

  const [saving, setSaving] = useState(false)
  const [results, setResults] = useState<Partial<Record<ResultKey, ApiResult>>>({})

  useEffect(() => {
    let cancelled = false

    const remembering = isRemembering()
    setRemember(remembering)

    const stored = remembering ? loadStoredSettings() : null

    if (stored) {
      // Re-apply the remembered values to the backend — covers the case where the backend
      // restarted (these live in env vars / a static field, not anything persisted) since these
      // were last saved.
      setConnectionSettings(stored)
      CONNECTION_SETTINGS.forEach((cfg) => {
        apiRequest(cfg.url, { method: 'POST', body: cfg.toRequestBody(stored[cfg.key]) })
      })
      return
    }

    Promise.all(
      CONNECTION_SETTINGS.map((cfg) =>
        apiRequest<Record<string, unknown>>(cfg.url).then(
          ({ data }) => [cfg.key, cfg.fromGetResponse(data)] as const,
        ),
      ),
    ).then((pairs) => {
      if (cancelled) return
      setConnectionSettings((prev) => ({ ...prev, ...Object.fromEntries(pairs) }))
    })

    return () => {
      cancelled = true
    }
  }, [])

  function setTokenField(name: string, value: string) {
    setTokenFields((f) => ({ ...f, [name]: value }))
  }

  function handleToggleRemember(checked: boolean) {
    setRemember(checked)
    setRemembering(checked)
  }

  async function handleSave(e: FormEvent) {
    e.preventDefault()
    setSaving(true)

    const token = ((tokenFields.Token as string) ?? '').trim()

    const connectionResults = await Promise.all(
      CONNECTION_SETTINGS.map((cfg) =>
        apiRequest(cfg.url, { method: 'POST', body: cfg.toRequestBody(connectionSettings[cfg.key]) }),
      ),
    )
    // Auth Token is deliberately session-only — save it too, but only if the field isn't empty,
    // since posting an empty token would fail the backend's own validation for no reason.
    const tokenResult = token ? await apiRequest('/api/auth/token', { method: 'POST', body: { Token: token } }) : null

    setResults((r) => {
      const next = { ...r }
      CONNECTION_SETTINGS.forEach((cfg, i) => {
        next[cfg.key] = connectionResults[i]
      })
      if (tokenResult) next.token = tokenResult
      return next
    })

    if (remember) {
      saveSettings(connectionSettings)
    }

    setSaving(false)
  }

  return (
    <div className="max-w-2xl space-y-4">
      <div className="rounded border border-amber-400 bg-amber-50 p-4 text-sm text-amber-900">
        <strong>Development / demo use only.</strong> The settings below override how the backend
        connects to TNZ's API — some apply to every session on this backend instance, and some
        deliberately weaken transport security (skipping certificate validation, allowing plain
        HTTP). Do not use these in a production deployment.
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Settings</CardTitle>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSave} className="space-y-8">
            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save'}
            </Button>

            <section className="space-y-4 border-t pt-6">
              <div>
                <h2 className="font-medium">Auth Token</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Override the AuthToken used for this session, instead of the backend's
                  configured default. Scoped to your session only. Never saved to this browser,
                  even with Remember These Settings below turned on — it stays only in the
                  backend's HttpOnly session cookie, which client-side JS can't read.
                </p>
              </div>
              <TextField
                label="JWT Auth Token"
                name="Token"
                values={tokenFields}
                onChange={setTokenField}
                placeholder="eyJhbGciOi..."
                multiline
              />
              <p className="rounded border border-sky-200 bg-sky-50 p-2 text-xs text-sky-900">
                This token is held in memory only, tied to your session. If the backend process or
                Docker container restarts, it's lost and you'll need to re-enter and save it here
                again.
              </p>
              {results.token && <ResponseViewer status={results.token.status} data={results.token.data} />}
            </section>

            <section className="space-y-4 border-t pt-6">
              <div>
                <h2 className="font-medium">API URL</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Override the TNZ API base URL (defaults to https://api.tnz.co.nz). Unlike the
                  Auth Token above, <strong>this applies process-wide to the backend</strong> — it
                  affects every session connected to this backend instance, not just yours. Fine
                  for a single-developer local demo; avoid on a shared deployment.
                </p>
              </div>
              <TextField
                label="API URL"
                name="ApiUrl"
                values={{ ApiUrl: connectionSettings.apiUrl }}
                onChange={(_, value) => setConnectionSettings((s) => ({ ...s, apiUrl: value }))}
                placeholder="https://api.tnz.co.nz"
              />
              {results.apiUrl && <ResponseViewer status={results.apiUrl.status} data={results.apiUrl.data} />}
            </section>

            <section className="space-y-4 border-t pt-6">
              <div>
                <h2 className="font-medium">SSL Verification</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  When off, the backend accepts any TLS certificate from the API URL above without
                  validating it — useful for a staging server with a self-signed certificate. Has
                  no effect if the API URL is plain http://, since certificate validation only
                  happens during a TLS handshake. <strong>Process-wide</strong>, same as API URL.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <input
                  id="sslVerification"
                  type="checkbox"
                  checked={connectionSettings.sslVerificationEnabled}
                  onChange={(e) =>
                    setConnectionSettings((s) => ({ ...s, sslVerificationEnabled: e.target.checked }))
                  }
                />
                <Label htmlFor="sslVerification">Verify server certificate (recommended)</Label>
              </div>
              {results.sslVerificationEnabled && (
                <ResponseViewer status={results.sslVerificationEnabled.status} data={results.sslVerificationEnabled.data} />
              )}
            </section>

            <section className="space-y-4 border-t pt-6">
              <div>
                <h2 className="font-medium">Allow Insecure HTTP</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  The backend refuses to send the Authorization bearer token over plain http:// by
                  default. Turning this on is a separate, deliberate choice from SSL Verification
                  above — it is <strong>not</strong> inferred automatically just because the API
                  URL starts with http://, so a mistyped URL can't silently send your token in
                  cleartext. <strong>Process-wide</strong>, same as the settings above.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <input
                  id="allowInsecureHttp"
                  type="checkbox"
                  checked={connectionSettings.allowInsecureHttp}
                  onChange={(e) =>
                    setConnectionSettings((s) => ({ ...s, allowInsecureHttp: e.target.checked }))
                  }
                />
                <Label htmlFor="allowInsecureHttp">Allow plain http:// (not recommended)</Label>
              </div>
              {results.allowInsecureHttp && (
                <ResponseViewer status={results.allowInsecureHttp.status} data={results.allowInsecureHttp.data} />
              )}
            </section>

            <section className="space-y-2 border-t pt-6">
              <div>
                <h2 className="font-medium">Remember These Settings</h2>
                <p className="mt-1 text-sm text-muted-foreground">
                  Save API URL, SSL Verification, and Allow Insecure HTTP to this browser's local
                  storage on Save, and automatically re-apply them here whenever this page loads —
                  useful since the backend forgets them on restart. Does{' '}
                  <strong>not</strong> include the Auth Token above.
                </p>
              </div>
              <div className="flex items-center gap-2">
                <input
                  id="rememberSettings"
                  type="checkbox"
                  checked={remember}
                  onChange={(e) => handleToggleRemember(e.target.checked)}
                />
                <Label htmlFor="rememberSettings">Remember these settings in this browser</Label>
              </div>
            </section>

            <Button type="submit" disabled={saving}>
              {saving ? 'Saving...' : 'Save'}
            </Button>
          </form>
        </CardContent>
      </Card>
    </div>
  )
}