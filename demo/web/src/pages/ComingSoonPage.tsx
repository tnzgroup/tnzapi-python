type ComingSoonPageProps = {
  title: string;
};

export default function ComingSoonPage({ title }: ComingSoonPageProps) {
  return (
    <div className="max-w-2xl space-y-2">
      <h1 className="text-xl font-semibold">{title}</h1>
      <p className="text-sm text-muted-foreground">
        Not implemented yet — this is a later phase of the TNZAPI.NET.Demo rollout.
      </p>
    </div>
  );
}