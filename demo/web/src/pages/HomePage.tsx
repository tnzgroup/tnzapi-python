import { Link } from "react-router-dom";
import { NAV_SECTIONS } from "@/components/layout/nav-items";

export default function HomePage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-2xl font-semibold">TNZAPI Demo</h1>
        <p className="text-sm text-muted-foreground">
          Every card below exercises one operation of the TNZAPI.NET SDK end-to-end.
        </p>
      </div>
      {NAV_SECTIONS.map((section) => (
        <div key={section.title}>
          <h2 className="mb-2 font-medium">{section.title}</h2>
          <div className="grid grid-cols-2 gap-3 sm:grid-cols-4">
            {section.items.map((item) => (
              <Link
                key={item.href}
                to={item.href}
                className="rounded border p-3 text-sm hover:bg-muted"
              >
                {item.label}
              </Link>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}