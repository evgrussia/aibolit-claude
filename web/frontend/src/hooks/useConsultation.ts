import { useMutation, useQueryClient } from '@tanstack/react-query';
import { startConsultation } from '../api/consultations';

export function useStartConsultation() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (vars: { specialty: string; complaints: string; patientId?: string }) =>
      startConsultation(vars.specialty, vars.complaints, vars.patientId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ['consultations'] });
    },
  });
}
