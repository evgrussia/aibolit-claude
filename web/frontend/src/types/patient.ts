export interface PatientSummary {
  id: string;
  name: string;
  dob: string;
  gender: string;
}

export interface Allergy {
  substance: string;
  reaction: string;
  severity: string;
}

export interface Medication {
  name: string;
  dosage: string;
  frequency: string;
  route: string;
  start_date: string | null;
  end_date: string | null;
  prescribing_doctor: string;
  notes: string;
}

export interface Diagnosis {
  icd10_code: string;
  name: string;
  date_diagnosed: string;
  status: string;
  notes: string;
  confidence: number;
}

export interface LabResult {
  test_name: string;
  value: number | string;
  unit: string;
  reference_range: string;
  date: string;
  is_abnormal: boolean;
  notes: string;
}

export interface VitalSigns {
  timestamp: string;
  systolic_bp: number | null;
  diastolic_bp: number | null;
  heart_rate: number | null;
  temperature: number | null;
  spo2: number | null;
  respiratory_rate: number | null;
  weight: number | null;
  height: number | null;
  blood_glucose: number | null;
}

export interface PatientFull {
  id: string;
  first_name: string;
  last_name: string;
  full_name: string;
  age: number;
  date_of_birth: string;
  gender: string;
  blood_type: string | null;
  allergies: Allergy[];
  medications: Medication[];
  diagnoses: Diagnosis[];
  lab_results: LabResult[];
  vitals_history: VitalSigns[];
  family_history: string[];
  surgical_history: string[];
  lifestyle: Record<string, string>;
  notes: string;
}

export interface Consultation {
  id: number;
  patient_id: string | null;
  patient_name: string | null;
  specialty: string;
  complaints: string;
  response: Record<string, unknown>;
  date: string;
}

export interface Skill {
  name: string;
  description: string;
}

export interface Specialization {
  id: string;
  name_ru: string;
  name_en: string;
  description: string;
  skills: Skill[];
}

export interface ConsultationSkill {
  name: string;
  description: string;
  tool: string;
}

export interface ConsultationResult {
  doctor: {
    specialty_id: string;
    name: string;
    qualification: string;
  };
  consultation: {
    complaints: string;
    patient_context: string;
    summary: string;
    available_skills: ConsultationSkill[];
    relevant_icd_prefixes: string[];
    recommended_tests: string[];
  };
  instructions: string;
  disclaimer: string;
}

export interface IcdResult {
  code: string;
  title: string;
  definition?: string;
  uri?: string;
}

export interface PubMedArticle {
  pmid: string;
  title: string;
  authors: string;
  journal: string;
  year: string;
  doi?: string;
  url?: string;
}

export interface DiseaseInfo {
  name: string;
  icd_codes: IcdResult[];
  description: string;
  symptoms: string[];
  risk_factors: string[];
}
