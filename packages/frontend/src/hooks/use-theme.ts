import { useContext } from "react"
import { ThemeProviderContext } from "@/components/ThemeProvider" // Importa o Contexto

// Esta é a função que estava causando o aviso
export const useTheme = () => {
  const context = useContext(ThemeProviderContext)

  if (context === undefined)
    throw new Error("useTheme must be used within a ThemeProvider")

  return context
}