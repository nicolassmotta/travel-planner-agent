import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import * as z from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Card } from "@/components/ui/card";
import { Calendar, Loader2, MapPin, DollarSign, Sparkles } from "lucide-react";
import { useToast } from "@/hooks/use-toast";

const today = new Date().toISOString().split('T')[0];

// --- MELHORIA 1: Tags para preenchimento rápido ---
const INTEREST_TAGS = [
  "Praia 🏖️", "História 🏛️", "Gastronomia 🍷", "Natureza 🌲", 
  "Aventura 🧗", "Relaxamento 🧘", "Compras 🛍️", "Vida Noturna 🎉",
  "Museus 🖼️", "Família 👨‍👩‍👧‍👦"
];

const formSchema = z.object({
  origin: z.string().min(2, "Informe a cidade de origem"),
  destination: z.string().min(2, "Informe o destino"),
  departureDate: z.string().min(1, "Selecione a data de ida")
    .refine(date => date >= today, {
      message: "A data de ida não pode ser no passado."
    }),
  returnDate: z.string().optional(),
  totalBudget: z.preprocess(
    (val) => (val === "" ? 0 : Number(val)), 
    z.number().min(0, "O orçamento deve ser um número positivo")
  ),
  nightlyBudget: z.preprocess(
    (val) => (val === "" ? 0 : Number(val)), 
    z.number().min(0, "O orçamento deve ser um número positivo")
  ),
  preferences: z.string().min(10, "Descreva suas preferências (mínimo 10 caracteres)"),
}).refine(data => {
  if (!data.returnDate) return true;
  return data.returnDate >= data.departureDate;
}, {
  message: "A data de volta deve ser igual ou depois da data de ida.",
  path: ["returnDate"], 
});

export type FormData = z.infer<typeof formSchema>;

interface TravelFormProps {
  onPlanGenerated: (plan: string, data: FormData) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  initialData?: FormData;
  setTravelPlan: React.Dispatch<React.SetStateAction<string | null>>;
}

