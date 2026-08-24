import type { ClinicalDocument } from '../../../api/clinicalDocuments'

import type {
  NursingIntakeFormState,
} from './types'


export interface NursingIntakePayload
  extends Record<string, unknown> {
  presenting_complaint: string | null
  history_of_presenting_complaint: string | null

  known_allergies: string[]

  allergy_notes: string | null

  past_medical_history: string | null

  current_medications: string[]

  surgical_history: string | null

  general_appearance: string | null
  level_of_consciousness: string | null
  mobility_status: string | null

  pain_score: number | null
  pain_location: string | null

  fall_risk: string | null
  pressure_injury_risk: string | null
  infection_precautions: string | null

  nursing_observations: string | null
  immediate_concerns: string | null
  handover_notes: string | null
}


export function intakeToPayload(
  intake: NursingIntakeFormState,
): NursingIntakePayload {
  return {
    presenting_complaint:
      intake.presenting_complaint ||
      null,

    history_of_presenting_complaint:
      intake
        .history_of_presenting_complaint ||
      null,

    known_allergies:
      intake.known_allergies
        .split(',')
        .map(
          value =>
            value.trim(),
        )
        .filter(Boolean),

    allergy_notes:
      intake.allergy_notes ||
      null,

    past_medical_history:
      intake.past_medical_history ||
      null,

    current_medications:
      intake.current_medications
        .split(',')
        .map(
          value =>
            value.trim(),
        )
        .filter(Boolean),

    surgical_history:
      intake.surgical_history ||
      null,

    general_appearance:
      intake.general_appearance ||
      null,

    level_of_consciousness:
      intake.level_of_consciousness ||
      null,

    mobility_status:
      intake.mobility_status ||
      null,

    pain_score:
      intake.pain_score
        ? Number(
            intake.pain_score,
          )
        : null,

    pain_location:
      intake.pain_location ||
      null,

    fall_risk:
      intake.fall_risk ||
      null,

    pressure_injury_risk:
      intake.pressure_injury_risk ||
      null,

    infection_precautions:
      intake.infection_precautions ||
      null,

    nursing_observations:
      intake.nursing_observations ||
      null,

    immediate_concerns:
      intake.immediate_concerns ||
      null,

    handover_notes:
      intake.handover_notes ||
      null,
  }
}


export function documentToIntake(
  document: ClinicalDocument,
): NursingIntakeFormState {
  const content =
    document.content

  return {
    presenting_complaint:
      String(
        content.presenting_complaint ??
          '',
      ),

    history_of_presenting_complaint:
      String(
        content
          .history_of_presenting_complaint ??
          '',
      ),

    known_allergies:
      Array.isArray(
        content.known_allergies,
      )
        ? content.known_allergies.join(
            ', ',
          )
        : '',

    allergy_notes:
      String(
        content.allergy_notes ??
          '',
      ),

    past_medical_history:
      String(
        content.past_medical_history ??
          '',
      ),

    current_medications:
      Array.isArray(
        content.current_medications,
      )
        ? content.current_medications.join(
            ', ',
          )
        : '',

    surgical_history:
      String(
        content.surgical_history ??
          '',
      ),

    general_appearance:
      String(
        content.general_appearance ??
          '',
      ),

    level_of_consciousness:
      String(
        content.level_of_consciousness ??
          '',
      ),

    mobility_status:
      String(
        content.mobility_status ??
          '',
      ),

    pain_score:
      content.pain_score === null ||
      content.pain_score === undefined
        ? ''
        : String(
            content.pain_score,
          ),

    pain_location:
      String(
        content.pain_location ??
          '',
      ),

    fall_risk:
      String(
        content.fall_risk ??
          '',
      ),

    pressure_injury_risk:
      String(
        content.pressure_injury_risk ??
          '',
      ),

    infection_precautions:
      String(
        content.infection_precautions ??
          '',
      ),

    nursing_observations:
      String(
        content.nursing_observations ??
          '',
      ),

    immediate_concerns:
      String(
        content.immediate_concerns ??
          '',
      ),

    handover_notes:
      String(
        content.handover_notes ??
          '',
      ),
  }
}
