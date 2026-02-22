import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import ApiError from '../../components/shared/ApiError';

describe('ApiError', () => {
  it('renders error message', () => {
    render(<ApiError message="Что-то пошло не так" />);
    expect(screen.getByText('Что-то пошло не так')).toBeInTheDocument();
    expect(screen.getByRole('alert')).toBeInTheDocument();
  });

  it('does not show retry button when onRetry is not provided', () => {
    render(<ApiError message="Error" />);
    expect(screen.queryByText('Повторить')).not.toBeInTheDocument();
  });

  it('shows retry button and calls onRetry on click', () => {
    const onRetry = vi.fn();
    render(<ApiError message="Error" onRetry={onRetry} />);
    const button = screen.getByText('Повторить');
    expect(button).toBeInTheDocument();
    fireEvent.click(button);
    expect(onRetry).toHaveBeenCalledOnce();
  });
});
