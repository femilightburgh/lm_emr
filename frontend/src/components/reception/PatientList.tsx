import type { FormEvent } from 'react'

import type { Patient } from '../../types'


interface Props {
  patients: Patient[]
  searchQuery: string
  patientLoading: boolean
  patientError: string | null
  onSearchQueryChange: (value: string) => void
  onSearch: (event: FormEvent) => void
  onRegisterPatient: () => void
  onSelectPatient: (patient: Patient) => void
}


export default function PatientList({
  patients,
  searchQuery,
  patientLoading,
  patientError,
  onSearchQueryChange,
  onSearch,
  onRegisterPatient,
  onSelectPatient,
}: Props) {
  return (
    <>
      <div className="section-toolbar">

        <form
          className="patient-search"
          onSubmit={onSearch}
        >
          <input
            type="search"
            value={searchQuery}
            onChange={event =>
              onSearchQueryChange(
                event.target.value,
              )
            }
            placeholder="Search patients by name"
          />

          <button
            type="submit"
            className="secondary-button"
            disabled={patientLoading}
          >
            {patientLoading
              ? 'Searching...'
              : 'Search'}
          </button>

        </form>

        <button
          type="button"
          className="primary-button"
          onClick={onRegisterPatient}
        >
          Register patient
        </button>

      </div>


      {patientError && (
        <div className="login-error">
          {patientError}
        </div>
      )}


      {patientLoading && (
        <div className="empty-state">
          Loading patients...
        </div>
      )}


      {!patientLoading &&
        patients.length === 0 && (
        <div className="empty-state">
          <strong>
            No patients found.
          </strong>

          <span>
            Search again or register a new
            patient.
          </span>
        </div>
      )}


      {!patientLoading &&
        patients.length > 0 && (
        <div className="patient-table">

          <div className="patient-table-header">
            <span>Hospital number</span>
            <span>Patient</span>
            <span>Sex</span>
            <span>Date of birth</span>
            <span>Phone</span>
          </div>

          {patients.map(patient => (
            <button
              type="button"
              className="patient-row"
              key={patient.id}
              onClick={() =>
                onSelectPatient(patient)
              }
            >
              <span>
                <strong>
                  {patient.hospital_number}
                </strong>
              </span>

              <span>
                {patient.last_name},{' '}
                {patient.first_name}{' '}
                {patient.middle_name ?? ''}
              </span>

              <span>
                {patient.sex}
              </span>

              <span>
                {patient.date_of_birth}
              </span>

              <span>
                {patient.phone_number ?? '—'}
              </span>
            </button>
          ))}

        </div>
      )}
    </>
  )
}