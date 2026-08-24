export interface NursingIntakeFormState {
  presenting_complaint: string
  history_of_presenting_complaint: string
  known_allergies: string
  allergy_notes: string
  past_medical_history: string
  current_medications: string
  surgical_history: string
  general_appearance: string
  level_of_consciousness: string
  mobility_status: string
  pain_score: string
  pain_location: string
  fall_risk: string
  pressure_injury_risk: string
  infection_precautions: string
  nursing_observations: string
  immediate_concerns: string
  handover_notes: string
}


export interface VitalsFormState {
  temperature: string
  heart_rate: string
  respiratory_rate: string
  systolic_bp: string
  diastolic_bp: string
  spo2: string
  weight: string
}
