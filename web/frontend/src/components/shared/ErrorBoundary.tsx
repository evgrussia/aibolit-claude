import { Component } from 'react';
import type { ErrorInfo, ReactNode } from 'react';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export default class ErrorBoundary extends Component<Props, State> {
  state: State = { hasError: false, error: null };

  static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, info: ErrorInfo) {
    console.error('[ErrorBoundary]', error, info.componentStack);
  }

  handleReset = () => {
    this.setState({ hasError: false, error: null });
  };

  render() {
    if (this.state.hasError) {
      if (this.props.fallback) return this.props.fallback;
      return (
        <div role="alert" className="flex flex-col items-center justify-center min-h-[50vh] gap-4 p-8">
          <div className="text-red-500 text-6xl">!</div>
          <h2 className="text-xl font-semibold text-gray-800">Что-то пошло не так</h2>
          <p className="text-sm text-gray-500 text-center max-w-md">
            {this.state.error?.message || 'Произошла непредвиденная ошибка отрисовки.'}
          </p>
          <button
            onClick={this.handleReset}
            className="px-5 py-2 bg-medical-teal text-white rounded-lg hover:bg-medical-navy transition-colors"
          >
            Попробовать снова
          </button>
        </div>
      );
    }
    return this.props.children;
  }
}
