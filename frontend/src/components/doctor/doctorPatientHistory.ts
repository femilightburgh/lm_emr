import {
  listPatientEpisodes,
  type Episode,
} from '../../api/episodes'

import {
  listEncounterClinicalDocuments,
  type ClinicalDocument,
} from '../../api/clinicalDocuments'

import {
  listEpisodeDiagnoses,
  type ClinicalDiagnosis,
} from '../../api/diagnoses'

import {
  listEncounterClinicalOrders,
  type ClinicalOrder,
} from '../../api/clinicalOrders'

import {
  getEncounterTimeline,
  type ClinicalEvent,
  type Encounter,
} from '../../api/encounters'

import {
  listEncounterVitals,
  type Vitals,
} from '../../api/vitals'

export interface HistoricalEncounterContext {
  encounter: Encounter
  documents: ClinicalDocument[]
  diagnoses: ClinicalDiagnosis[]
  orders: ClinicalOrder[]
  vitals: Vitals[]
  timeline: ClinicalEvent[]
}

export async function loadPatientHistory(
  accessToken: string,
  patientId: string,
): Promise<Episode[]> {
  return listPatientEpisodes(
    accessToken,
    patientId,
  )
}

export async function loadHistoricalEncounterContext(
  accessToken: string,
  encounter: Encounter,
): Promise<HistoricalEncounterContext> {
  const [
    documents,
    diagnoses,
    orders,
    vitals,
    timeline,
  ] = await Promise.all([
    listEncounterClinicalDocuments(
      accessToken,
      encounter.id,
    ),
    listEpisodeDiagnoses(
      accessToken,
      encounter.episode_id,
    ),
    listEncounterClinicalOrders(
      accessToken,
      encounter.id,
    ),
    listEncounterVitals(
      accessToken,
      encounter.id,
    ),
    getEncounterTimeline(
      accessToken,
      encounter.id,
    ),
  ])

  return {
    encounter,
    documents,
    diagnoses,
    orders,
    vitals,
    timeline,
  }
}
