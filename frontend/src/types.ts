export interface LoginRequest {
  hospital_code: string
  email: string
  password: string
}

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: 'bearer'
}

export interface AuthenticatedUser {
  id: string
  email: string
  hospital_id: string
  is_superuser: boolean
  status: string
  roles: string[]
}

export interface Patient {
  id: string
  hospital_number: string
  first_name: string
  last_name: string
  middle_name: string | null
  sex: string
  date_of_birth: string
  phone_number: string | null
  email: string | null
  address: string | null
  occupation: string | null
  marital_status: string | null
  religion: string | null
  blood_group: string | null
  genotype: string | null
  next_of_kin_name: string | null
  next_of_kin_relationship: string | null
  next_of_kin_phone: string | null
  next_of_kin_address: string | null
}

export interface PatientListResponse {
  total: number
  items: Patient[]
}

export interface CreatePatientRequest {
  hospital_number: string
  first_name: string
  last_name: string
  middle_name?: string | null

  sex: 'Male' | 'Female'
  date_of_birth: string

  phone_number?: string | null
  email?: string | null
  address?: string | null
  occupation?: string | null

  marital_status?:
    | 'Single'
    | 'Married'
    | 'Divorced'
    | 'Widowed'
    | 'Separated'
    | null

  religion?: string | null

  blood_group?:
    | 'A+'
    | 'A-'
    | 'B+'
    | 'B-'
    | 'AB+'
    | 'AB-'
    | 'O+'
    | 'O-'
    | 'Unknown'
    | null

  genotype?:
    | 'AA'
    | 'AS'
    | 'AC'
    | 'SS'
    | 'SC'
    | 'CC'
    | 'Unknown'
    | null

  next_of_kin_name?: string | null

  next_of_kin_relationship?:
    | 'Spouse'
    | 'Father'
    | 'Mother'
    | 'Son'
    | 'Daughter'
    | 'Brother'
    | 'Sister'
    | 'Uncle'
    | 'Aunt'
    | 'Grandparent'
    | 'Grandchild'
    | 'Friend'
    | 'Employer'
    | 'Guardian'
    | 'Other'
    | null

  next_of_kin_phone?: string | null
  next_of_kin_address?: string | null
}