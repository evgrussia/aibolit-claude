import api from './client';
import type { Specialization, ConsultationResult } from '../types/patient';

export async function getSpecializations(): Promise<Specialization[]> {
  const { data } = await api.get('/reference/specializations');
  return data;
}

export async function startConsultation(
  specialty: string,
  complaints: string,
  patientId?: string,
): Promise<ConsultationResult> {
  const { data } = await api.post('/consultations/start', {
    specialty,
    complaints,
    patient_id: patientId || null,
  });
  return data;
}
