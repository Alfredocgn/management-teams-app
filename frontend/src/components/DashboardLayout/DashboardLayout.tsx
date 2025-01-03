import { ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import { useSubscriptionStatus } from "../../hooks/useSubscriptionStatus";

interface DashboardLayoutProps {
  children: ReactNode;
}

// Se considera que seria util agregar barra de busqueda y filtros
// Vista del perfil imagen del perfil, datos de la persona loggeada

export const DashboardLayout = ({ children }: DashboardLayoutProps) => {
  const navigate = useNavigate();
  const { isSubscribed } = useSubscriptionStatus();
  const handleLogout = () => {
    localStorage.removeItem("token");
    window.location.href = "/login";
  };

  return (
    <div className="min-h-screen bg-gray-100">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center justify-between w-full">
              <h2>QOOP Managment Dashboard</h2>
              <div className="flex gap-2">
                {isSubscribed ? (
                  <p className="text-green-500">Subscription Active</p>
                ) : (
                  <button
                    className="text-red-500"
                    onClick={() => navigate("/dashboard/subscription")}>
                    Subscribe
                  </button>
                )}
                <button onClick={() => navigate("/dashboard/projects")}>
                  Projects
                </button>
                <button onClick={handleLogout}>Logout</button>
              </div>
            </div>
          </div>
        </div>
      </nav>
      <main className="py-10">
        <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">{children}</div>
      </main>
    </div>
  );
};
