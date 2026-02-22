import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { MemoryRouter } from 'react-router-dom';
import PatientListPage from '../../pages/PatientListPage';

const mockPatients = [
  { id: 'abc123', name: 'Иванов Иван', dob: '1985-01-15', gender: 'male' },
  { id: 'def456', name: 'Петрова Анна', dob: '1990-06-20', gender: 'female' },
];

vi.mock('../../api/patients', () => ({
  getPatients: vi.fn(),
  searchPatients: vi.fn(),
}));

import { getPatients } from '../../api/patients';

function renderPage() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  });
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <PatientListPage />
      </MemoryRouter>
    </QueryClientProvider>
  );
}

describe('PatientListPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('shows loading skeleton then patient list', async () => {
    vi.mocked(getPatients).mockResolvedValue(mockPatients);
    renderPage();

    await waitFor(() => {
      expect(screen.getByText('Иванов Иван')).toBeInTheDocument();
      expect(screen.getByText('Петрова Анна')).toBeInTheDocument();
    });
  });

  it('shows error with retry button on failure', async () => {
    vi.mocked(getPatients).mockRejectedValue(new Error('Network error'));
    renderPage();

    await waitFor(() => {
      expect(screen.getByRole('alert')).toBeInTheDocument();
      expect(screen.getByText('Повторить')).toBeInTheDocument();
    });
  });

  it('shows empty state when no patients', async () => {
    vi.mocked(getPatients).mockResolvedValue([]);
    renderPage();

    await waitFor(() => {
      expect(screen.getByText('Пациенты не найдены')).toBeInTheDocument();
    });
  });

  it('has accessible search input', async () => {
    vi.mocked(getPatients).mockResolvedValue([]);
    renderPage();

    const input = screen.getByPlaceholderText(/поиск по имени/i);
    expect(input).toBeInTheDocument();
    await userEvent.type(input, 'Иван');
    expect(input).toHaveValue('Иван');
  });
});
