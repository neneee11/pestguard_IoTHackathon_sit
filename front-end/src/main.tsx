import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import Index from './pages/Index'
import { Toaster } from '@/component/ui/sonner'
import './index.css'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Index />
    <Toaster />
  </StrictMode>,
)