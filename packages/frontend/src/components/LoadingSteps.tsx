import { useState, useEffect } from "react";
import { CheckCircle2, Circle, Loader2 } from "lucide-react";
import { Card } from "@/components/ui/card";

const STEPS = [
  "Decolando o agente de IA...",
  "Pesquisando melhores voos...",
  "Verificando disponibilidade de hotéis...",
  "Buscando atrações locais...",
  "Compilando seu roteiro personalizado...",
];

export default function LoadingSteps() {
  const [currentStep, setCurrentStep] = useState(0);

  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentStep((prev) => (prev < STEPS.length - 1 ? prev + 1 : prev));
    }, 3500); // Muda o texto a cada 3.5 segundos

    return () => clearInterval(interval);
  }, []);

  return (
    <Card className="p-8 shadow-lg flex flex-col items-center justify-center space-y-6 min-h-[400px]">
      <div className="relative">
        <div className="absolute inset-0 bg-primary/20 blur-xl rounded-full animate-pulse" />
        <Loader2 className="h-16 w-16 animate-spin text-primary relative z-10" />
      </div>
      
      <div className="space-y-4 w-full max-w-md">
        {STEPS.map((step, index) => (
          <div 
            key={index} 
            className={`flex items-center gap-3 transition-all duration-500 ${
              index === currentStep 
                ? "opacity-100 scale-105 translate-x-2" 
                : index < currentStep 
                  ? "opacity-50" 
                  : "opacity-30"
            }`}
          >
            {index < currentStep ? (
              <CheckCircle2 className="h-5 w-5 text-green-500" />
            ) : index === currentStep ? (
              <Circle className="h-5 w-5 text-primary animate-pulse" />
            ) : (
              <Circle className="h-5 w-5 text-muted-foreground" />
            )}
            <span className={`text-sm font-medium ${index === currentStep ? "text-primary" : "text-muted-foreground"}`}>
              {step}
            </span>
          </div>
        ))}
      </div>
    </Card>
  );
}