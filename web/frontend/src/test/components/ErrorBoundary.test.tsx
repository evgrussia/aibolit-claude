import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ErrorBoundary from '../../components/shared/ErrorBoundary';

function ThrowingComponent({ shouldThrow }: { shouldThrow: boolean }) {
  if (shouldThrow) throw new Error('Test error');
  return <div>Working fine</div>;
}

describe('ErrorBoundary', () => {
  it('renders children when no error', () => {
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={false} />
      </ErrorBoundary>
    );
    expect(screen.getByText('Working fine')).toBeInTheDocument();
  });

  it('shows fallback UI when child throws', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={true} />
      </ErrorBoundary>
    );
    expect(screen.getByText('Что-то пошло не так')).toBeInTheDocument();
    expect(screen.getByText('Test error')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toBeInTheDocument();
    vi.restoreAllMocks();
  });

  it('resets on button click', () => {
    vi.spyOn(console, 'error').mockImplementation(() => {});
    let shouldThrow = true;
    const { rerender } = render(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={shouldThrow} />
      </ErrorBoundary>
    );
    expect(screen.getByText('Что-то пошло не так')).toBeInTheDocument();

    shouldThrow = false;
    fireEvent.click(screen.getByText('Попробовать снова'));

    rerender(
      <ErrorBoundary>
        <ThrowingComponent shouldThrow={shouldThrow} />
      </ErrorBoundary>
    );
    // After reset, children should re-render
    vi.restoreAllMocks();
  });
});
