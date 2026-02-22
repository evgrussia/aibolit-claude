import { useQuery } from '@tanstack/react-query';
import { getSpecializations } from '../api/consultations';

export function useSpecializations() {
  return useQuery({
    queryKey: ['specializations'],
    queryFn: getSpecializations,
    staleTime: 5 * 60_000,
  });
}
