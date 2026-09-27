import { apiRequest, apiRequestBlob } from './client'

export type DiagnosticCategory =
  | 'RADIOLOGY'
  | 'CARDIOLOGY'
  | 'NEUROPHYSIOLOGY'
  | 'RESPIRATORY'
  | 'AUDIOLOGY'
  | 'ENDOSCOPY'

export type DiagnosticReportStatus =
  | 'DRAFT'
  | 'FINAL'

export interface DiagnosticInvestigation {
  id: string
  hospital_id: string
  code: string
  name: string
  category: DiagnosticCategory
  description: string | null
  report_template: Record<string, unknown>
  active: boolean
  created_at: string
  updated_at: string
}

export interface DiagnosticQueueItem {
  id: string
  encounter_id: string
  patient_id: string
  patient_name: string
  hospital_number: string
  episode_number: string
  ordering_clinician_name: string
  order_type: 'DIAGNOSTIC' | 'RADIOLOGY'
  status:
    | 'REQUESTED'
    | 'RECEIVED'
    | 'IN_PROGRESS'
  priority: string
  details: Record<string, unknown>
  ordered_at: string
  started_at: string | null
}

export interface DiagnosticReport {
  id: string
  order_id: string
  investigation_id?: string
  category: DiagnosticCategory
  status: DiagnosticReportStatus
  findings: string | null
  impression: string | null
  interpretation: string | null
  recommendations: string | null
  measurements: Record<string, unknown> | null
  reported_at: string | null
  recorded_by: string | null
  recorded_at: string | null
  created_at: string
  updated_at: string
}

export interface DiagnosticReportAttachment {
  id: string
  report_id: string
  file_name: string
  content_type: string
  description: string | null
  created_at: string
  updated_at: string
}

export interface CreateDiagnosticReportRequest {
  order_id: string
  investigation_id?: string
  category: DiagnosticCategory
  findings?: string | null
  impression?: string | null
  interpretation?: string | null
  recommendations?: string | null
  measurements?: Record<string, unknown> | null
}

export interface UpdateDiagnosticReportRequest {
  findings?: string | null
  impression?: string | null
  interpretation?: string | null
  recommendations?: string | null
  measurements?: Record<string, unknown> | null
}

export async function listDiagnosticQueue(
  accessToken: string,
): Promise<DiagnosticQueueItem[]> {
  return apiRequest<DiagnosticQueueItem[]>(
    '/clinical-orders/queue/diagnostics',
    {},
    accessToken,
  )
}

export async function listDiagnosticInvestigations(
  accessToken: string,
): Promise<DiagnosticInvestigation[]> {
  return apiRequest<DiagnosticInvestigation[]>(
    '/diagnostics/investigations',
    {},
    accessToken,
  )
}

export async function receiveDiagnosticOrder(
  accessToken: string,
  orderId: string,
): Promise<unknown> {
  return apiRequest<unknown>(
    `/clinical-orders/${orderId}/receive`,
    {
      method: 'POST',
    },
    accessToken,
  )
}

export async function startDiagnosticOrder(
  accessToken: string,
  orderId: string,
): Promise<unknown> {
  return apiRequest<unknown>(
    `/clinical-orders/${orderId}/start`,
    {
      method: 'POST',
    },
    accessToken,
  )
}

export async function createDiagnosticReport(
  accessToken: string,
  request: CreateDiagnosticReportRequest,
): Promise<DiagnosticReport> {
  return apiRequest<DiagnosticReport>(
    '/diagnostics/reports',
    {
      method: 'POST',
      body: JSON.stringify(request),
    },
    accessToken,
  )
}

export async function getDiagnosticReportByOrder(
  accessToken: string,
  orderId: string,
): Promise<DiagnosticReport> {
  return apiRequest<DiagnosticReport>(
    `/diagnostics/reports/by-order/${orderId}`,
    {},
    accessToken,
  )
}

export async function getDiagnosticReport(
  accessToken: string,
  reportId: string,
): Promise<DiagnosticReport> {
  return apiRequest<DiagnosticReport>(
    `/diagnostics/reports/${reportId}`,
    {},
    accessToken,
  )
}

export async function updateDiagnosticReport(
  accessToken: string,
  reportId: string,
  request: UpdateDiagnosticReportRequest,
): Promise<DiagnosticReport> {
  return apiRequest<DiagnosticReport>(
    `/diagnostics/reports/${reportId}`,
    {
      method: 'PUT',
      body: JSON.stringify(request),
    },
    accessToken,
  )
}

export async function finalizeDiagnosticReport(
  accessToken: string,
  reportId: string,
): Promise<DiagnosticReport> {
  return apiRequest<DiagnosticReport>(
    `/diagnostics/reports/${reportId}/finalize`,
    {
      method: 'POST',
    },
    accessToken,
  )
}

export async function listDiagnosticAttachments(
  accessToken: string,
  reportId: string,
): Promise<DiagnosticReportAttachment[]> {
  return apiRequest<DiagnosticReportAttachment[]>(
    `/diagnostics/reports/${reportId}/attachments`,
    {},
    accessToken,
  )
}

export async function uploadDiagnosticAttachment(
  accessToken: string,
  reportId: string,
  file: File,
  description?: string,
): Promise<DiagnosticReportAttachment> {
  const formData = new FormData()

  formData.append('file', file)

  if (description?.trim()) {
    formData.append(
      'description',
      description.trim(),
    )
  }

  return apiRequest<DiagnosticReportAttachment>(
    `/diagnostics/reports/${reportId}/attachments`,
    {
      method: 'POST',
      body: formData,
    },
    accessToken,
  )
}


export async function downloadDiagnosticAttachment(
  accessToken: string,
  attachmentId: string,
): Promise<Blob> {
  return apiRequestBlob(
    `/diagnostics/attachments/${attachmentId}`,
    {},
    accessToken,
  )
}
