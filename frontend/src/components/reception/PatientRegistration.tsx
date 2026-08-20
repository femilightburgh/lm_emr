import type { FormEvent } from 'react'

import type {
  CreatePatientRequest,
  Patient,
} from '../../types'


interface Props {
  patientForm: CreatePatientRequest
  registrationLoading: boolean
  registrationError: string | null
  registrationSuccess: Patient | null
  onChange: (
    field: keyof CreatePatientRequest,
    value: string | null,
  ) => void
  onSubmit: (event: FormEvent) => void
  onRegisterAnother: () => void
  onViewPatients: () => void
  onDashboard: () => void
}


export default function PatientRegistration({
  patientForm,
  registrationLoading,
  registrationError,
  registrationSuccess,
  onChange,
  onSubmit,
  onRegisterAnother,
  onViewPatients,
  onDashboard,
}: Props) {
  return (
    <section className="workspace-content">

      {registrationSuccess ? (
        <div className="registration-success">

          <div className="success-mark">
            ✓
          </div>

          <p className="eyebrow">
            PATIENT REGISTERED
          </p>

          <h2>
            {registrationSuccess.first_name}{' '}
            {registrationSuccess.last_name}
          </h2>

          <p>
            The patient has been registered
            successfully.
          </p>

          <div className="registration-number">
            <span>
              Hospital number
            </span>

            <strong>
              {registrationSuccess.hospital_number}
            </strong>
          </div>

          <div className="registration-actions">

            <button
              type="button"
              className="secondary-button"
              onClick={onRegisterAnother}
            >
              Register another
            </button>

            <button
              type="button"
              className="primary-button"
              onClick={onViewPatients}
            >
              View patients
            </button>

          </div>

        </div>
      ) : (
        <form
          className="registration-form"
          onSubmit={onSubmit}
        >

          <div className="form-section">

            <div className="form-section-heading">
              <p className="eyebrow">
                IDENTIFICATION
              </p>

              <h2>
                Patient information
              </h2>

              <p>
                Enter the patient's hospital
                identification and demographic
                information.
              </p>
            </div>

            <div className="form-grid">

              <label>
                Hospital number
                <input
                  value={patientForm.hospital_number}
                  onChange={event =>
                    onChange(
                      'hospital_number',
                      event.target.value,
                    )
                  }
                  required
                />
              </label>

              <label>
                First name
                <input
                  value={patientForm.first_name}
                  onChange={event =>
                    onChange(
                      'first_name',
                      event.target.value,
                    )
                  }
                  required
                />
              </label>

              <label>
                Last name
                <input
                  value={patientForm.last_name}
                  onChange={event =>
                    onChange(
                      'last_name',
                      event.target.value,
                    )
                  }
                  required
                />
              </label>

              <label>
                Middle name
                <input
                  value={patientForm.middle_name ?? ''}
                  onChange={event =>
                    onChange(
                      'middle_name',
                      event.target.value,
                    )
                  }
                />
              </label>

              <label>
                Sex
                <select
                  value={patientForm.sex}
                  onChange={event =>
                    onChange(
                      'sex',
                      event.target.value,
                    )
                  }
                  required
                >
                  <option value="Male">
                    Male
                  </option>

                  <option value="Female">
                    Female
                  </option>
                </select>
              </label>

              <label>
                Date of birth
                <input
                  type="date"
                  value={patientForm.date_of_birth}
                  onChange={event =>
                    onChange(
                      'date_of_birth',
                      event.target.value,
                    )
                  }
                  required
                />
              </label>

            </div>

          </div>


          <div className="form-section">

            <div className="form-section-heading">
              <p className="eyebrow">
                CONTACT
              </p>

              <h2>
                Contact information
              </h2>
            </div>

            <div className="form-grid">

              <label>
                Phone number
                <input
                  type="tel"
                  value={
                    patientForm.phone_number ?? ''
                  }
                  onChange={event =>
                    onChange(
                      'phone_number',
                      event.target.value,
                    )
                  }
                />
              </label>

              <label>
                Email
                <input
                  type="email"
                  value={
                    patientForm.email ?? ''
                  }
                  onChange={event =>
                    onChange(
                      'email',
                      event.target.value,
                    )
                  }
                />
              </label>

              <label className="wide-field">
                Address
                <input
                  value={
                    patientForm.address ?? ''
                  }
                  onChange={event =>
                    onChange(
                      'address',
                      event.target.value,
                    )
                  }
                />
              </label>

              <label>
                Occupation
                <input
                  value={
                    patientForm.occupation ?? ''
                  }
                  onChange={event =>
                    onChange(
                      'occupation',
                      event.target.value,
                    )
                  }
                />
              </label>

              <label>
                Marital status
                <select
                  value={
                    patientForm.marital_status ?? ''
                  }
                  onChange={event =>
                    onChange(
                      'marital_status',
                      event.target.value || null,
                    )
                  }
                >
                  <option value="">
                    Not specified
                  </option>

                  <option value="Single">
                    Single
                  </option>

                  <option value="Married">
                    Married
                  </option>

                  <option value="Divorced">
                    Divorced
                  </option>

                  <option value="Widowed">
                    Widowed
                  </option>

                  <option value="Separated">
                    Separated
                  </option>
                </select>
              </label>

              <label>
                Religion
                <input
                  value={
                    patientForm.religion ?? ''
                  }
                  onChange={event =>
                    onChange(
                      'religion',
                      event.target.value,
                    )
                  }
                />
              </label>

            </div>

          </div>


          <div className="form-section">

            <div className="form-section-heading">
              <p className="eyebrow">
                HEALTH INFORMATION
              </p>

              <h2>
                Clinical demographics
              </h2>
            </div>

            <div className="form-grid">

              <label>
                Blood group
                <select
                  value={
                    patientForm.blood_group ?? ''
                  }
                  onChange={event =>
                    onChange(
                      'blood_group',
                      event.target.value || null,
                    )
                  }
                >
                  <option value="">
                    Not specified
                  </option>

                  <option value="A+">A+</option>
                  <option value="A-">A-</option>
                  <option value="B+">B+</option>
                  <option value="B-">B-</option>
                  <option value="AB+">AB+</option>
                  <option value="AB-">AB-</option>
                  <option value="O+">O+</option>
                  <option value="O-">O-</option>

                  <option value="Unknown">
                    Unknown
                  </option>
                </select>
              </label>

              <label>
                Genotype
                <select
                  value={
                    patientForm.genotype ?? ''
                  }
                  onChange={event =>
                    onChange(
                      'genotype',
                      event.target.value || null,
                    )
                  }
                >
                  <option value="">
                    Not specified
                  </option>

                  <option value="AA">
                    AA
                  </option>

                  <option value="AS">
                    AS
                  </option>

                  <option value="AC">
                    AC
                  </option>

                  <option value="SS">
                    SS
                  </option>

                  <option value="SC">
                    SC
                  </option>

                  <option value="CC">
                    CC
                  </option>

                  <option value="Unknown">
                    Unknown
                  </option>
                </select>
              </label>

            </div>

          </div>


          <div className="form-section">

            <div className="form-section-heading">
              <p className="eyebrow">
                NEXT OF KIN
              </p>

              <h2>
                Emergency contact
              </h2>
            </div>

            <div className="form-grid">

              <label>
                Name
                <input
                  value={
                    patientForm.next_of_kin_name ?? ''
                  }
                  onChange={event =>
                    onChange(
                      'next_of_kin_name',
                      event.target.value,
                    )
                  }
                />
              </label>

              <label>
                Relationship
                <select
                  value={
                    patientForm.next_of_kin_relationship ?? ''
                  }
                  onChange={event =>
                    onChange(
                      'next_of_kin_relationship',
                      event.target.value || null,
                    )
                  }
                >
                  <option value="">
                    Not specified
                  </option>

                  <option value="Spouse">
                    Spouse
                  </option>

                  <option value="Father">
                    Father
                  </option>

                  <option value="Mother">
                    Mother
                  </option>

                  <option value="Son">
                    Son
                  </option>

                  <option value="Daughter">
                    Daughter
                  </option>

                  <option value="Brother">
                    Brother
                  </option>

                  <option value="Sister">
                    Sister
                  </option>

                  <option value="Uncle">
                    Uncle
                  </option>

                  <option value="Aunt">
                    Aunt
                  </option>

                  <option value="Grandparent">
                    Grandparent
                  </option>

                  <option value="Grandchild">
                    Grandchild
                  </option>

                  <option value="Friend">
                    Friend
                  </option>

                  <option value="Employer">
                    Employer
                  </option>

                  <option value="Guardian">
                    Guardian
                  </option>

                  <option value="Other">
                    Other
                  </option>
                </select>
              </label>

              <label>
                Phone number
                <input
                  type="tel"
                  value={
                    patientForm.next_of_kin_phone ?? ''
                  }
                  onChange={event =>
                    onChange(
                      'next_of_kin_phone',
                      event.target.value,
                    )
                  }
                />
              </label>

              <label>
                Address
                <input
                  value={
                    patientForm.next_of_kin_address ?? ''
                  }
                  onChange={event =>
                    onChange(
                      'next_of_kin_address',
                      event.target.value,
                    )
                  }
                />
              </label>

            </div>

          </div>


          {registrationError && (
            <div className="login-error">
              {registrationError}
            </div>
          )}


          <div className="form-actions">

            <button
              type="button"
              className="secondary-button"
              onClick={onDashboard}
            >
              Cancel
            </button>

            <button
              type="submit"
              className="primary-button"
              disabled={registrationLoading}
            >
              {registrationLoading
                ? 'Registering...'
                : 'Register patient'}
            </button>

          </div>

        </form>
      )}

    </section>
  )
}