import { useMutation, useQueryClient } from '@tanstack/react-query';
import {
  addVitals, addLabResult, addDiagnosis, addMedication, addAllergy, updatePatient,
  deleteSubRecord, updateSubRecord,
} from '../api/patients';

export function usePatientMutations(patientId: string | undefined) {
  const qc = useQueryClient();

  const invalidate = () => {
    if (patientId) {
      qc.invalidateQueries({ queryKey: ['patient', patientId] });
    }
  };

  const vitals = useMutation({
    mutationFn: (data: Record<string, unknown>) => addVitals(patientId!, data),
    onSuccess: invalidate,
  });

  const lab = useMutation({
    mutationFn: (data: Record<string, unknown>) => addLabResult(patientId!, data),
    onSuccess: invalidate,
  });

  const diagnosis = useMutation({
    mutationFn: (data: Record<string, unknown>) => addDiagnosis(patientId!, data),
    onSuccess: invalidate,
  });

  const medication = useMutation({
    mutationFn: (data: Record<string, unknown>) => addMedication(patientId!, data),
    onSuccess: invalidate,
  });

  const allergy = useMutation({
    mutationFn: (data: Record<string, unknown>) => addAllergy(patientId!, data),
    onSuccess: invalidate,
  });

  const profile = useMutation({
    mutationFn: (data: Record<string, unknown>) => updatePatient(patientId!, data),
    onSuccess: invalidate,
  });

  const deleteRecord = useMutation({
    mutationFn: ({ table, recordId }: { table: string; recordId: number }) =>
      deleteSubRecord(patientId!, table, recordId),
    onSuccess: invalidate,
  });

  const updateRecord = useMutation({
    mutationFn: ({ table, recordId, fields }: { table: string; recordId: number; fields: Record<string, unknown> }) =>
      updateSubRecord(patientId!, table, recordId, fields),
    onSuccess: invalidate,
  });

  return { vitals, lab, diagnosis, medication, allergy, profile, deleteRecord, updateRecord };
}
