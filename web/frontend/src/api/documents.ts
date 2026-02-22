import api from './client';

export interface MedicalRecordRequest {
  patient_name: string; patient_age: number; gender: string;
  complaints: string; anamnesis: string; examination: string;
  diagnoses: Array<{ name: string; icd10_code: string; confidence?: number }>;
  plan: string; doctor_specialty?: string;
  vitals?: Record<string, number>; lab_results?: unknown[];
}

export interface PrescriptionRequest {
  patient_name: string;
  medications: Array<{ name: string; dosage: string; frequency: string; duration?: string; route?: string; notes?: string }>;
  diagnoses: string[]; doctor_specialty?: string; notes?: string;
}

export interface ReferralRequest {
  patient_name: string; patient_age: number;
  from_specialty: string; to_specialty: string;
  reason: string; current_diagnoses: string[];
  relevant_results?: string; urgency?: string;
}

export interface DocumentResponse { content: string }

const toDocResponse = (r: { data: { document: string } }): DocumentResponse => ({ content: r.data.document });

export const generateMedicalRecord = (data: MedicalRecordRequest) =>
  api.post<{ document: string }>('/documents/medical-record', data).then(toDocResponse);

export const generatePrescription = (data: PrescriptionRequest) =>
  api.post<{ document: string }>('/documents/prescription', data).then(toDocResponse);

export const generateReferral = (data: ReferralRequest) =>
  api.post<{ document: string }>('/documents/referral', data).then(toDocResponse);
