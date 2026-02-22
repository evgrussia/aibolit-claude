import api from './client';

export async function searchIcd(query: string) {
  const { data } = await api.get('/knowledge/icd-search', { params: { q: query } });
  return data;
}

export async function getDiseaseInfo(name: string) {
  const { data } = await api.get('/knowledge/disease-info', { params: { name } });
  return data;
}

export async function searchLiterature(query: string, maxResults = 10) {
  const { data } = await api.get('/knowledge/literature', {
    params: { q: query, max_results: maxResults },
  });
  return data;
}

export async function getArticleAbstract(pmid: string) {
  const { data } = await api.get(`/knowledge/article/${pmid}`);
  return data;
}
