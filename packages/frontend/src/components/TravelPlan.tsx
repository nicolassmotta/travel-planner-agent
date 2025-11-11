import { Card } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { Button } from "@/components/ui/button";
import { Download, Share2, FileText } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import ReactMarkdown from "react-markdown"; 
import { useRef } from "react"; 

import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { cn } from "@/lib/utils";

interface TravelPlanProps {
  plan: string | null;
  isLoading: boolean;
}

function parsePlanToSections(plan: string) {
  const sections = plan.split('### '); 
  const intro = sections[0].trim(); 
  
  const mappedSections = sections.slice(1).map((sectionText) => {
    const parts = sectionText.split('\n'); 
    const title = parts[0].trim(); 
    const content = parts.slice(1).join('\n').trim();
    return { title, content };
  });

  return { intro, sections: mappedSections };
}


const TravelPlan = ({ plan, isLoading }: TravelPlanProps) => {
  const { toast } = useToast();
  const planContentRef = useRef<HTMLDivElement>(null);
  const handleDownload = async () => {
    if (!plan) {
      toast({ title: "Erro ao baixar", description: "Não há plano para baixar.", variant: "destructive" });
      return;
    }
    toast({ title: "Gerando PDF..." });

    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/download-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan: plan }) 
      });

      if (!response.ok) {
        throw new Error("Falha ao gerar o PDF no servidor.");
      }

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = "plano-de-viagem.pdf";
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error("Erro ao baixar PDF:", error);
      toast({ title: "Erro ao baixar PDF", description: (error as Error).message, variant: "destructive" });
    }
  };
  // --- FIM DA ATUALIZAÇÃO ---

  const handleShare = async () => {
    if (!plan) return;
    
    if (navigator.share) {
      try {
        await navigator.share({ title: 'Meu Plano de Viagem', text: plan });
      } catch (err) { console.error('Erro ao compartilhar:', err); }
    } else {
      navigator.clipboard.writeText(plan);
      toast({ title: "Copiado!", description: "Plano copiado para a área de transferência" });
    }
  };

  if (isLoading && !plan) {
    return (
      <Card className="p-6 shadow-lg">
        <div className="space-y-4">
          <Skeleton className="h-8 w-3/4" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-full" />
          <Skeleton className="h-4 w-5/6" />
          <div className="pt-4">
            <Skeleton className="h-6 w-1/2 mb-3" />
            <Skeleton className="h-20 w-full" />
          </div>
        </div>
      </Card>
    );
  }

  if (!plan) {
    return (
      <Card className="p-6 shadow-lg h-full min-h-[400px] flex items-center justify-center border-dashed">
        <div className="text-center space-y-3">
          <div className="w-16 h-16 rounded-full bg-muted mx-auto flex items-center justify-center">
            <FileText className="w-8 h-8 text-muted-foreground" />
          </div>
          <div>
            <p className="text-sm font-medium text-foreground">Nenhum plano gerado ainda</p>
            <p className="text-xs text-muted-foreground mt-1">
              Preencha o formulário para começar
            </p>
          </div>
        </div>
      </Card>
    );
  }

  const { intro, sections } = parsePlanToSections(plan);

  return (
    <Card className="shadow-lg">
      <div className="flex gap-2 p-4 border-b">
        <Button 
          variant="outline" 
          size="sm"
          onClick={handleDownload}
          className="flex-1"
          disabled={isLoading || !plan} 
        >
          <Download className="w-4 h-4 mr-2" />
          Baixar PDF
        </Button>
        <Button 
          variant="outline" 
          size="sm"
          onClick={handleShare}
          className="flex-1"
          disabled={isLoading || !plan} 
        >
          <Share2 className="w-4 h-4 mr-2" />
          Compartilhar
        </Button>
      </div>

      {/* A div de referência não é mais necessária para o PDF, mas mantemos para o layout */}
      <div ref={planContentRef} className="p-6">
        <div className="prose prose-sm max-w-none dark:prose-invert">
          <ReactMarkdown
            components={{
              a: ({ node, ...props }) => (
                <a {...props} target="_blank" rel="noopener noreferrer" />
              ),
            }}
          >
            {intro}
          </ReactMarkdown>
        </div>

        <Accordion type="multiple" defaultValue={sections.map(s => s.title)} className="w-full mt-4">
          {sections.map((section, index) => (
            <AccordionItem value={section.title} key={index} className={cn(index === 0 && "border-t")}>
              <AccordionTrigger className="text-base font-bold text-left">
                {section.title.replace(/\*/g, '')}
              </AccordionTrigger>
              <AccordionContent>
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <ReactMarkdown
                    components={{
                      a: ({ node, ...props }) => (
                        <a {...props} target="_blank" rel="noopener noreferrer" />
                      ),
                    }}
                  >
                    {section.content}
                  </ReactMarkdown>
                </div>
              </AccordionContent>
            </AccordionItem>
          ))}
        </Accordion>
      </div>
    </Card>
  );
};

export default TravelPlan;