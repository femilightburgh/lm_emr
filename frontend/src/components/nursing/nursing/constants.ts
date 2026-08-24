import type {
  NursingIntakeFormState,
  VitalsFormState,
} from './types'


export const INITIAL_INTAKE_FORM:
  NursingIntakeFormState = {
    presenting_complaint: '',
    history_of_presenting_complaint: '',
    known_allergies: '',
    allergy_notes: '',
    past_medical_history: '',
    current_medications: '',
    surgical_history: '',
    general_appearance: '',
    level_of_consciousness: '',
    mobility_status: '',
    pain_score: '',
    pain_location: '',
    fall_risk: '',
    pressure_injury_risk: '',
    infection_precautions: '',
    nursing_observations: '',
    immediate_concerns: '',
    handover_notes: '',
  }


export const INITIAL_VITALS_FORM:
  VitalsFormState = {
    temperature: '',
    heart_rate: '',
    respiratory_rate: '',
    systolic_bp: '',
    diastolic_bp: '',
    spo2: '',
    weight: '',
  }
