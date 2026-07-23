/**
 * WhatsApp send utility — tries real API, falls back to mock
 */
import { whatsappApi, type WhatsAppMessageResponse } from './api';

export interface SendResult {
  success: boolean;
  message_id?: string;
  error?: string;
  mock: boolean;
}

export async function sendWhatsAppReal(
  to: string,
  text: string,
): Promise<SendResult> {
  try {
    const resp = await whatsappApi.sendText({ to, text });
    const data: WhatsAppMessageResponse = resp.data;
    return {
      success: data.success,
      message_id: data.message_id,
      error: data.error,
      mock: false,
    };
  } catch (err: any) {
    // If backend is 503 (not configured), fall back to mock
    if (err?.response?.status === 503) {
      console.warn('WhatsApp not configured on backend, using mock');
      return mockSend(to, text);
    }
    return {
      success: false,
      error: err?.response?.data?.error || err?.message || 'Erro ao enviar',
      mock: false,
    };
  }
}

function mockSend(to: string, text: string): Promise<SendResult> {
  return new Promise((resolve) => {
    const succeeded = Math.random() > 0.25;
    setTimeout(
      () => {
        resolve({
          success: succeeded,
          message_id: succeeded ? `mock-${Date.now()}` : undefined,
          error: succeeded ? undefined : 'Mock: falha simulada',
          mock: true,
        });
      },
      1500 + Math.random() * 1500,
    );
  });
}
