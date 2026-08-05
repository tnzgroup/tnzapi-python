type ResponseViewerProps = {
  status: number | null;
  data: unknown;
};

export function ResponseViewer({ status, data }: ResponseViewerProps) {
  if (status === null) return null;
  // status 0 means apiRequest() couldn't complete the request at all (network failure) — treat it
  // as an error, same as any 4xx/5xx.
  const isError = status === 0 || status >= 400;
  return (
    <div
      className={`mt-4 rounded border p-4 ${
        isError ? "border-red-400 bg-red-50" : "border-green-400 bg-green-50"
      }`}
    >
      <div className={`mb-2 text-sm font-medium ${isError ? "text-red-700" : "text-green-700"}`}>
        {status === 0 ? "Network error" : isError ? `Error (HTTP ${status})` : `Success (HTTP ${status})`}
      </div>
      <pre className="overflow-x-auto whitespace-pre-wrap text-xs">
        {JSON.stringify(data, null, 2)}
      </pre>
    </div>
  );
}