import { useQuery } from '@tanstack/react-query';
import { getVitalsHistory } from '../api/patients.ts';

export function useVitalsHistory(patientId: string | undefined) {
  return useQuery({
    queryKey: ['vitalsHistory', patientId],
    queryFn: () => getVitalsHistory(patientId!),
    enabled: !!patientId,
  });
}
