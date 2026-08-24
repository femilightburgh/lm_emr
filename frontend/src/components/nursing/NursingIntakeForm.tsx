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


interface Props {
  intake: NursingIntakeFormState
  disabled: boolean
  saving: boolean
  status: string

  onChange: (
    field: keyof NursingIntakeFormState,
    value: string,
  ) => void

  onSave: () => void
  onSign: () => void
}


function Field({
  label,
  value,
  onChange,
  disabled,
  placeholder,
  textarea = false,
  full = false,
  type = 'text',
  min,
  max,
}: {
  label: string
  value: string
  onChange: (
    value: string,
  ) => void
  disabled: boolean
  placeholder?: string
  textarea?: boolean
  full?: boolean
  type?: string
  min?: string
  max?: string
}) {
  return (
    <label
      className={
        full
          ? 'nursing-intake-field nursing-intake-field-full'
          : 'nursing-intake-field'
      }
    >
      <span>
        {label}
      </span>

      {textarea ? (
        <textarea
          value={value}
          placeholder={placeholder}
          onChange={event =>
            onChange(
              event.target.value,
            )
          }
          disabled={disabled}
          rows={4}
        />
      ) : (
        <input
          type={type}
          min={min}
          max={max}
          value={value}
          placeholder={placeholder}
          onChange={event =>
            onChange(
              event.target.value,
            )
          }
          disabled={disabled}
        />
      )}
    </label>
  )
}


function Section({
  eyebrow,
  title,
  children,
}: {
  eyebrow: string
  title: string
  children: React.ReactNode
}) {
  return (
    <div className="nursing-intake-group">

      <div className="nursing-intake-group-heading">

        <p className="eyebrow">
          {eyebrow}
        </p>

        <h4>
          {title}
        </h4>

      </div>

      <div className="nursing-intake-grid">
        {children}
      </div>

    </div>
  )
}


function DisplayField({
  label,
  value,
}: {
  label: string
  value: string
}) {
  return (
    <div className="nursing-signed-field">

      <span>
        {label}
      </span>

      <strong>
        {value.trim()
          ? value
          : '—'}
      </strong>

    </div>
  )
}


