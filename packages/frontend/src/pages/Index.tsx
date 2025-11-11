import { useState, useEffect } from "react";
import { Plane, Library, Sparkles } from "lucide-react";
import TravelForm, { type FormData } from "@/components/TravelForm";
import TravelPlan from "@/components/TravelPlan";
import { Link, useLocation } from "react-router-dom";
import { Button } from "@/components/ui/button";
import { type SavedTravelPlan } from "./MyPlans";
import { ThemeToggle } from "@/components/ThemeToggle"; // Importa o botão de tema

const STORAGE_KEY = "travelPlans";

const Index = () => {
  const [travelPlan, setTravelPlan] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [initialData, setInitialData] = useState<FormData | undefined>(undefined);
  const [currentPlanId, setCurrentPlanId] = useState<string | null>(null);
  
  const location = useLocation();

  useEffect(() => {
    // Carrega o plano vindo da página "Meus Planos"
    if (location.state?.formData) {
      setInitialData(location.state.formData);
      setTravelPlan(location.state.plan);
      setCurrentPlanId(location.state.id);
    } else {
      // Ou carrega o último plano do Local Storage
      const existingPlansRaw = localStorage.getItem(STORAGE_KEY);
      const existingPlans: SavedTravelPlan[] = existingPlansRaw ? JSON.parse(existingPlansRaw) : [];
      if (existingPlans.length > 0) {
        setTravelPlan(existingPlans[0].plan);
        setInitialData(existingPlans[0].formData);
        setCurrentPlanId(existingPlans[0].id);
      }
    }
  }, [location.state]);

  const handlePlanGenerated = (plan: string, data: FormData) => {
    setTravelPlan(plan);
    const newPlanId = new Date().toISOString();

    try {
      const newPlan: SavedTravelPlan = { id: newPlanId, formData: data, plan: plan };
      const existingPlansRaw = localStorage.getItem(STORAGE_KEY);
      const existingPlans: SavedTravelPlan[] = existingPlansRaw ? JSON.parse(existingPlansRaw) : [];
      const updatedPlans = [newPlan, ...existingPlans];
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedPlans));
      setCurrentPlanId(newPlanId);

    } catch (error) {
      console.error("Falha ao salvar plano no Local Storage:", error);
    }
  };

  return (
    // Layout principal da aplicação
    <div className="flex flex-col min-h-screen bg-muted/20 dark:bg-gray-950">
      
      {/* 1. O NOVO CABEÇALHO (NAVBAR) */}
      <header className="sticky top-0 z-50 w-full border-b bg-background shadow-sm">
        <div className="container mx-auto max-w-7xl px-4 h-16 flex items-center justify-between">
          
          {/* Título do App */}
          <Link to="/" className="flex items-center gap-2">
            <div className="p-2 bg-primary rounded-lg">
              <Plane className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-xl font-bold text-foreground">
              Travel Planner
            </span>
          </Link>

          {/* Botões de Ação */}
          <div className="flex items-center gap-2">
            <Button asChild variant="ghost" className="text-muted-foreground">
              <Link to="/meus-planos">
                <Library className="w-4 h-4 mr-2" />
                Meus Planos
              </Link>
            </Button>
            <ThemeToggle />
          </div>
        </div>
      </header>

      {/* 2. O CONTEÚDO PRINCIPAL */}
      <main className="flex-1 container mx-auto max-w-7xl px-4 py-8 md:py-12">
        <div className="grid lg:grid-cols-2 gap-8 items-start">
          
          {/* Coluna da Esquerda (Formulário) */}
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-foreground mb-1">
                Planeje sua Viagem
              </h2>
              <p className="text-muted-foreground">
                {initialData ? "Plano salvo carregado. Edite ou gere novamente." : "Preencha os detalhes e deixe a IA criar seu roteiro."}
              </p>
            </div>
            <TravelForm 
              onPlanGenerated={handlePlanGenerated}
              isLoading={isLoading}
              setIsLoading={setIsLoading}
              key={currentPlanId} 
              initialData={initialData}
              setTravelPlan={setTravelPlan}
            />
          </div>

          {/* Coluna da Direita (Plano) */}
          <div>
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-foreground mb-1">
                Seu Plano de Viagem
              </h2>
              <p className="text-muted-foreground">
                {travelPlan ? "Seu itinerário personalizado está pronto!" : "Aguardando informações..."}
              </p>
            </div>
            <TravelPlan plan={travelPlan} isLoading={isLoading} />
          </div>
        </div>
      </main>

      {/* Footer Fino */}
      <footer className="border-t py-6 px-4">
        <div className="container mx-auto max-w-7xl text-center text-muted-foreground text-sm">
          Powered by Google AI & SerpApi • © 2025
        </div>
      </footer>
    </div>
  );
};

export default Index;