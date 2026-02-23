import api from './client';
import type { Specialization, ConsultationResult } from '../types/patient';

export interface TriageRecommendation {
  specialty_id: string;
  name_ru: string;
  description: string;
  relevance: number;
  reason: string;
}

export interface TriageResult {
  recommendations: TriageRecommendation[];
  emergency?: {
    call: string;
    message: string;
    flags: Array<{ description: string; action: string }>;
  };
  red_flags?: Array<{ description: string; urgency: number; action: string }>;
}

export async function getSpecializations(): Promise<Specialization[]> {
  const { data } = await api.get('/reference/specializations');
  return data;
}

export async function triageComplaints(complaints: string): Promise<TriageResult> {
  const { data } = await api.post('/consultations/triage', { complaints });
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
  }, {
    timeout: 120_000, // AI-консультация может занимать до 120 секунд
  });
  return data;
}
