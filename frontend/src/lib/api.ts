import axios from 'axios';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Interceptor para adicionar token JWT
api.interceptors.request.use(
  (config) => {
    if (typeof window !== 'undefined') {
      const token = localStorage.getItem('polis_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para tratar erros de autenticação
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401 && typeof window !== 'undefined') {
      // Não redirecionar para endpoints de auth (login/register)
      // — o catch do AuthContext trata o fallback mock
      const url = error.config?.url || '';
      if (!url.startsWith('/auth/')) {
        localStorage.removeItem('polis_token');
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export interface LoginPayload {
  email: string;
  password: string;
}

export interface RegisterPayload {
  name: string;
  email: string;
  password: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user?: {
    id: number;
    name: string;
    email: string;
  };
}

export interface Metrics {
  total_agents: number;
  active_conversations: number;
  avg_response_time: string;
  success_rate: number;
  total_messages: number;
  users_today: number;
}

export const authApi = {
  login: (payload: LoginPayload) =>
    api.post<AuthResponse>('/auth/login', payload),
  register: (payload: RegisterPayload) =>
    api.post<AuthResponse>('/auth/register', payload),
  me: () => api.get<AuthResponse['user']>('/auth/me'),
};

export const dashboardApi = {
  getMetrics: () => api.get<Metrics>('/dashboard/metrics'),
  getRecentActivity: () => api.get('/dashboard/recent-activity'),
};

export default api;

/* ───── WhatsApp API ───── */

export interface WhatsAppSendTextPayload {
  to: string;
  text: string;
  preview_url?: boolean;
}

export interface WhatsAppSendMediaPayload {
  to: string;
  media_url: string;
  caption?: string;
  media_type?: string;
}

export interface WhatsAppSendTemplatePayload {
  to: string;
  template_name: string;
  params?: Record<string, string>;
  language?: string;
}

export interface WhatsAppMessageResponse {
  success: boolean;
  message_id?: string;
  error?: string;
}

export const whatsappApi = {
  /** Send text message */
  sendText: (payload: WhatsAppSendTextPayload) =>
    api.post<WhatsAppMessageResponse>('/whatsapp/send/text', payload),

  /** Send media (image/video/document) */
  sendMedia: (payload: WhatsAppSendMediaPayload) =>
    api.post<WhatsAppMessageResponse>('/whatsapp/send/media', payload),

  /** Send template message */
  sendTemplate: (payload: WhatsAppSendTemplatePayload) =>
    api.post<WhatsAppMessageResponse>('/whatsapp/send/template', payload),

  /** Check service status */
  getStatus: () =>
    api.get<{ configured: boolean; online: boolean }>('/whatsapp/status'),

  /** Check message delivery status */
  getMessageStatus: (messageId: string) =>
    api.get(`/whatsapp/messages/${messageId}/status`),
};
