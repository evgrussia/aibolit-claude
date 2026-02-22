import { BrowserRouter, Routes, Route, Navigate, Outlet } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import { ToastProvider } from './contexts/ToastContext';
import ErrorBoundary from './components/shared/ErrorBoundary';
import Layout from './components/layout/Layout';
import LoginPage from './pages/LoginPage';
import DashboardPage from './pages/DashboardPage';
import LabResultsPage from './pages/LabResultsPage';
import VitalsHistoryPage from './pages/VitalsHistoryPage';
import ConsultationsPage from './pages/ConsultationsPage';
import ConsultDoctorPage from './pages/ConsultDoctorPage';
import DiagnosisDetailPage from './pages/DiagnosisDetailPage';
import HealthTimelinePage from './pages/HealthTimelinePage';
import DiagnosticsPage from './pages/DiagnosticsPage';
import DrugToolsPage from './pages/DrugToolsPage';
import DocumentsPage from './pages/DocumentsPage';
import LoadingSpinner from './components/shared/LoadingSpinner';

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      staleTime: 30_000,
      refetchOnWindowFocus: false,
    },
  },
});

function ProtectedRoute() {
  const { isAuthenticated, isLoading } = useAuth();
  if (isLoading) return <div className="min-h-screen flex items-center justify-center"><LoadingSpinner /></div>;
  if (!isAuthenticated) return <Navigate to="/login" replace />;
  return <Outlet />;
}

function RedirectToMyDashboard() {
  const { patientId, isLoading } = useAuth();
  if (isLoading) return <div className="min-h-screen flex items-center justify-center"><LoadingSpinner /></div>;
  if (patientId) return <Navigate to={`/patients/${patientId}`} replace />;
  return <Navigate to="/login" replace />;
}

export default function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <ToastProvider>
            <BrowserRouter>
              <Routes>
                <Route path="/login" element={<LoginPage />} />
                <Route element={<ProtectedRoute />}>
                  <Route element={<Layout />}>
                    <Route path="/" element={<RedirectToMyDashboard />} />
                    <Route path="/patients/:patientId" element={<DashboardPage />} />
                    <Route path="/patients/:patientId/labs" element={<LabResultsPage />} />
                    <Route path="/patients/:patientId/vitals" element={<VitalsHistoryPage />} />
                    <Route path="/patients/:patientId/consultations" element={<ConsultationsPage />} />
                    <Route path="/patients/:patientId/timeline" element={<HealthTimelinePage />} />
                    <Route path="/patients/:patientId/diagnoses/:icdCode" element={<DiagnosisDetailPage />} />
                    <Route path="/consult" element={<ConsultDoctorPage />} />
                    <Route path="/diagnostics" element={<DiagnosticsPage />} />
                    <Route path="/drugs" element={<DrugToolsPage />} />
                    <Route path="/documents" element={<DocumentsPage />} />
                  </Route>
                </Route>
                <Route path="*" element={<Navigate to="/" replace />} />
              </Routes>
            </BrowserRouter>
          </ToastProvider>
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
