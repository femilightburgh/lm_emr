import {
  getEncounter,
  getEncounterTimeline,
  type Encounter,
} from '../../api/encounters'

import {
  listEpisodeDiagnoses,
  type ClinicalDiagnosis,
} from '../../api/diagnoses'

import {
  listEpisodeClinicalOrders,
  type ClinicalOrder,
} from '../../api/clinicalOrders'

import {
  listEncounterVitals,
  type Vitals,
} from '../../api/vitals'

import {
  listOrderClinicalResults,
  type ClinicalResult,
} from '../../api/clinicalResults'

import {
  downloadDiagnosticAttachment,
  getDiagnosticReportByOrder,
  listDiagnosticAttachments,
  type DiagnosticReport,
  type DiagnosticReportAttachment,
} from '../../api/diagnostics'

export interface DoctorDiagnosticAttachment
  extends DiagnosticReportAttachment {
  url: string
}

export interface DoctorEncounterContext {
  encounter: Encounter
  diagnoses: ClinicalDiagnosis[]
  timeline: Awaited<
    ReturnType<typeof getEncounterTimeline>
  >
  orders: ClinicalOrder[]
  vitals: Vitals[]
  clinicalResults: ClinicalResult[]
  diagnosticReports: DiagnosticReport[]
  diagnosticAttachments: Record<
    string,
    DoctorDiagnosticAttachment[]
  >
}

export async function loadDoctorEncounterContext(
  accessToken: string,
  encounterId: string,
): Promise<DoctorEncounterContext> {
  const encounter =
    await getEncounter(
      accessToken,
      encounterId,
    )

  const [
    diagnoses,
    timeline,
    orders,
    vitals,
  ] = await Promise.all([
    listEpisodeDiagnoses(
      accessToken,
      encounter.episode_id,
    ),
    getEncounterTimeline(
      accessToken,
      encounterId,
    ),
    listEpisodeClinicalOrders(
      accessToken,
      encounter.episode_id,
    ),
    listEncounterVitals(
      accessToken,
      encounterId,
    ),
  ])

  const clinicalResultOrders =
    orders.filter(
      order =>
        order.order_type === 'LABORATORY' ||
        order.order_type === 'RADIOLOGY',
    )

  const diagnosticOrders =
    orders.filter(
      order =>
        order.order_type === 'DIAGNOSTIC',
    )

  const resultGroups =
    await Promise.all(
      clinicalResultOrders.map(
        order =>
          listOrderClinicalResults(
            accessToken,
            order.id,
          ),
      ),
    )

  const diagnosticReportGroups =
    await Promise.all(
      diagnosticOrders.map(
        async order => {
          try {
            return await getDiagnosticReportByOrder(
              accessToken,
              order.id,
            )
          } catch {
            return null
          }
        },
      ),
    )

  const clinicalResults =
    resultGroups.flat()

  const diagnosticReports =
    diagnosticReportGroups.filter(
      (
        report,
      ): report is DiagnosticReport =>
        report !== null &&
        report.status === 'FINAL',
    )

  const attachmentEntries =
    await Promise.all(
      diagnosticReports.map(
        async report => {
          try {
            const attachments =
              await listDiagnosticAttachments(
                accessToken,
                report.id,
              )

            const hydratedAttachments =
              await Promise.all(
                attachments.map(
                  async attachment => {
                    const blob =
                      await downloadDiagnosticAttachment(
                        accessToken,
                        attachment.id,
                      )

                    return {
                      ...attachment,
                      url: URL.createObjectURL(
                        blob,
                      ),
                    }
                  },
                ),
              )

            return [
              report.id,
              hydratedAttachments,
            ] as const
          } catch {
            return [
              report.id,
              [],
            ] as const
          }
        },
      ),
    )

  return {
    encounter,
    diagnoses,
    timeline,
    orders,
    vitals,
    clinicalResults,
    diagnosticReports,
    diagnosticAttachments:
      Object.fromEntries(
        attachmentEntries,
      ),
  }
}
