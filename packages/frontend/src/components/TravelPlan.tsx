import { Card } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Download, Share2, FileText, MapPin } from "lucide-react";
import { useToast } from "@/hooks/use-toast";
import ReactMarkdown from "react-markdown"; 
import {
  Accordion,
  AccordionContent,
  AccordionItem,
  AccordionTrigger,
} from "@/components/ui/accordion";
import { cn } from "@/lib/utils";
import { Badge } from "@/components/ui/badge";

// Importa os novos componentes
import DestinationMap from "./DestinationMap";
import LoadingSteps from "./LoadingSteps";

interface TravelPlanProps {
  plan: string | null;
  isLoading: boolean;
  destination?: string; // Adicionei esta prop opcional para o mapa saber o que buscar
}

function parsePlanToSections(plan: string) {
  // Divide o markdown pelos títulos de nível 3 (###) usados pelo agente
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

const TravelPlan = ({ plan, isLoading, destination }: TravelPlanProps) => {
  const { toast } = useToast();

  const handleDownload = async () => {
    if (!plan) return;
    toast({ title: "Gerando PDF..." });

    try {
      const apiUrl = import.meta.env.VITE_API_URL || "http://localhost:8000";
      const response = await fetch(`${apiUrl}/download-plan`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ plan: plan }) 
      });

      if (!response.ok) throw new Error("Falha ao gerar o PDF");

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `Viagem-${destination || 'Plano'}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);

    } catch (error) {
      console.error(error);
      toast({ title: "Erro", description: "Não foi possível baixar o PDF.", variant: "destructive" });
    }
  };

  const handleShare = async () => {
    if (!plan) return;
    if (navigator.share) {
      try { await navigator.share({ title: 'Meu Plano de Viagem', text: plan }); } 
      catch (err) { console.error(err); }
    } else {
      navigator.clipboard.writeText(plan);
      toast({ title: "Copiado!", description: "Plano copiado para a área de transferência" });
    }
  };

  // 1. Mostra o Loading Rico se estiver carregando e não tiver plano ainda
  if (isLoading && !plan) {
    return <LoadingSteps />;
  }

  // 2. Estado vazio inicial
  if (!plan) {
    return (
      <Card className="p-6 shadow-lg h-full min-h-[400px] flex items-center justify-center border-dashed">
        <div className="text-center space-y-3">
          <div className="w-16 h-16 rounded-full bg-muted mx-auto flex items-center justify-center">
            <FileText className="w-8 h-8 text-muted-foreground" />
          </div>
          <div>
            <p className="text-sm font-medium text-foreground">Seu roteiro aparecerá aqui</p>
            <p className="text-xs text-muted-foreground mt-1">
              Preencha os dados ao lado para começar a mágica ✨
            </p>
          </div>
        </div>
      </Card>
    );
  }

  const { intro, sections } = parsePlanToSections(plan);

  // Extrai o nome da cidade do título ou usa a prop
  const mapQuery = destination || (sections.length > 0 ? sections[0].title.split(' ')[0] : "");

  return (
    <Card className="shadow-lg overflow-hidden border-t-4 border-t-primary">
      {/* Cabeçalho de Ações */}
      <div className="flex gap-2 p-4 border-b bg-muted/30">
        <Button variant="outline" size="sm" onClick={handleDownload} className="flex-1" disabled={isLoading}>
          <Download className="w-4 h-4 mr-2" />
          PDF
        </Button>
        <Button variant="outline" size="sm" onClick={handleShare} className="flex-1" disabled={isLoading}>
          <Share2 className="w-4 h-4 mr-2" />
          Compartilhar
        </Button>
      </div>

      <div className="p-6 space-y-6">
        {/* Mapa do Destino */}
        {mapQuery && (
          <div className="animate-in fade-in slide-in-from-bottom-4 duration-700">
             <div className="flex items-center gap-2 mb-2">
                <Badge variant="outline" className="px-3 py-1"><MapPin className="w-3 h-3 mr-1"/> {mapQuery}</Badge>
             </div>
             <DestinationMap destination={mapQuery} />
          </div>
        )}

        {/* Introdução do Plano */}
        <div className="prose prose-sm max-w-none dark:prose-invert animate-in fade-in duration-500">
          <ReactMarkdown components={MarkdownComponents}>
            {intro}
          </ReactMarkdown>
        </div>

        {/* Seções do Plano (Accordion) */}
        <Accordion type="multiple" defaultValue={sections.map(s => s.title)} className="w-full">
          {sections.map((section, index) => (
            <AccordionItem value={section.title} key={index} className="border-b border-muted last:border-0">
              <AccordionTrigger className="text-lg font-semibold hover:no-underline hover:bg-muted/50 px-2 rounded-md">
                <div className="flex items-center gap-2">
                  {getIconForSection(section.title)}
                  {section.title.replace(/\*/g, '').replace(/^[^\w]+/, '')}
                </div>
              </AccordionTrigger>
              <AccordionContent className="px-2 pt-4 pb-6">
                <div className="prose prose-sm max-w-none dark:prose-invert">
                  <ReactMarkdown components={MarkdownComponents}>
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

// --- Helpers e Componentes de Estilo ---

// Mapeia ícones baseados no título da seção (truque visual)
const getIconForSection = (title: string) => {
  const t = title.toLowerCase();
  if (t.includes('voo') || t.includes('aéreo')) return <span className="text-2xl">✈️</span>;
  if (t.includes('hotel') || t.includes('hospeda')) return <span className="text-2xl">🏨</span>;
  if (t.includes('atividade') || t.includes('roteiro')) return <span className="text-2xl">🗺️</span>;
  if (t.includes('clima') || t.includes('tempo')) return <span className="text-2xl">🌦️</span>;
  if (t.includes('gastronomia') || t.includes('restaurante')) return <span className="text-2xl">🍽️</span>;
  return <span className="text-2xl">✨</span>;
};

// Componentes customizados para o Markdown (Imagens bonitas, Links, etc)
const MarkdownComponents = {
  // Estiliza imagens para serem responsivas e bonitas
  img: ({ node, ...props }: any) => (
    <div className="my-6 relative group overflow-hidden rounded-xl shadow-md border hover:shadow-xl transition-all">
      <img 
        {...props} 
        className="w-full h-auto object-cover max-h-[400px] transform transition-transform duration-700 group-hover:scale-105" 
        loading="lazy"
      />
      {props.alt && (
        <div className="absolute bottom-0 left-0 right-0 bg-black/60 text-white p-2 text-xs opacity-0 group-hover:opacity-100 transition-opacity">
          {props.alt}
        </div>
      )}
    </div>
  ),
  // Estiliza links
  a: ({ node, ...props }: any) => (
    <a 
      {...props} 
      className="text-primary font-medium hover:underline underline-offset-4 transition-colors" 
      target="_blank" 
      rel="noopener noreferrer" 
    />
  ),
  // Estiliza listas
  ul: ({ node, ...props }: any) => (
    <ul {...props} className="list-none space-y-2 my-4 ml-1" />
  ),
  li: ({ node, ...props }: any) => (
    <li {...props} className="flex items-start gap-2 before:content-['•'] before:text-primary before:font-bold before:mt-1" />
  ),
};

export default TravelPlan;