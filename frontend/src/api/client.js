import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ─── Existing endpoints ──────────────────────────────────────
export const fetchCourses = (programType) =>
  api.get('/api/courses', { params: programType ? { program_type: programType } : {} });
export const fetchSkillGap = () => api.get('/api/skillgap');
export const fetchPlacements = () => api.get('/api/placements');
export const fetchStats = () => api.get('/api/stats');
export const fetchFeedback = () => api.get('/api/feedback');

export const extractSkills = (text) => api.post('/api/extract', { text });
export const liveSkillGap = (text) => api.post('/api/skillgap/live', { text });
export const submitFeedback = (data) => api.post('/api/feedback', data);

// ─── New endpoints for PS #26134 ─────────────────────────────
export const fetchMarketIntelligence = () => api.get('/api/market-intelligence');
export const fetchSkillComparison = () => api.get('/api/skill-comparison');
export const fetchRecommendations = (recType, priority) =>
  api.get('/api/recommendations', { params: { rec_type: recType, priority } });
export const fetchDistrictPlans = () => api.get('/api/district-plans');
export const fetchStudentPrograms = (interest) =>
  api.get('/api/student/programs', { params: interest ? { interest } : {} });

// ─── Resume upload endpoints ─────────────────────────────────
export const parseResume = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/resume/parse', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  });
};

export const matchResumePrograms = (file) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/resume/match-programs', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 60000,
  });
};

export default api;

export const fetchDemand = (params = {}) =>
  api.get('/api/demand', { params });

export const fetchCourseMarketRoles = (courseId) =>
  api.get(`/api/courses/${courseId}/market-roles`);
export const fetchCourseMarketGap = (courseId, roleId) =>
  api.get(`/api/courses/${courseId}/gap`, { params: roleId ? { role_id: roleId } : {} });


export const alignResume = (file, roleId) => {
  const formData = new FormData();
  formData.append('file', file);
  return api.post('/api/resume/align', formData, {
    params: roleId ? { role_id: roleId } : {},
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 90000,
  });
};

export const fetchMarketRoles = () => api.get('/api/roles');
