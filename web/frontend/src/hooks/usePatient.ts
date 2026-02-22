import { useQuery } from '@tanstack/react-query';
import { getPatient } from '../api/patients.ts';

export function usePatient(patientId: string | undefined) {
  return useQuery({
    queryKey: ['patient', patientId],
    queryFn: () => getPatient(patientId!),
    enabled: !!patientId,
  });
}
