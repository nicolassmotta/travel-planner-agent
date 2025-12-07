import { Toaster } from "@/components/ui/toaster";
import { Toaster as Sonner } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Index from "./pages/Index";
import NotFound from "./pages/NotFound";
import MyPlans from "@/pages/MyPlans"; 
import Login from "@/pages/Login";
import Register from "@/pages/Register";

const queryClient = new QueryClient();

// ✅ PROTEÇÃO ATIVADA: Verifica se tem token
const PrivateRoute = ({ children }: { children: JSX.Element }) => {
  const token = localStorage.getItem("token");
  if (!token) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const App = () => (
  <QueryClientProvider client={queryClient}>
    <TooltipProvider>
      <Toaster />
      <Sonner />
      <BrowserRouter>
        <Routes>
          {/* Rotas Públicas */}
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />

          {/* 🔒 Rotas Privadas (Protegidas pelo PrivateRoute) */}
          <Route path="/" element={
            <PrivateRoute>
              <Index />
            </PrivateRoute>
          } />
          
          <Route path="/meus-planos" element={
            <PrivateRoute>
              <MyPlans />
            </PrivateRoute>
          } />

          <Route path="*" element={<NotFound />} />
        </Routes>
      </BrowserRouter>
    </TooltipProvider>
  </QueryClientProvider>
);

export default App;