const TravelForm = ({ 
  onPlanGenerated, 
  isLoading, 
  setIsLoading, 
  initialData,
  setTravelPlan
}: TravelFormProps) => {
  const { toast } = useToast();
  const [step, setStep] = useState(1);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue // Adicionado para permitir atualização via botões
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: initialData || {
      origin: '',
      destination: '',
      departureDate: '',
      returnDate: '',
      totalBudget: 0,
      nightlyBudget: 0,
      preferences: '',
    },
  });

  const departureDate = watch("departureDate");
  const currentPreferences = watch("preferences"); // Observar para adicionar vírgula corretamente

  const onSubmit = async (data: FormData) => {
    setIsLoading(true);
    setTravelPlan(null);
    
    let fullPlan = ""; 

    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";

    try {
      const response = await fetch(`${apiUrl}/generate-plan`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Falha na comunicação com o servidor");
      }

      if (!response.body) {
        throw new Error("A resposta da API não continha um corpo.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break;
        }
        
        const chunk = decoder.decode(value);
        fullPlan += chunk;
        setTravelPlan(fullPlan);
      }

      onPlanGenerated(fullPlan, data); 
      
      toast({
        title: "Plano gerado com sucesso!",
        description: "Confira seu itinerário personalizado ao lado",
      });

    } catch (error) {
      console.error("Erro ao gerar plano:", error);
      toast({
        title: "Erro ao gerar plano",
        description: error instanceof Error ? error.message : "Por favor, tente novamente",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  // Função auxiliar para adicionar tags
  const handleAddTag = (tag: string) => {
    const separator = currentPreferences && currentPreferences.length > 0 ? ", " : "";
    setValue("preferences", currentPreferences + separator + tag, { 
      shouldValidate: true, 
      shouldDirty: true 
    });
  };

  return (
    <Card className="p-6 shadow-[var(--shadow-elevated)]">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Step Indicator */}
        <div className="flex items-center justify-between mb-8">
          {[1, 2, 3].map((s) => (
            <div key={s} className="flex items-center flex-1">
              <div className={`w-10 h-10 rounded-full flex items-center justify-center font-semibold transition-all ${
                step >= s ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'
              }`}>
                {s}
              </div>
              {s < 3 && <div className={`flex-1 h-1 mx-2 rounded ${step > s ? 'bg-primary' : 'bg-muted'}`} />}
            </div>
          ))}
        </div>
        {step === 1 && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <div>
              <Label htmlFor="origin" className="flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                Cidade de Origem
              </Label>
              <Input 
                id="origin"
                placeholder="Ex: São Paulo"
                {...register("origin")}
                className="mt-1.5"
              />
              {errors.origin && (
                <p className="text-sm text-destructive mt-1">{errors.origin.message}</p>
              )}
            </div>

            <div>
              <Label htmlFor="destination" className="flex items-center gap-2">
                <MapPin className="w-4 h-4" />
                Destino
              </Label>
              <Input 
                id="destination"
                placeholder="Ex: Rio de Janeiro"
                {...register("destination")}
                className="mt-1.5"
              />
              {errors.destination && (
                <p className="text-sm text-destructive mt-1">{errors.destination.message}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <Label htmlFor="departureDate" className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Data de Ida
                </Label>
                <Input 
                  id="departureDate"
                  type="date"
                  min={today}
                  {...register("departureDate")}
                  className="mt-1.5"
                />
                {errors.departureDate && (
                  <p className="text-sm text-destructive mt-1">{errors.departureDate.message}</p>

                )}
              </div>

              <div>
                <Label htmlFor="returnDate" className="flex items-center gap-2">
                  <Calendar className="w-4 h-4" />
                  Data de Volta
                </Label>
                <Input 
                  id="returnDate"
                  type="date"
                  min={departureDate || today}
                  {...register("returnDate")}
                  className="mt-1.5"
                />
                {errors.returnDate && (
                  <p className="text-sm text-destructive mt-1">{errors.returnDate.message}</p>
                )}
              </div>
            </div>

            <Button 
              type="button" 
              onClick={() => setStep(2)}
              className="w-full"
            >
              Próximo
            </Button>
          </div>
        )}
        {step === 2 && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <div>
              <Label htmlFor="totalBudget" className="flex items-center gap-2">
                <DollarSign className="w-4 h-4" />
                Orçamento Total (R$)
              </Label>
              <Input 
                id="totalBudget"
                type="number"
                placeholder="Ex: 5000"
                {...register("totalBudget")}
                className="mt-1.5"
              />
              {errors.totalBudget && (
                <p className="text-sm text-destructive mt-1">{errors.totalBudget.message}</p>
              )}
            </div>

            <div>
              <Label htmlFor="nightlyBudget" className="flex items-center gap-2">
                <DollarSign className="w-4 h-4" />
                Orçamento por Noite de Hotel (R$)
              </Label>
              <Input 
                id="nightlyBudget"
                type="number"
                placeholder="Ex: 300"
                {...register("nightlyBudget")}
                className="mt-1.5"
              />
              {errors.nightlyBudget && (
                <p className="text-sm text-destructive mt-1">{errors.nightlyBudget.message}</p>
              )}
              <p className="text-xs text-muted-foreground mt-1">
                Valor máximo que você gostaria de gastar por noite
              </p>
            </div>

            <div className="flex gap-2">
              <Button 
                type="button" 
                variant="outline"
                onClick={() => setStep(1)}
                className="flex-1"
              >
                Voltar
              </Button>
              <Button 
                type="button" 
                onClick={() => setStep(3)}
                className="flex-1"
              >
                Próximo
              </Button>
            </div>
          </div>
        )}
        {step === 3 && (
          <div className="space-y-4 animate-in fade-in duration-300">
            <div>
              <Label htmlFor="preferences" className="flex items-center gap-2">
                <Sparkles className="w-4 h-4" />
                Preferências e Interesses
              </Label>
              <Textarea 
                id="preferences"
                placeholder="Ex: Gosto de praias, gastronomia local, história e cultura. Prefiro atividades ao ar livre durante o dia."
                rows={6}
                {...register("preferences")}
                className="mt-1.5 resize-none"
              />
              
              {/* --- Início das Tags Rápidas --- */}
              <div className="mt-3">
                <p className="text-xs text-muted-foreground mb-2">Sugestões rápidas (clique para adicionar):</p>
                <div className="flex flex-wrap gap-2">
                  {INTEREST_TAGS.map((tag) => (
                    <Button
                      key={tag}
                      type="button"
                      variant="outline"
                      size="sm"
                      className="h-7 text-xs bg-background hover:bg-primary/10 hover:text-primary border-dashed"
                      onClick={() => handleAddTag(tag)}
                    >
                      {tag}
                    </Button>
                  ))}
                </div>
              </div>
              {/* --- Fim das Tags Rápidas --- */}

              {errors.preferences && (
                <p className="text-sm text-destructive mt-1">{errors.preferences.message}</p>
              )}
              <p className="text-xs text-muted-foreground mt-1">
                Descreva o tipo de experiências que você busca nesta viagem
              </p>
            </div>

            <div className="flex gap-2">
              <Button 
                type="button" 
                variant="outline"
                onClick={() => setStep(2)}
                className="flex-1"
              >
                Voltar
              </Button>
              <Button 
                type="submit"
                disabled={isLoading}
                className="flex-1"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Gerando...
                  </>
                ) : (
                  <>
                    <Sparkles className="mr-2 h-4 w-4" />
                    Gerar Plano
                  </>
                )}
              </Button>
            </div>
          </div>
        )}
      </form>
    </Card>
  );
};
  
export default TravelForm;