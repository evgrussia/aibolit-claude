import { useQuery } from '@tanstack/react-query';
import { getDiseaseInfo, searchIcd, searchLiterature } from '../api/knowledge';

export function useDiseaseInfo(name: string | undefined) {
  return useQuery({
    queryKey: ['disease-info', name],
    queryFn: () => getDiseaseInfo(name!),
    enabled: !!name,
    staleTime: 5 * 60_000,
  });
}

export function useIcdSearch(query: string | undefined) {
  return useQuery({
    queryKey: ['icd-search', query],
    queryFn: () => searchIcd(query!),
    enabled: !!query && query.length >= 2,
    staleTime: 5 * 60_000,
  });
}

export function useLiteratureSearch(query: string | undefined) {
  return useQuery({
    queryKey: ['literature', query],
    queryFn: () => searchLiterature(query!),
    enabled: !!query && query.length >= 3,
    staleTime: 5 * 60_000,
  });
}
