import { NavLink } from "react-router-dom";
import { Sparkles } from "lucide-react";
import { cn } from "../../lib/utils";
import { NAV_ITEMS } from "./navItems";

export function Sidebar() {
  return (
    <aside className="hidden md:flex md:w-64 lg:w-72 shrink-0 flex-col border-r border-border bg-card">
      <div className="flex items-center gap-2.5 px-6 py-6">
        <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-violet text-white shadow-sm">
          <Sparkles size={18} />
        </div>
        <div className="leading-tight">
          <div className="font-semibold tracking-tight text-body">PRAGYA AI</div>
          <div className="font-mono text-[10px] uppercase tracking-wider text-muted">
            Knowledge Engine
          </div>
        </div>
      </div>

      <nav className="flex-1 space-y-1 px-3 py-2">
        {NAV_ITEMS.map(({ to, label, icon: Icon }) => (
          <NavLink
            key={to}
            to={to}
            end={to === "/"}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-xl px-3 py-2.5 text-sm font-medium transition-colors",
                isActive
                  ? "bg-violet-50 text-violet-700"
                  : "text-muted hover:bg-background hover:text-body"
              )
            }
          >
            {({ isActive }) => (
              <>
                <Icon
                  size={18}
                  className={cn(isActive ? "text-violet-700" : "text-muted")}
                />
                {label}
              </>
            )}
          </NavLink>
        ))}
      </nav>

      <div className="border-t border-border px-6 py-4">
        <div className="flex items-center gap-2">
          <span className="h-2 w-2 animate-pulse-soft rounded-full bg-teal" />
          <span className="font-mono text-xs text-muted">API · localhost:8000</span>
        </div>
      </div>
    </aside>
  );
}
