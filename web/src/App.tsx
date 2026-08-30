import { BrowserRouter, Navigate, Route, Routes } from 'react-router-dom'
import AppShell from './components/AppShell'
import { ToastProvider } from './components/ui/Toast'
import { AuthProvider, useAuth } from './lib/auth'
import CustomersPage from './pages/CustomersPage'
import DashboardPage from './pages/DashboardPage'
import DocsPage from './pages/DocsPage'
import LoginPage from './pages/LoginPage'
import OffersPage from './pages/OffersPage'
import QuotationDetailPage from './pages/QuotationDetailPage'
import QuotationsPage from './pages/QuotationsPage'
import ReportPage from './pages/ReportPage'
import SalesCommandPage from './pages/SalesCommandPage'
import StaffPage from './pages/StaffPage'
import type { ReactNode } from 'react'

function Guard({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  if (!user) return <Navigate to="/login" replace />
  return children
}

function PublicOnly({ children }: { children: ReactNode }) {
  const { user } = useAuth()
  if (user) return <Navigate to="/" replace />
  return children
}

export default function App() {
  return (
    <AuthProvider>
      <ToastProvider>
        <BrowserRouter>
          <Routes>
            <Route
              path="/login"
              element={
                <PublicOnly>
                  <LoginPage />
                </PublicOnly>
              }
            />
            <Route
              element={
                <Guard>
                  <AppShell />
                </Guard>
              }
            >
              <Route index element={<DashboardPage />} />
              <Route path="offers" element={<OffersPage />} />
              <Route path="report" element={<ReportPage />} />
              <Route path="sales-command" element={<SalesCommandPage />} />
              <Route path="docs" element={<DocsPage />} />
              <Route path="customers" element={<CustomersPage />} />
              <Route path="quotations" element={<QuotationsPage />} />
              <Route path="quotations/:id" element={<QuotationDetailPage />} />
              <Route path="staff" element={<StaffPage />} />
            </Route>
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </BrowserRouter>
      </ToastProvider>
    </AuthProvider>
  )
}
