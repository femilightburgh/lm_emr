import { apiRequest } from './client'


// ============================================================================
// Types
// ============================================================================


export type ClinicalDocumentType =
  | 'NURSING_INTAKE'


export type ClinicalDocumentStatus =
  | 'DRAFT'
  | 'SIGNED'
  | 'AMENDED'


export interface ClinicalDocument {
  id: string

  encounter_id: string

  document_type: ClinicalDocumentType

  status: ClinicalDocumentStatus

  version: number

  content: Record<string, unknown>

  authored_by: string

  signed_at: string | null

  signed_by: string | null

  amended_from_id: string | null
}


// ============================================================================
// Create
// ============================================================================


export async function createClinicalDocument(
  accessToken: string,
  payload: {
    encounter_id: string
    patient_id: string
    document_type: ClinicalDocumentType
    authored_by: string
    content: Record<string, unknown>
  },
): Promise<ClinicalDocument> {
  return apiRequest<ClinicalDocument>(
    '/clinical-documents',
    {
      method: 'POST',
      body: JSON.stringify(payload),
    },
    accessToken,
  )
}


// ============================================================================
// Update Draft
// ============================================================================


export async function updateClinicalDocument(
  accessToken: string,
  documentId: string,
  editedBy: string,
  content: Record<string, unknown>,
): Promise<ClinicalDocument> {
  return apiRequest<ClinicalDocument>(
    `/clinical-documents/${documentId}`,
    {
      method: 'PATCH',
      body: JSON.stringify({
        edited_by: editedBy,
        content,
      }),
    },
    accessToken,
  )
}


// ============================================================================
// Sign
// ============================================================================


export async function signClinicalDocument(
  accessToken: string,
  documentId: string,
): Promise<ClinicalDocument> {
  return apiRequest<ClinicalDocument>(
    `/clinical-documents/${documentId}/sign`,
    {
      method: 'POST',
    },
    accessToken,
  )
}


// ============================================================================
// Retrieve
// ============================================================================


export async function getClinicalDocument(
  accessToken: string,
  documentId: string,
): Promise<ClinicalDocument> {
  return apiRequest<ClinicalDocument>(
    `/clinical-documents/${documentId}`,
    {},
    accessToken,
  )
}


// ============================================================================
// Encounter Documents
// ============================================================================


export async function listEncounterClinicalDocuments(
  accessToken: string,
  encounterId: string,
): Promise<ClinicalDocument[]> {
  return apiRequest<ClinicalDocument[]>(
    `/clinical-documents/encounters/${encounterId}`,
    {},
    accessToken,
  )
}
