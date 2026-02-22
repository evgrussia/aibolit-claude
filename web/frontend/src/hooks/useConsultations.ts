import { useQuery } from '@tanstack/react-query';
import { getPatientConsultations } from '../api/patients.ts';

export function useConsultations(patientId: string | undefined) {
  return useQuery({
    queryKey: ['consultations', patientId],
    queryFn: () => getPatientConsultations(patientId!),
    enabled: !!patientId,
  });
}
