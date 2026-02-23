import api from './client';

export interface DrugInfo {
  name: string; brand_name?: string; brand_names?: string[]; generic_name?: string;
  indications?: string; dosage?: string; contraindications?: string;
  warnings?: string; adverse_reactions?: string; drug_class?: string;
  drug_interactions?: string; pregnancy?: string; mechanism_of_action?: string;
  manufacturer?: string;
}

export interface DrugInteractionResult {
  has_interactions: boolean;
  interactions: Array<{ drug1: string; drug2: string; severity: string; description: string }>;
  checked_pairs: number;
}

export interface AdverseEvent {
  reaction: string; count: number; outcome?: string;
}

export const getDrugInfo = (name: string) =>
  api.get<DrugInfo>(`/drugs/${encodeURIComponent(name)}`).then(r => r.data);

export const checkInteractions = (drugs: string[]) =>
  api.post<Array<{ drug1: string; drug2: string; warning: string; severity: string }>>('/drugs/interactions', { drugs })
    .then(r => {
      const raw = r.data;
      // Backend returns raw array; normalize to expected shape
      const list = Array.isArray(raw) ? raw : [];
      return {
        has_interactions: list.length > 0,
        interactions: list.map(x => ({ drug1: x.drug1, drug2: x.drug2, severity: x.severity, description: x.warning })),
        checked_pairs: Math.floor((drugs.length * (drugs.length - 1)) / 2),
      } as DrugInteractionResult;
    });

export const getAdverseEvents = (name: string) =>
  api.get<{ drug: string; events: AdverseEvent[] }>(`/drugs/${encodeURIComponent(name)}/adverse-events`).then(r => r.data);
