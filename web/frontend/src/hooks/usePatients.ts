import { useQuery } from '@tanstack/react-query';
import { getPatients, searchPatients } from '../api/patients.ts';

export function usePatients(searchQuery?: string) {
  return useQuery({
    queryKey: ['patients', searchQuery ?? ''],
    queryFn: () =>
      searchQuery && searchQuery.length >= 2
        ? searchPatients(searchQuery)
        : getPatients(),
  });
}
