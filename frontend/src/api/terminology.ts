import { apiRequest } from './client'

export type TerminologySystem =
  | 'ICD-10-CM'
  | 'ICD-11'
  | 'SNOMED-CT'

export interface TerminologyConcept {
  id: string
  system: TerminologySystem
  code: string
  display_name: string
  description: string | null
  active: boolean
}

export async function searchDiagnosisTerminology(
  accessToken: string,
  query: string,
  options?: {
    system?: TerminologySystem
    limit?: number
  },
): Promise<TerminologyConcept[]> {
  const params = new URLSearchParams({
    q: query,
  })

  if (options?.system) {
    params.set('system', options.system)
  }

  if (options?.limit !== undefined) {
    params.set('limit', String(options.limit))
  }

  return apiRequest<TerminologyConcept[]>(
    `/terminology/diagnoses/search?${params.toString()}`,
    {},
    accessToken,
  )
}
