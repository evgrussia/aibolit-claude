import { useQuery } from '@tanstack/react-query';
import { getLabTrends } from '../api/patients.ts';

export function useLabTrends(patientId: string | undefined, testName: string) {
  return useQuery({
    queryKey: ['labTrends', patientId, testName],
    queryFn: () => getLabTrends(patientId!, testName),
    enabled: !!patientId && !!testName,
  });
}
