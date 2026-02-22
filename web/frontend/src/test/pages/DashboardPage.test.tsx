import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter, Route, Routes } from 'react-router-dom';
import { ToastProvider } from '../../contexts/ToastContext';
import DashboardPage from '../../pages/DashboardPage';
import type { PatientFull } from '../../types/patient';

const mockPatient: PatientFull = {
  id: 'abc123',
  first_name: 'Иван',
  last_name: 'Иванов',
  full_name: 'Иванов Иван Иванович',
  date_of_birth: '1985-01-15',
  gender: 'male',
  age: 41,
  blood_type: 'A+',
  allergies: [],
  medications: [],
  diagnoses: [],
  vitals_history: [],
  lab_results: [],
  family_history: [],
  surgical_history: [],
  lifestyle: {},
  notes: '',
};

vi.mock('../../api/patients', () => ({
  getPatient: vi.fn(),
}));

import { getPatient } from '../../api/patients';

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <ToastProvider>
        <MemoryRouter initialEntries={['/patients/abc123']}>
          <Routes>
            <Route path="/patients/:patientId" element={<DashboardPage />} />
          </Routes>
        </MemoryRouter>
      </ToastProvider>
    </QueryClientProvider>
  );
}

describe('DashboardPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows patient info on success', async () => {
    vi.mocked(getPatient).mockResolvedValue(mockPatient);
    renderPage();

    await waitFor(() => {
      expect(screen.getByText('Иванов Иван Иванович')).toBeInTheDocument();
    });
  });

  it('shows error with retry on failure', async () => {
    vi.mocked(getPatient).mockRejectedValue(new Error('Сервер недоступен'));
    renderPage();

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText('Повторить')).toBeInTheDocument();
    });
  });
});
