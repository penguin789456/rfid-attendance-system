import { Outlet } from "react-router-dom";
import { SidebarProvider, SidebarTrigger } from "@/components/ui/sidebar";
import { AppSidebar } from "./AppSidebar";
import { Toaster } from "@/components/ui/sonner";

export function AppLayout() {
  return (
    <SidebarProvider>
      <AppSidebar />
      <main className="flex-1 overflow-auto">
        <div className="flex items-center gap-2 border-b px-6 py-3">
          <SidebarTrigger />
        </div>
        <div className="p-6">
          <Outlet />
        </div>
      </main>
      <Toaster />
    </SidebarProvider>
  );
}
