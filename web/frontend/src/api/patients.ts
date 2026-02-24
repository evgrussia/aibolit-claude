import api from './client';
import type { PatientSummary, PatientFull } from '../types/patient';

export async function getPatients(): Promise<PatientSummary[]> {
  const { data } = await api.get('/patients');
  return data;
}

export async function searchPatients(q: string): Promise<PatientSummary[]> {
  const { data } = await api.get('/patients/search', { params: { q } });
  return data;
}

export async function getPatient(id: string): Promise<PatientFull> {
  const { data } = await api.get(`/patients/${id}`);
  return data;
}

export async function getLabTrends(patientId: string, test: string) {
  const { data } = await api.get(`/patients/${patientId}/lab-trends`, { params: { test } });
  return data;
}

export async function getVitalsHistory(patientId: string) {
  const { data } = await api.get(`/patients/${patientId}/vitals-history`);
  return data;
}

export async function getPatientConsultations(patientId: string) {
  const { data } = await api.get(`/patients/${patientId}/consultations`);
  return data;
}

export async function addVitals(patientId: string, vitals: Record<string, unknown>) {
  const { data } = await api.post(`/patients/${patientId}/vitals`, vitals);
  return data;
}

export async function addLabResult(patientId: string, lab: Record<string, unknown>) {
  const { data } = await api.post(`/patients/${patientId}/labs`, lab);
  return data;
}

export async function registerPatient(patient: Record<string, unknown>) {
  const { data } = await api.post('/patients', patient);
  return data;
}

export async function addDiagnosis(patientId: string, diag: Record<string, unknown>) {
  const { data } = await api.post(`/patients/${patientId}/diagnoses`, diag);
  return data;
}

export async function addMedication(patientId: string, med: Record<string, unknown>) {
  const { data } = await api.post(`/patients/${patientId}/medications`, med);
  return data;
}

export async function addAllergy(patientId: string, allergy: Record<string, unknown>) {
  const { data } = await api.post(`/patients/${patientId}/allergies`, allergy);
  return data;
}

export async function parseLabFile(patientId: string, file: File) {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post(`/patients/${patientId}/labs/upload-parse`, formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 180_000,
  });
  return data;
}

export async function addLabResultsBulk(patientId: string, results: Record<string, unknown>[]) {
  const { data } = await api.post(`/patients/${patientId}/labs/bulk`, { results });
  return data;
}

export async function updatePatient(patientId: string, updates: Record<string, unknown>) {
  const { data } = await api.patch(`/patients/${patientId}`, updates);
  return data;
}

export async function deleteSubRecord(patientId: string, table: string, recordId: number) {
  const { data } = await api.delete(`/patients/${patientId}/${table}/${recordId}`);
  return data;
}

export async function updateSubRecord(patientId: string, table: string, recordId: number, fields: Record<string, unknown>) {
  const { data } = await api.patch(`/patients/${patientId}/${table}/${recordId}`, fields);
  return data;
}
