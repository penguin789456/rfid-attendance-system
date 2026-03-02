import { createBrowserRouter, Navigate, RouterProvider } from "react-router-dom";
import { AppLayout } from "@/components/layout/AppLayout";
import { DepartmentsPage } from "@/pages/DepartmentsPage";
import { EmployeesPage } from "@/pages/EmployeesPage";
import { SchedulesPage } from "@/pages/SchedulesPage";
import { FlexSettingsPage } from "@/pages/FlexSettingsPage";
import { AttendancePage } from "@/pages/AttendancePage";

const router = createBrowserRouter([
  {
    path: "/",
    element: <AppLayout />,
    children: [
      { index: true, element: <Navigate to="/departments" replace /> },
      { path: "departments", element: <DepartmentsPage /> },
      { path: "employees", element: <EmployeesPage /> },
      { path: "schedules", element: <SchedulesPage /> },
      { path: "flex-settings", element: <FlexSettingsPage /> },
      { path: "attendance", element: <AttendancePage /> },
    ],
  },
]);

export default function App() {
  return <RouterProvider router={router} />;
}
