import { useState, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import { type FormData } from "@/components/TravelForm"; 

export type SavedTravelPlan = {
  id: string;
  formData: FormData;
  plan: string;
};

import { Card, CardHeader, CardTitle, CardDescription, CardContent, CardFooter } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Trash2, Eye } from "lucide-react";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"

const STORAGE_KEY = "travelPlans";

const MyPlans = () => {
  const [plans, setPlans] = useState<SavedTravelPlan[]>([]);
  const navigate = useNavigate();

  useEffect(() => {
    const existingPlansRaw = localStorage.getItem(STORAGE_KEY);
    const existingPlans: SavedTravelPlan[] = existingPlansRaw ? JSON.parse(existingPlansRaw) : [];
    setPlans(existingPlans);
  }, []);

  const handleLoadPlan = (plan: SavedTravelPlan) => {
    navigate("/", { state: { id: plan.id, formData: plan.formData, plan: plan.plan } });
  };

  const handleDeletePlan = (id: string) => {
    const updatedPlans = plans.filter(p => p.id !== id);
    setPlans(updatedPlans);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(updatedPlans));
  };

  return (
    <div className="min-h-screen bg-background">
      <header className="py-6 px-4 bg-primary/5">
        <div className="container mx-auto max-w-4xl flex items-center justify-between">
          <h1 className="text-3xl font-bold text-foreground">Meus Planos Salvos</h1>
          <Button asChild variant="outline">
            <Link to="/">
              <ArrowLeft className="mr-2" />
              Voltar
            </Link>
          </Button>
        </div>
      </header>

      <main className="container mx-auto max-w-4xl px-4 py-12">
        {plans.length === 0 ? (
          <div className="text-center text-muted-foreground border border-dashed rounded-lg p-12">
            <p className="text-lg font-medium">Nenhum plano salvo ainda.</p>
            <p className="mt-2">Volte para a página inicial e gere seu primeiro plano de viagem!</p>
          </div>
        ) : (
          <div className="grid gap-6">
            {plans.map((plan) => (
              <Card key={plan.id} className="shadow-md">
                <CardHeader>
                  <CardTitle className="text-2xl">
                    Viagem para {plan.formData.destination}
                  </CardTitle>
                  <CardDescription>
                    De {plan.formData.origin} | {plan.formData.departureDate}
                    {plan.formData.returnDate && ` até ${plan.formData.returnDate}`}
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <p className="line-clamp-3 text-sm text-muted-foreground">
                    {plan.plan.split('\n').find(line => line.length > 50) || "Seu plano de viagem..."}
                  </p>
                </CardContent>
                <CardFooter className="flex justify-end gap-2">
                  <AlertDialog>
                    <AlertDialogTrigger asChild>
                      <Button variant="outline" size="sm">
                        <Trash2 className="mr-2" />
                        Excluir
                      </Button>
                    </AlertDialogTrigger>
                    <AlertDialogContent>
                      <AlertDialogHeader>
                        <AlertDialogTitle>Você tem certeza?</AlertDialogTitle>
                        <AlertDialogDescription>
                          Esta ação não pode ser desfeita. Isso excluirá permanentemente
                          seu plano de viagem salvo.
                        </AlertDialogDescription>
                      </AlertDialogHeader>
                      <AlertDialogFooter>
                        <AlertDialogCancel>Cancelar</AlertDialogCancel>
                        <AlertDialogAction onClick={() => handleDeletePlan(plan.id)}>
                          Excluir
                        </AlertDialogAction>
                      </AlertDialogFooter>
                    </AlertDialogContent>
                  </AlertDialog>
                  
                  <Button size="sm" onClick={() => handleLoadPlan(plan)}>
                    <Eye className="mr-2" />
                    Carregar e Ver
                  </Button>
                </CardFooter>
              </Card>
            ))}
          </div>
        )}
      </main>
    </div>
  );
};

export default MyPlans;