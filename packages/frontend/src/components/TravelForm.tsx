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

// Pega a data de hoje no formato "YYYY-MM-DD"
const today = new Date().toISOString().split('T')[0];

const formSchema = z.object({
  origin: z.string().min(2, "Informe a cidade de origem"),
  destination: z.string().min(2, "Informe o destino"),
  departureDate: z.string().min(1, "Selecione a data de ida")
    .refine(date => date >= today, {
      message: "A data de ida não pode ser no passado."
    }),
  returnDate: z.string().optional(),
  totalBudget: z.string().min(1, "Informe o orçamento total"),
  nightlyBudget: z.string().min(1, "Informe o orçamento por noite"),
  preferences: z.string().min(10, "Descreva suas preferências (mínimo 10 caracteres)"),
}).refine(data => {
  if (!data.returnDate) return true;
  return data.returnDate >= data.departureDate;
}, {
  message: "A data de volta deve ser igual ou depois da data de ida.",
  path: ["returnDate"], 
});

// --- MUDANÇA 1: Exportamos o type para usá-lo em outros arquivos ---
export type FormData = z.infer<typeof formSchema>;

interface TravelFormProps {
  // --- MUDANÇA 2: Atualizamos onPlanGenerated para enviar os dados do form ---
  onPlanGenerated: (plan: string, data: FormData) => void;
  isLoading: boolean;
  setIsLoading: (loading: boolean) => void;
  // Adicionamos uma prop para preencher o formulário com dados salvos
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
    watch
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    // Definimos os valores iniciais do formulário (útil para o "Notebook")
    defaultValues: initialData,
  });

  const departureDate = watch("departureDate");

  const onSubmit = async (data: FormData) => {
    setIsLoading(true);
    setTravelPlan(null); // Limpa o plano anterior
    
    let fullPlan = ""; // Acumulador para o plano completo

    // --- MUDANÇA DA MELHORIA 2 ---
    // Lê o URL do .env, com um fallback para o localhost
    const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
    // --- FIM DA MUDANÇA ---

    try {
      const response = await fetch(`${apiUrl}/generate-plan`, { // <--- URL ATUALIZADO
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      });

      if (!response.ok) {
        const errorData = await response.json(); // Tenta ler o erro como JSON
        throw new Error(errorData.error || "Falha na comunicação com o servidor");
      }

      // --- LÓGICA DE STREAMING ---
      if (!response.body) {
        throw new Error("A resposta da API não continha um corpo.");
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          break; // Stream terminada
        }
        
        const chunk = decoder.decode(value);
        fullPlan += chunk;
        setTravelPlan(fullPlan); // Atualiza o estado em tempo real
      }
      // --- FIM DA LÓGICA DE STREAMING ---

      // Quando a stream termina, guardamos o plano completo no Local Storage
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

  return (
    <Card className="p-6 shadow-[var(--shadow-elevated)]">
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* ... (O resto do seu formulário (JSX) não muda nada) ... */}
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

        {/* Step 1: Destino e Datas */}
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
                  min={departureDate}
                  {...register("returnDate")}
                  className="mt-1.5"
                />
                <p className="text-xs text-muted-foreground mt-1">Opcional</p>
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

        {/* Step 2: Orçamento */}
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

        {/* Step 3: Preferências */}
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