export default function NursingIntakeForm({
  intake,
  disabled,
  saving,
  status,
  onChange,
  onSave,
  onSign,
}: Props) {
  const signed =
    status === 'SIGNED'


  // ==========================================================================
  // Signed Nursing Intake
  // ==========================================================================

  if (signed) {
    return (
      <section className="nursing-section nursing-intake">

        <div className="nursing-section-heading">

          <div>
            <p className="eyebrow">
              NURSING DOCUMENT
            </p>

            <h3>
              Signed nursing intake
            </h3>

            <p>
              Completed nursing assessment.
            </p>
          </div>

          <span className="nursing-signed-badge">
            SIGNED
          </span>

        </div>


        <div className="nursing-signed-document">

          <div className="nursing-signed-document-header">
            <strong>
              Nursing assessment
            </strong>

            <span className="nursing-signed-badge">
              Read-only
            </span>
          </div>


          <div className="nursing-signed-document-body">

            <div className="nursing-signed-group">

              <p className="eyebrow">
                PRESENTING PROBLEM
              </p>

              <div className="nursing-signed-grid">

                <DisplayField
                  label="Presenting complaint"
                  value={
                    intake.presenting_complaint
                  }
                />

                <DisplayField
                  label="History of presenting complaint"
                  value={
                    intake
                      .history_of_presenting_complaint
                  }
                />

              </div>

            </div>


            <div className="nursing-signed-group">

              <p className="eyebrow">
                MEDICAL BACKGROUND
              </p>

              <div className="nursing-signed-grid">

                <DisplayField
                  label="Known allergies"
                  value={
                    intake.known_allergies
                  }
                />

                <DisplayField
                  label="Allergy notes"
                  value={
                    intake.allergy_notes
                  }
                />

                <DisplayField
                  label="Past medical history"
                  value={
                    intake.past_medical_history
                  }
                />

                <DisplayField
                  label="Current medications"
                  value={
                    intake.current_medications
                  }
                />

                <DisplayField
                  label="Surgical history"
                  value={
                    intake.surgical_history
                  }
                />

              </div>

            </div>


            <div className="nursing-signed-group">

              <p className="eyebrow">
                CLINICAL ASSESSMENT
              </p>

              <div className="nursing-signed-grid">

                <DisplayField
                  label="General appearance"
                  value={
                    intake.general_appearance
                  }
                />

                <DisplayField
                  label="Level of consciousness"
                  value={
                    intake.level_of_consciousness
                  }
                />

                <DisplayField
                  label="Mobility status"
                  value={
                    intake.mobility_status
                  }
                />

                <DisplayField
                  label="Pain score"
                  value={
                    intake.pain_score
                  }
                />

                <DisplayField
                  label="Pain location"
                  value={
                    intake.pain_location
                  }
                />

              </div>

            </div>


            <div className="nursing-signed-group">

              <p className="eyebrow">
                RISK &amp; SAFETY
              </p>

              <div className="nursing-signed-grid">

                <DisplayField
                  label="Fall risk"
                  value={
                    intake.fall_risk
                  }
                />

                <DisplayField
                  label="Pressure injury risk"
                  value={
                    intake
                      .pressure_injury_risk
                  }
                />

                <DisplayField
                  label="Infection precautions"
                  value={
                    intake
                      .infection_precautions
                  }
                />

              </div>

            </div>


            <div className="nursing-signed-group">

              <p className="eyebrow">
                NURSING OBSERVATIONS
              </p>

              <div className="nursing-signed-grid">

                <DisplayField
                  label="Nursing observations"
                  value={
                    intake
                      .nursing_observations
                  }
                />

                <DisplayField
                  label="Immediate concerns"
                  value={
                    intake
                      .immediate_concerns
                  }
                />

              </div>

            </div>


            <div className="nursing-signed-group">

              <p className="eyebrow">
                HANDOVER
              </p>

              <div className="nursing-signed-grid">

                <DisplayField
                  label="Handover notes"
                  value={
                    intake.handover_notes
                  }
                />

              </div>

            </div>

          </div>

        </div>

        <div className="nursing-signed-note">
          This nursing intake has been signed
          and is now read-only.
        </div>

      </section>
    )
  }


  // ==========================================================================
  // Draft Nursing Intake
  // ==========================================================================

  return (
    <section className="nursing-section nursing-intake">

      <div className="nursing-section-heading">

        <div>
          <p className="eyebrow">
            NURSING DOCUMENT
          </p>

          <h3>
            Nursing intake
          </h3>

          <p>
            Complete the nursing assessment
            before routing the patient.
          </p>
        </div>

        <span className="nursing-document-status">
          {status}
        </span>

      </div>


      <Section
        eyebrow="PRESENTING PROBLEM"
        title="Reason for visit"
      >

        <Field
          label="Presenting complaint"
          value={
            intake.presenting_complaint
          }
          onChange={value =>
            onChange(
              'presenting_complaint',
              value,
            )
          }
          disabled={disabled}
          full
          textarea
          placeholder="Describe the main reason for the patient's visit."
        />


        <Field
          label="History of presenting complaint"
          value={
            intake
              .history_of_presenting_complaint
          }
          onChange={value =>
            onChange(
              'history_of_presenting_complaint',
              value,
            )
          }
          disabled={disabled}
          full
          textarea
          placeholder="Document the relevant history."
        />

      </Section>


      <Section
        eyebrow="MEDICAL BACKGROUND"
        title="History, allergies & medications"
      >

        <Field
          label="Known allergies"
          value={
            intake.known_allergies
          }
          onChange={value =>
            onChange(
              'known_allergies',
              value,
            )
          }
          disabled={disabled}
          placeholder="e.g. Penicillin"
        />


        <Field
          label="Allergy notes"
          value={
            intake.allergy_notes
          }
          onChange={value =>
            onChange(
              'allergy_notes',
              value,
            )
          }
          disabled={disabled}
          placeholder="Additional allergy details"
        />


        <Field
          label="Past medical history"
          value={
            intake.past_medical_history
          }
          onChange={value =>
            onChange(
              'past_medical_history',
              value,
            )
          }
          disabled={disabled}
          full
          textarea
          placeholder="Relevant medical history"
        />


        <Field
          label="Current medications"
          value={
            intake.current_medications
          }
          onChange={value =>
            onChange(
              'current_medications',
              value,
            )
          }
          disabled={disabled}
          full
          textarea
          placeholder="Separate multiple medications with commas"
        />


        <Field
          label="Surgical history"
          value={
            intake.surgical_history
          }
          onChange={value =>
            onChange(
              'surgical_history',
              value,
            )
          }
          disabled={disabled}
          full
          textarea
          placeholder="Relevant previous procedures or surgery"
        />

      </Section>


      <Section
        eyebrow="CLINICAL ASSESSMENT"
        title="Current nursing assessment"
      >

        <Field
          label="General appearance"
          value={
            intake.general_appearance
          }
          onChange={value =>
            onChange(
              'general_appearance',
              value,
            )
          }
          disabled={disabled}
          textarea
          placeholder="General appearance and condition"
        />


        <Field
          label="Level of consciousness"
          value={
            intake.level_of_consciousness
          }
          onChange={value =>
            onChange(
              'level_of_consciousness',
              value,
            )
          }
          disabled={disabled}
          placeholder="e.g. Alert, drowsy"
        />


        <Field
          label="Mobility status"
          value={
            intake.mobility_status
          }
          onChange={value =>
            onChange(
              'mobility_status',
              value,
            )
          }
          disabled={disabled}
          placeholder="e.g. Independent"
        />


        <Field
          label="Pain score"
          value={
            intake.pain_score
          }
          onChange={value =>
            onChange(
              'pain_score',
              value,
            )
          }
          disabled={disabled}
          type="number"
          min="0"
          max="10"
          placeholder="0–10"
        />


        <Field
          label="Pain location"
          value={
            intake.pain_location
          }
          onChange={value =>
            onChange(
              'pain_location',
              value,
            )
          }
          disabled={disabled}
          placeholder="e.g. Chest"
        />

      </Section>


      <Section
        eyebrow="RISK & SAFETY"
        title="Patient safety"
      >

        <Field
          label="Fall risk"
          value={
            intake.fall_risk
          }
          onChange={value =>
            onChange(
              'fall_risk',
              value,
            )
          }
          disabled={disabled}
          placeholder="e.g. Low / Moderate / High"
        />


        <Field
          label="Pressure injury risk"
          value={
            intake.pressure_injury_risk
          }
          onChange={value =>
            onChange(
              'pressure_injury_risk',
              value,
            )
          }
          disabled={disabled}
          placeholder="e.g. Low / Moderate / High"
        />


        <Field
          label="Infection precautions"
          value={
            intake.infection_precautions
          }
          onChange={value =>
            onChange(
              'infection_precautions',
              value,
            )
          }
          disabled={disabled}
          full
          textarea
          placeholder="Precautions currently required"
        />

      </Section>


      <Section
        eyebrow="NURSING OBSERVATIONS"
        title="Observations & concerns"
      >

        <Field
          label="Nursing observations"
          value={
            intake.nursing_observations
          }
          onChange={value =>
            onChange(
              'nursing_observations',
              value,
            )
          }
          disabled={disabled}
          full
          textarea
          placeholder="Record relevant nursing observations."
        />


        <Field
          label="Immediate concerns"
          value={
            intake.immediate_concerns
          }
          onChange={value =>
            onChange(
              'immediate_concerns',
              value,
            )
          }
          disabled={disabled}
          full
          textarea
          placeholder="Document issues requiring immediate attention."
        />

      </Section>


      <Section
        eyebrow="HANDOVER"
        title="Handover to the receiving team"
      >

        <Field
          label="Handover notes"
          value={
            intake.handover_notes
          }
          onChange={value =>
            onChange(
              'handover_notes',
              value,
            )
          }
          disabled={disabled}
          full
          textarea
          placeholder="What should the receiving clinical team know?"
        />

      </Section>


      <div className="nursing-intake-actions">

        <div>
          <span className="nursing-document-status">
            {status}
          </span>

          <p>
            Save the assessment as a draft while
            you work. Signing makes it read-only.
          </p>
        </div>


        <div className="nursing-intake-action-buttons">

          <button
            type="button"
            className="secondary-button"
            onClick={onSave}
            disabled={
              disabled ||
              saving
            }
          >
            {saving
              ? 'Saving...'
              : 'Save draft'}
          </button>


          <button
            type="button"
            className="primary-button"
            onClick={onSign}
            disabled={
              disabled ||
              saving
            }
          >
            Sign nursing intake
          </button>

        </div>

      </div>

    </section>
  )
}
