import { describe, it, expect } from 'vitest';
import api from '../../api/client';

describe('API Client', () => {
  it('has correct base URL', () => {
    expect(api.defaults.baseURL).toBe('/api/v1');
  });

  it('has timeout configured', () => {
    expect(api.defaults.timeout).toBe(15000);
  });

  it('has JSON content-type header', () => {
    expect(api.defaults.headers['Content-Type']).toBe('application/json');
  });

  it('has response interceptor', () => {
    const interceptors = api.interceptors.response as unknown as { handlers: unknown[] };
    expect(interceptors.handlers.length).toBeGreaterThan(0);
  });
});
