import api from './client';

// ── Document generation ────────────────────────────────────

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

// ── File upload / download ─────────────────────────────────

export interface UploadedDocument {
  id: number;
  file_name: string;
  file_type: string;
  file_size: number;
  notes: string;
  uploaded_at: string;
}

export async function uploadDocument(file: File, notes?: string): Promise<{ id: number; file_name: string; file_size: number }> {
  const formData = new FormData();
  formData.append('file', file);
  if (notes) formData.append('notes', notes);
  const { data } = await api.post('/documents/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  });
  return data;
}

export async function listMyDocuments(): Promise<UploadedDocument[]> {
  const { data } = await api.get('/documents/my');
  return data;
}

export async function downloadDocument(id: number, fileName: string): Promise<void> {
  const { data } = await api.get(`/documents/${id}/download`, { responseType: 'blob' });
  const url = URL.createObjectURL(data);
  const a = document.createElement('a');
  a.href = url;
  a.download = fileName;
  a.click();
  URL.revokeObjectURL(url);
}

export async function deleteDocument(id: number): Promise<void> {
  await api.delete(`/documents/${id}`);
}
