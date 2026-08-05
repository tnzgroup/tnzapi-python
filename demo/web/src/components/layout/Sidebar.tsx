import { Link, useLocation } from "react-router-dom";
import { NAV_SECTIONS } from "./nav-items";

export function Sidebar() {
  const location = useLocation();
  return (
    <nav className="w-64 shrink-0 border-r bg-muted/30 p-4 space-y-6 overflow-y-auto">
      <Link to="/" className="block text-lg font-semibold mb-2">
        TNZAPI Demo
      </Link>
      {NAV_SECTIONS.map((section) => (
        <div key={section.title}>
          <div className="text-xs font-medium uppercase text-muted-foreground mb-1">
            {section.title}
          </div>
          <ul className="space-y-1">
            {section.items.map((item) => {
              const active = location.pathname === item.href;
              return (
                <li key={item.href}>
                  <Link
                    to={item.href}
                    className={`block rounded px-2 py-1 text-sm ${
                      active ? "bg-primary text-primary-foreground" : "hover:bg-muted"
                    }`}
                  >
                    {item.label}
                  </Link>
                </li>
              );
            })}
          </ul>
        </div>
      ))}
    </nav>
  );
}